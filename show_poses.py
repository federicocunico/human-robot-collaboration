import numpy as np
from chico_dataset import CHICODataset
from open3d_wrapper import Open3DWrapper


def main():
    FPS = 25

    wrapper = Open3DWrapper()
    wrapper.initialize_visualizer()

    # all_actions = CHICODataset.actions
    all_actions = [
        "span_light",
        "span_light_CRASH",
        "hammer",
        "lift",
        "place-hp",
        "place-hp_CRASH",
        "place-lp",
        "place-lp_CRASH",
        "polish",
        "polish_CRASH",
        "span_heavy",
        "span_heavy_CRASH",
    ]

    all_subjects = ["S{0}".format(str(i).zfill(2)) for i in range(12)]
    for subj in all_subjects:
        print("-"*150)
        print(f"Subject: {subj}")
        for action in all_actions:
            print("Running action: ", action)
            chico = CHICODataset("data/chico", subject_filter=subj, action_filter=action)
            links = chico.keypoints_links
            kuka_links = chico.kuka_links

            coordinate_system = None

            for poses_data, rgb_data in chico:
                subj, act, all_person_kpts, all_robot_kpts = poses_data

                skeleton, robot = None, None
                for i, person_kpts in enumerate(all_person_kpts):
                    robot_kpts = all_robot_kpts[i]

                    # Create / Update person skeleton
                    if skeleton is None:
                        skeleton = wrapper.create_skeleton(person_kpts, links, radius=20)
                    else:
                        skeleton.update(person_kpts)

                    # Create / Update robot skeleton
                    if robot is None:
                        robot = wrapper.create_skeleton(
                            robot_kpts,
                            kuka_links,
                            radius=20,
                            line_colors=[[0, 0, 1]] * 9,
                            point_colors=[[0, 0, 1]] * 9,
                        )
                    else:
                        robot.update(robot_kpts)

                    # Add coordinate system
                    if coordinate_system is None:
                        pts = np.asarray(person_kpts)
                        loc = [
                            np.min(pts[:, 0]).item(),
                            np.min(pts[:, 1]).item(),
                            np.min(pts[:, 2]).item(),
                        ]
                        coordinate_system = wrapper.create_coordinate_system(loc, 150)

                    wrapper.update()
                    wrapper.wait(1 / FPS)

                wrapper.clear()


if __name__ == "__main__":
    main()
