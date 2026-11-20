# HH-Bench (preliminary release)

> [!IMPORTANT]
> This is a **preliminary release** of HH-Bench. The exact specifications we used in the paper (object masses, success
> criteria, evaluation protocol) will be organized and released later.
> Object masses are currently left unset (`mass_kg: null` in every `task.json`); set them according to your own requirements.

HH-Bench contains 12 multi-humanoid loco-manipulation tasks on the Unitree G1. Four of them come in several team sizes
(the object is scaled to the team), giving 18 task variants in total. For every variant we provide the reference motion
of each robot, the object and scene assets, and the task metadata. No policy weights are included.

## Tasks

| id | task | robots | length (s) | object | scene |
|---|---|---|---|---|---|
| `01_L_corridor` | L-shaped corridor | 2 | 100.9 | box 70 x 15.5 x 43 cm | walls (`terrain.usd`) |
| `02_narrow_door` | Narrow door | 2 | 89.4 | box 70 x 15.5 x 43 cm | wall with a 0.89 m door (`terrain.usd`) |
| `03a_table_2robots` | Table carry | 2 | 36.8 | table | flat |
| `03b_table_4robots` | Table carry | 4 | 36.8 | table (larger) | flat |
| `03c_table_10robots` | Table carry | 10 | 36.8 | long table | flat |
| `04a_sofa_2robots` | L-shaped sofa | 2 | 77.9 | L-sofa | flat |
| `04b_sofa_5robots` | L-shaped sofa | 5 | 51.1 | L-sofa 2.25 x 1.44 m | flat |
| `05_stair_carry` | Stair carry | 2 | 49.7 | box 70 x 15.5 x 43 cm | stairs |
| `06_DollyPlace` | Lift, carry and put the box on a dolly | 2 | 66.9 | box 70 x 15.5 x 43 cm | dolly, 20 cm high |
| `07_box_handover` | Box handover from a truck | 2 | 33.5 | box | truck bed, 0.975 m high |
| `08a_palanquin_2robots` | Palanquin | 2 | 21.8 | palanquin | flat |
| `08b_palanquin_4robots` | Palanquin | 4 | 21.8 | palanquin (4 poles) | flat |
| `09a_rebar_2robots` | Rebar / beam shoulder carry | 2 | 23.8 | beam 2.8 m | sawhorses |
| `09b_rebar_3robots` | Rebar / beam shoulder carry | 3 | 23.8 | beam 4.1 m | sawhorses |
| `10_fire_hose` | Fire hose (rubber hand / Dex3 hand) | 2 | 28.0 | physical 9.4 m hose | hydrant, stands |
| `11_box_push` | Box push | 2 | 15.8 | large box | flat |
| `12_millstone` | Millstone | 2 | 37.1 | millstone (revolute joint) | millstone base |

`10_fire_hose` has two variants: `motion/` (rubber hand) and `motion_dex3/` (Dex3 hand).

**How we use these tasks in the paper.** Heave-Ho does not train per task or per trajectory. In our setting, a single
general policy is trained for interacting with each object, and it can follow arbitrary trajectories with that object
(e.g. carrying a box, table or sofa along any path, turning, stepping sideways, lifting and putting down). The references
in HH-Bench are specific instances chosen for evaluation. Where a reference was composed from reusable team skills, the
skill sequence is listed under `composed_from_units` in its `task.json`. Our training data and code will be released later.

HH-Bench itself does not prescribe a training protocol: you may train on the references directly or in any other way.

## Layout

```
manifest.json                 all task.json entries in one list
tasks/<id>/
  task.json                   robots, length, object (USD, scale), static scene objects, notes
  motion/agent_<k>/           reference of robot k: motion.npz + meta.json
  terrain.usd                 static walls in world coordinates (01, 02 only)
  terrain_boxes.json          the same walls as boxes (center, size, yaw)
objects/                      object and static scene USDs (paths in task.json)
robots/                       G1 URDFs + meshes used by the references
tools/load_task.py            load a task with numpy and print a summary
tools/replay.py               replay a task in Isaac Lab (optionally write a video)
```

