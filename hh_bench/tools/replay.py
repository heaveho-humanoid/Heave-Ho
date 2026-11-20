"""Replay an HH-Bench reference in Isaac Lab: robots, object and static scene follow the reference motion kinematically.

    python tools/replay.py --task 03b_table_4robots                      # GUI
    python tools/replay.py --task 06_DollyPlace --headless --video out.mp4
    python tools/replay.py --task 10_fire_hose --variant dex3

Requires Isaac Sim 5.0 + Isaac Lab 2.x (tested with isaaclab 0.44). No other code from us is needed.
The object pose is written from the reference every frame (it is NOT simulated), so this shows the task, not a policy.
The fire hose (10_fire_hose) is a physical articulation without a reference pose; it is not shown here."""
import argparse, json, os
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ap = argparse.ArgumentParser()
ap.add_argument("--task", required=True, help="task id, e.g. 03b_table_4robots (see manifest.json)")
ap.add_argument("--variant", default=None, help="10_fire_hose only: 'dex3' uses motion_dex3/ and the Dex3 hand")
ap.add_argument("--video", default=None, help="write an mp4 here (needs imageio[ffmpeg])")
ap.add_argument("--stride", type=int, default=2, help="render every n-th reference frame (50 fps data)")
ap.add_argument("--start", type=int, default=0); ap.add_argument("--end", type=int, default=None)
from isaaclab.app import AppLauncher
AppLauncher.add_app_launcher_args(ap)
args = ap.parse_args()
if args.video: args.enable_cameras = True
app = AppLauncher(args).app

import torch
import isaaclab.sim as sim_utils
from isaaclab.actuators import ImplicitActuatorCfg
from isaaclab.assets import Articulation, ArticulationCfg, RigidObject, RigidObjectCfg

task_dir = os.path.join(ROOT, "tasks", args.task); task = json.load(open(os.path.join(task_dir, "task.json")))
robot_type = task["robot_type"]; motion_dir = os.path.join(task_dir, "motion")
if args.variant == "dex3": robot_type, motion_dir = "g1_29dof_dex3-feet-complex", os.path.join(task_dir, "motion_dex3")
N = task["num_agents"]
D = [np.load(os.path.join(motion_dir, f"agent_{k}", "motion.npz")) for k in range(N)]
M = [json.load(open(os.path.join(motion_dir, f"agent_{k}", "meta.json"))) for k in range(N)]
bn = M[0]["body_names"]; T = len(D[0]["joint_pos"]); end = min(args.end or T, T)
dev = "cuda:0" if torch.cuda.is_available() else "cpu"
sim = sim_utils.SimulationContext(sim_utils.SimulationCfg(dt=1 / 50, device=dev))
sim_utils.GroundPlaneCfg().func("/World/ground", sim_utils.GroundPlaneCfg())
sim_utils.DomeLightCfg(intensity=2000.0).func("/World/light", sim_utils.DomeLightCfg(intensity=2000.0))
if os.path.exists(os.path.join(task_dir, "terrain.usd")):        # static walls, already in world coordinates
    sim_utils.UsdFileCfg(usd_path=os.path.join(task_dir, "terrain.usd")).func("/World/terrain", sim_utils.UsdFileCfg(usd_path=os.path.join(task_dir, "terrain.usd")))

robots = []
for k in range(N):
    cfg = ArticulationCfg(
        prim_path=f"/World/Robot_{k}",
        spawn=sim_utils.UrdfFileCfg(
            asset_path=os.path.join(ROOT, "robots", f"{robot_type}.urdf"), fix_base=False, merge_fixed_joints=True,
            replace_cylinders_with_capsules=True, self_collision=False,
            joint_drive=sim_utils.UrdfConverterCfg.JointDriveCfg(gains=sim_utils.UrdfConverterCfg.JointDriveCfg.PDGainsCfg(stiffness=0, damping=0), target_type="none"),
            rigid_props=sim_utils.RigidBodyPropertiesCfg(disable_gravity=True),
            collision_props=sim_utils.CollisionPropertiesCfg(collision_enabled=False)),
        actuators={"all": ImplicitActuatorCfg(joint_names_expr=[".*"], stiffness=0.0, damping=0.0)})
    robots.append(Articulation(cfg))


