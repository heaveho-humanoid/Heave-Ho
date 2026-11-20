"""Load an HH-Bench task with numpy only and print what is in it.

    python tools/load_task.py --task 03b_table_4robots

motion/agent_<k>/motion.npz (one file per robot, 50 fps, T frames, B bodies, J joints):
    body_pos_w      [T, B, 3]  world positions (m). Bodies follow meta.json body_names: the robot links first
                               (index 0 = pelvis = root), then the object and any static scene bodies.
    body_quat_w     [T, B, 4]  world orientations, (w, x, y, z)
    body_lin_vel_w  [T, B, 3]  world linear velocities (m/s)
    body_ang_vel_w  [T, B, 3]  world angular velocities (rad/s)
    joint_pos       [T, J]     joint angles (rad), order = meta.json joint_names
    joint_vel       [T, J]     joint velocities (rad/s)
    object_contact  [T, 2]     1 while the left / right hand should be in contact with the object
The object and the static bodies are identical in every agent file. Object poses are the USD prim origin of the object
asset (with task.json "scale" applied), e.g. a corner for objects/suitcase/suitcase.usd."""
import argparse, json, os
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load_task(task_id, motion="motion"):
    d = os.path.join(ROOT, "tasks", task_id); task = json.load(open(os.path.join(d, "task.json")))
    agents = []
    for k in range(task["num_agents"]):
        a = os.path.join(d, motion, f"agent_{k}")
        agents.append(dict(np.load(os.path.join(a, "motion.npz")), meta=json.load(open(os.path.join(a, "meta.json")))))
    return task, agents


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--task", required=True); ap.add_argument("--motion", default="motion")
    args = ap.parse_args()
    task, agents = load_task(args.task, args.motion)
    m = agents[0]["meta"]; T = agents[0]["joint_pos"].shape[0]
    print(f"{task['id']}: {task['title']}")
    print(f"  robots {task['num_agents']} ({task['robot_type']}), {T} frames = {T / m['fps']:.1f} s at {m['fps']} fps")
    print(f"  joints {len(m['joint_names'])}, bodies {len(m['body_names'])}: ... {m['body_names'][-4:]}")
    o = task.get("object")
    if o:
        i = m["body_names"].index(o["body_name_in_motion"]); p = agents[0]["body_pos_w"][:, i]
        print(f"  object {o['name']} ({o['usd']}, scale {o['scale']}, mass {o['mass_kg']} kg = set it yourself)")
        print(f"    start {p[0].round(3)}  end {p[-1].round(3)}")
    for x in task.get("static_extras", []): print(f"  static {x['name']} ({x['usd']})")
    for k, a in enumerate(agents):
        print(f"  agent_{k}: pelvis start {a['body_pos_w'][0, 0].round(3)} end {a['body_pos_w'][-1, 0].round(3)}, "
              f"hands in contact {a['object_contact'].all(1).mean() * 100:.0f}% of the frames")
    if "composed_from_units" in task: print(f"  composed from skill units: {task['composed_from_units']['keys']}")