## Data format

`motion.npz`, one per robot, 50 fps, `T` frames:

| key | shape | content |
|---|---|---|
| `body_pos_w`, `body_quat_w` | `[T, B, 3]`, `[T, B, 4]` | world pose of every body, quaternions `(w, x, y, z)`; order = `body_names` in `meta.json` |
| `body_lin_vel_w`, `body_ang_vel_w` | `[T, B, 3]` | world velocities |
| `joint_pos`, `joint_vel` | `[T, J]` | joint angles / velocities; order = `joint_names` in `meta.json` |
| `object_contact` | `[T, 2]` | 1 while the left / right hand should touch the object |

- `body_names` lists the robot links first (index 0 = pelvis = root), then the object and the static scene objects.
  The object and scene bodies are identical in every agent's file.
- Object poses are the pose of the USD prim origin of the object asset with the `scale` of `task.json` applied
  (for `objects/suitcase/suitcase.usd` this origin is a bottom corner, not the centre).
- Static scene objects (stairs, dolly, sawhorses, truck bed, millstone base) stay at their frame-0 pose.
- All robots share one time axis and one world frame and start together.

## Robots

| robot type | used by | joints |
|---|---|---|
| `g1_29dof_rubberhand-feet-complex` | most tasks | 29 |
| `g1_29dof_dex3_closed-feet-complex` | 01, 02, 05 (Dex3 hands fixed as fists) | 29 |
| `g1_29dof_dex3-feet-complex` | `10_fire_hose` Dex3 variant (actuated Dex3 fingers) | 43 |

All three are derived from Unitree's G1 description (BSD-3-Clause, see `robots/LICENSE_UNITREE`).

## Quick start

```bash
python tools/load_task.py --task 03b_table_4robots                    # numpy only
python tools/replay.py --task 03b_table_4robots                       # Isaac Lab GUI
python tools/replay.py --task 06_DollyPlace --headless --video dolly.mp4
python tools/replay.py --task 10_fire_hose --variant dex3
```

`tools/replay.py` needs Isaac Sim 5.0 and Isaac Lab (tested with Isaac Lab 0.44). It writes the reference pose of the
robots and the object every frame; nothing is simulated, so it shows the task, not a controller.

## Task notes

- **Team sizes.** Table (2 / 4 / 10), sofa (2 / 5), palanquin (2 / 4) and rebar (2 / 3) scale the object to the team.
  For the table, palanquin and rebar every robot performs the same motion at a different position; the 5-robot sofa is a
  larger L-sofa with its own motion.
- **`10_fire_hose`.** The hose is a physical PhysX articulation, not a rigid object, so it has no reference pose:
  - `objects/fire_hose/fire_hose.usd`: 9.4 m hose of 47 capsule links, the tail fixed to the hydrant;
    `objects/fire_hose/hose.json` lists its parameters.
  - PhysX starts every hose joint at 0 (straight hose); write `init_joint_pos_rad` from `hose.json` after reset.
  - The stands are one kinematic body that sinks 0.85 m into the floor at 0.5 m/s from frame 420.
  - The hose mass is left unset like all other masses.
- **`12_millstone`.** The upper stone turns about a revolute joint fixed to the world; anchor, axis and damping are in
  `object_revolute_joint` of `task.json`.
- **`terrain.usd`** contains static collision geometry only (no rigid bodies); reference it at the world origin.
- **`06_DollyPlace`.** The dolly sits right under the final box pose of the reference: the hands lower the box until its
  bottom is 1 cm above the dolly top, then let go.

## License

The L-sofa model (`objects/l_sofa/`) was created with Meshy AI under a paid plan. The robot models are derived from
Unitree's G1 description (BSD-3-Clause).