def kinematic(name, usd, scale):
    return RigidObject(RigidObjectCfg(prim_path=f"/World/{name}", spawn=sim_utils.UsdFileCfg(
        usd_path=os.path.join(ROOT, usd), scale=tuple(scale),
        rigid_props=sim_utils.RigidBodyPropertiesCfg(disable_gravity=True),
        collision_props=sim_utils.CollisionPropertiesCfg(collision_enabled=False))))


objs = []                                  # (rigid object, body index in motion.npz)
if task.get("object"):
    o = task["object"]; objs.append((kinematic("Object", o["usd"], o["scale"]), bn.index(o["body_name_in_motion"])))
for x in task.get("static_extras", []):
    objs.append((kinematic(x["name"], x["usd"], x["scale"]), bn.index(x["name"])))

cam = None
if args.video:
    from isaaclab.sensors import Camera, CameraCfg
    cam = Camera(CameraCfg(prim_path="/World/ReplayCam", update_period=0, height=540, width=960, data_types=["rgb"],
                           spawn=sim_utils.PinholeCameraCfg(focal_length=18.0, clipping_range=(0.05, 80.0))))
sim.reset()

t2 = lambda a: torch.tensor(np.asarray(a), dtype=torch.float32, device=dev)
perms = []
for r in robots:                           # reference joint order -> articulation joint order (missing joints held at 0)
    jn = M[0]["joint_names"]; perms.append([jn.index(n) if n in jn else -1 for n in r.joint_names])
print(f"[replay] {args.task}: {N} robots, {T} frames ({T / 50:.1f} s), robot {robot_type}, objects {[bn[i] for _, i in objs]}")

# camera: fixed viewing direction, follows the team centroid, distance scaled to the team extent
P0 = np.array([D[k]["body_pos_w"][0, 0] for k in range(N)]); ext = float(np.ptp(P0[:, :2], 0).max())
dv = np.array([0.4, -0.55, 0.9] if os.path.exists(os.path.join(task_dir, "terrain.usd")) else [0.55, -0.75, 0.38])   # look down over walls
eye_off = dv / np.linalg.norm(dv) * max(5.0, 1.5 * ext + 3.5); cam_c = None
def write_frame(t):
    for k, r in enumerate(robots):
        d = D[k]
        st = torch.cat([t2(d["body_pos_w"][t, 0]), t2(d["body_quat_w"][t, 0]), t2(d["body_lin_vel_w"][t, 0]), t2(d["body_ang_vel_w"][t, 0])])[None]
        r.write_root_state_to_sim(st)
        q = np.array([d["joint_pos"][t][i] if i >= 0 else 0.0 for i in perms[k]])
        r.write_joint_state_to_sim(t2(q)[None], torch.zeros_like(t2(q)[None]))
    for o, i in objs:
        so = torch.cat([t2(D[0]["body_pos_w"][t, i]), t2(D[0]["body_quat_w"][t, i]), torch.zeros(6, device=dev)])[None]
        o.write_root_state_to_sim(so); o.write_data_to_sim()
    for r in robots: r.write_data_to_sim()


def move_camera(t):
    global cam_c
    ctr = np.mean([D[k]["body_pos_w"][min(t + 30, T - 1), 0] for k in range(N)], 0); ctr[2] = 0.6
    cam_c = ctr if cam_c is None else 0.97 * cam_c + 0.03 * ctr
    cam.set_world_poses_from_view(t2(cam_c + eye_off)[None], t2(cam_c)[None])


frames = []
if cam is not None:                        # warm-up: scene at the first frame, camera in place, let the renderer converge
    write_frame(args.start); move_camera(args.start)
    for _ in range(15): sim.step(render=True)
for t in range(args.start, end):
    write_frame(t)
    rec = cam is not None and (t - args.start) % args.stride == 0
    if rec: move_camera(t)                 # camera placed before rendering this frame
    sim.step(render=(t - args.start) % args.stride == 0)
    for r in robots: r.update(sim.get_physics_dt())
    for o, _ in objs: o.update(sim.get_physics_dt())
    if not app.is_running(): break
    if rec:
        cam.update(0.0); frames.append(cam.data.output["rgb"][0].cpu().numpy()[..., :3].copy())
if args.video and frames:
    import imageio.v2 as iio
    iio.mimwrite(args.video, frames, fps=50 // args.stride, quality=7); print(f"[replay] wrote {args.video} ({len(frames)} frames)", flush=True)
os._exit(0)                                # app.close() can hang after headless rendering
