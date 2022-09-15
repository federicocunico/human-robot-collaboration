import os
import numpy as np
from datasets.befine.befine_dataset import BeFineDataset
from datasets.befine.befine_structures import BeFineBody
from visualizer.open3d_wrapper import Open3DWrapper


def main():
    FPS = 8

    camera_position_set = False
    wrapper = Open3DWrapper()
    wrapper.initialize_visualizer()

    # all_actions = CHICODataset.actions
    all_actions = [
        # "span_light",
        # "span_light_CRASH",
        # "hammer",
        "lift",
        "place_hp",
        "place_hp_CRASH",
        "place_lp",
        "place_lp_CRASH",
        "polish",
        "polish_CRASH",
        "span_heavy",
        "span_heavy_CRASH",
    ]

    all_subjects = ["avo"]
    for subj in all_subjects:
        print("-"*150)
        print(f"Subject: {subj}")
        for action in all_actions:
            print("Running action: ", action)
            
            befine = BeFineDataset(
                "data/godot", subj, action
            )
            links = [
                [3,4],
                [3,5],
                [4,6],
                [5,7],
                [6,8],
                [9,3],
                [10,4],
                [11,9],
                [12,10],
                [11,13],
                [12,14],
                [0,16],
            ]
            coordinate_system = None
            skeleton = None

            for ii, data in enumerate(befine):
                # assert len(data.bodies) < 2
                if len(data.bodies) == 0:
                    person_kpts = []
                else:
                    body: BeFineBody = data.bodies[0]
                    person_kpts = body.to_keypoints(scale=10)
                
                if len(person_kpts) != 0:  # ho davvero una persona
                    # not show NaN / None keypoints
                    # idxs = [i for i, k in enumerate(person_kpts) if np.isnan(k).all()]
                    # new_links = np.asarray([l for l in links if l[0] not in idxs and l[1] not in idxs])
                    # new_links -= len(idxs)
                    # new_links = new_links.tolist()
                    # person_kpts = [p for i, p in enumerate(person_kpts) if i not in idxs]

                    # Create / Update person skeleton
                    if skeleton is None:
                        skeleton = wrapper.create_skeleton(person_kpts, links, radius=0.5)
                    else:
                        skeleton.update(person_kpts)

                    # Add coordinate system
                    if coordinate_system is None:
                        pts = np.asarray(person_kpts)
                        pts = pts[~np.all(pts == 0, axis=1)]
                        loc = [
                            np.min(pts[:, 0]).item(),
                            np.min(pts[:, 1]).item(),
                            np.min(pts[:, 2]).item(),
                        ]
                        coordinate_system = wrapper.create_coordinate_system(loc, 5)

                wrapper.update()
                wrapper.wait(1 / FPS)

                if not camera_position_set:
                    wrapper.set_camera_visualization()
                    camera_position_set = True

                d = f"output/{action}"
                if not os.path.isdir(d):
                    os.makedirs(d)
                wrapper.save(f"{d}/{ii}.jpg")

            wrapper.clear()
            
            # Clear view variables
            del skeleton
            skeleton = None
            del coordinate_system
            coordinate_system = None
            camera_position_set = False


if __name__ == "__main__":
    main()
