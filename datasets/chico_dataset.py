import os
import glob
import pickle
from typing import Any, List, Optional, Tuple
import torch
from torch.utils.data.dataset import Dataset
from torch.utils.data.dataloader import DataLoader


class CHICODataset(Dataset):
    """CHICO Dataset Dataloader

    Expecting this folder structure:

    ROOT/
        poses/
            S00/
                lift.pkl
                span_light.pkl
                place-lp_CRASH.pkl
                ...
            S01/
                lift.pkl
                span_light.pkl
                place-lp_CRASH.pkl
                ...
            ...
        rgb/
            S00/
                00_03.mp4
                00_06.mp4
                00_12.mp4
            S01/
                00_03.mp4
                00_06.mp4
                00_12.mp4
            ...

    # ----------------------------------------------------------
    Pickles of poses contains a List of time instants.
    For each time instant you will find
        - Person Keypoints 3D
        - Robot Keypoints 3D

    # ----------------------------------------------------------
    Keypoints linkings
    [[0,1], [1,2], [2,3], [0,4], [4,5], [5,6], [1,9], [4,12], [8,7], [8,9], [8,12], [9,10], [10,11], [12,13], [13,14]]

    """

    actions = [
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
        "span_light",
        "span_light_CRASH",
    ]

    keypoints_dict = {
        "hip": 0,
        "r_hip": 1,
        "r_knee": 2,
        "r_foot": 3,
        "l_hip": 4,
        "l_knee": 5,
        "l_foot": 6,
        "nose": 7,
        "c_shoulder": 8,
        "r_shoulder": 9,
        "r_elbow": 10,
        "r_wrist": 11,
        "l_shoulder": 12,
        "l_elbow": 13,
        "l_wrist": 14,
    }

    keypoints_links = [
        [0,1],
        [1,2],
        [2,3],
        [0,4],
        [4,5],
        [5,6],
        [1,9],
        [4,12],
        [8,7],
        [8,9],
        [8,12],
        [9,10],
        [10,11],
        [12,13],
        [13,14]
    ]

    kuka_links = [
        [0,1],
        [1,2],
        [2,3],
        [3,4],
        [4,5],
        [5,6],
        [6,7],
        [7,8]
    ]

    def __init__(
        self,
        root: str,
        action_filter: Optional[str] = None,
        subject_filter: Optional[str] = None,
    ) -> None:
        super().__init__()

        assert os.path.isdir(root), f"Folder not found {root}!"

        poses_path = os.path.join(root, "poses")
        rgb_path = os.path.join(root, "rgb")

        poses_found = os.path.isdir(poses_path) and len(os.listdir(poses_path)) > 1
        rgb_found = os.path.isdir(rgb_path) and len(os.listdir(rgb_path)) > 1

        assert poses_found or rgb_found, "Excpected at least Poses or RGB to be found!"

        if not poses_found:
            print(f"No Poses found in {root}")
        if not rgb_found:
            print(f"No RGB found in {root}")

        if rgb_found:
            raise NotImplementedError("TODO: implement RGB loading")

        poses_pkls = glob.glob(poses_path + "/**/*.pkl", recursive=True)

        if action_filter is not None:
            if action_filter not in self.actions:
                err = f"Action: {action_filter} is not a valid action. Available actions are: {self.actions}"
                print(err)
                raise RuntimeError(err)

            poses_pkls = [
                p for p in poses_pkls if f"{action_filter}.pkl" in os.path.split(p)[1]
            ]
        if subject_filter is not None:
            poses_pkls = [
                p for p in poses_pkls if f"{os.sep}{subject_filter}{os.sep}" in p
            ]

        self.poses_pkls = poses_pkls
        # self.poses = {
        #     self.__get_subject_and_action(p): read_pickle(p) for p in poses_pkls
        # }
        tmp = [self.read_pickle(p) for p in poses_pkls]

        # subject, action, person_kpts, robot_kpts
        self.poses = [
            self.__get_subject_and_action(p) + (tmp[i][0], tmp[i][1])
            for (i, p) in enumerate(poses_pkls)
        ]

        print(f"Found {len(self.poses)} files")

    def __get_subject_and_action(self, path: str):
        res, action = os.path.split(path)
        _, subject = os.path.split(res)

        action = action.replace(".pkl", "")

        return subject, action

    def read_pickle(self, pickle_path: str):
        person_kpts = []
        robot_kpts = []
        with open(pickle_path, "rb") as fp:
            data = pickle.load(fp)
            for d in data:
                person_kpts.append(d[0])
                robot_kpts.append(d[1])

        return person_kpts, robot_kpts

    def __len__(self):
        return len(self.poses)

    def __getitem__(
        self, index
    ) -> Tuple[str, str, List[List[List[float]]], List[List[List[float]]]]:
        """Get item of dataset

        Args:
            index (int): index of poses and rgbs

        Returns:
            Tuple[str, str, List[List[List[float]]], List[List[List[float]]]]: subject, action, person keypoints per temporal index [N,15,3], robot keypoints per temporal index [N,9,3]
        """
        # subject, action, person_kpts, robot_kpts
        return self.poses[index], None


def __test__():
    dataset = CHICODataset("data/chico", subject_filter="S01")
    # dataset = CHICODataset("data/chico", subject_filter="S01", action_filter="hammer")

    for datum in dataset:
        print(datum)


if __name__ == "__main__":
    __test__()
