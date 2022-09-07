import json
import os
import glob
import pickle
from typing import Any, Dict, List, Optional, Tuple
import torch
from tqdm import tqdm
from torch.utils.data.dataset import Dataset
from torch.utils.data.dataloader import DataLoader
from datasets.befine.befine_structures import BeFineData


class BeFineDataset(Dataset):
    def __init__(
        self, root: str, subject: Optional[str] = None, action: Optional[str] = None
    ) -> None:
        super().__init__()
        self.root = root  # os.path.abspath(root)
        self.action = action

        subjects_folders = glob.glob(os.path.join(self.root, "*"))

        if subject is not None:
            subjects_folders = [
                p for p in subjects_folders if p.split(os.sep)[-1] == subject
            ]

        self.subjects = {
            f: {"actions": self.get_actions(glob.glob(os.path.join(f, "actions", "*")))}
            for f in subjects_folders
        }

    def get_actions(self, subject_actions: str):
        if len(subject_actions) == 0:
            return {}

        res: Dict[str, List[str]] = {}
        # root, _ = os.path.split(subject_actions[0])
        # actions = [s.split(os.sep)[-1] for s in subject_actions]

        for action_path in tqdm(subject_actions):
            _, action = os.path.split(action_path)

            tmp = action.split(".csv")[0]
            tmp = tmp.split("_")
            usr = tmp[0]
            is_single_camera = "jetsonzed" in "_".join(tmp[1:])

            if is_single_camera:
                # raise NotImplementedError
                # data = []
                continue
            else:
                data = BeFineData.load(action_path)

            if self.action is not None:
                if self.action not in action:
                    continue

            res[action_path] = data

        return res

    def __len__(self) -> int:
        if len(self.subjects) == 0:
            return 0
        subj = next(iter(self.subjects))
        actions = self.subjects[subj]
        if len(actions) == 0:
            return 0

        all_actions: Dict[str, BeFineData] = actions["actions"]
        act_name = next(iter(all_actions))
        act: BeFineData = all_actions[act_name]

        return len(act.data)

    def __getitem__(self, index):
        if len(self.subjects) == 0:
            return None
        subj = next(iter(self.subjects))
        actions = self.subjects[subj]
        if len(actions) == 0:
            return None

        all_actions: Dict[str, BeFineData] = actions["actions"]
        act_name = next(iter(all_actions))
        act: BeFineData = all_actions[act_name]

        return act.data[index]


def __test__():
    subj = "avo"
    action = "hammer"
    dataset = BeFineDataset("data/godot", subject=subj, action=action)
    n = len(dataset)
    
    print(f"For subject {subj} and action {action} found {n} samples")
    for data in dataset:
        print(data)


if __name__ == "__main__":
    __test__()
