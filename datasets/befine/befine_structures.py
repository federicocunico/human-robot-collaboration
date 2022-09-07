import json
import numpy as np
from typing import Any, List, Optional
from pydantic import BaseModel

"""
{
    "timestamp": 1661854037049, 
    "bodies": [
        {
            "body_id": "h0", 
            "event": [], 
            "keypoints": {
                "nose": [{"x": 7.86752986907959, "y": -2.7859725952148438, "z": 1.6457561254501343}],
                "left_ear": [{"x": 8.143104553222656, "y": -2.42840313911438, "z": 1.449127197265625}],
                "right_ear": [{"x": null, "y": null, "z": null}],
                "left_shoulder": [{"x": 7.692070722579956, "y": -2.7322360277175903, "z": 1.5049266815185547}],
                "right_shoulder": [{"x": 7.686703443527222, "y": -2.8926310539245605, "z": 1.525606393814087}],
                "left_elbow": [{"x": 7.655144214630127, "y": -2.660408139228821, "z": 1.1848040223121643}],
                "right_elbow": [{"x": 7.84174370765686, "y": -2.9815996885299683, "z": 1.2636361122131348}],
                "left_wrist": [{"x": 7.674472093582153, "y": -2.578041195869446, "z": 0.9961873292922974}],
                "right_wrist": [{"x": 7.837196111679077, "y": -2.9774341583251953, "z": 1.1755825877189636}],
                "left_hip": [{"x": 7.6080639362335205, "y": -2.9484660625457764, "z": 1.1869715452194214}],
                "right_hip": [{"x": 7.625810623168945, "y": -3.036259412765503, "z": 1.1760457754135132}],
                "left_knee": [{"x": null, "y": null, "z": null}],
                "right_knee": [{"x": null, "y": null, "z": null}],
                "left_ankle": [{"x": 7.536322593688965, "y": -2.830110192298889, "z": 0.31165218353271484}],
                "right_ankle": [{"x": 7.553667306900024, "y": -2.88664174079895, "z": 0.20994746685028076}],
                "neck": [{"x": 7.698575258255005, "y": -2.8514187335968018, "z": 1.546949326992035}],
                "chest": [{"x": 7.689387083053589, "y": -2.81243360042572, "z": 1.5152665376663208}],
                "mid_hip": [{"x": 7.6169373989105225, "y": -2.9923627376556396, "z": 1.1815086603164673}]
            }
        }
    ]
}
"""


class BeFineBodyKeypointCoords(BaseModel):
    name: str
    x: Optional[float]
    y: Optional[float]
    z: Optional[float]


class BeFineBodyKeypoints(BaseModel):
    def __init__(self, **data: Any) -> None:
        tmp = {"coords": []}
        # set_zero = lambda x: x if x is not None else 0
        for k, v in data.items():
            assert len(v) == 1, "Unexpected multiple coordinates for keypoint"
            kpts = v[0]
            x, y, z = kpts["x"], kpts["y"], kpts["z"]
            # fmt: off
            tmp["coords"].append(
                {
                    "name": k, 
                    # "x": set_zero(x), 
                    # "y": set_zero(y), 
                    # "z": set_zero(z),
                    "x": x, 
                    "y": y, 
                    "z": z
                }
            )
            # fmt: on

        super().__init__(**tmp)

    coords: List[
        BeFineBodyKeypointCoords
    ]  # NOTE: this should be only one element but the final data structure is still not defined


class BeFineBody(BaseModel):
    body_id: str
    event: List[Any] = []
    keypoints: BeFineBodyKeypoints

    def to_keypoints(self, scale=1, none_to_nan: bool = False):
        f = lambda x: x if x is not None else (float('nan') if none_to_nan else 0)
        return np.asarray([
            list(map(f, [k.x, k.y, k.z])) for k in self.keypoints.coords
        ])*scale


class BeFineDatum(BaseModel):
    timestamp: int
    bodies: List[BeFineBody] = []


class BeFineData(BaseModel):

    data: List[BeFineDatum] = []

    @staticmethod
    def load(path: str):
        with open(path, "r") as fp:
            lines = fp.readlines()

        data = {"data": [BeFineDatum(**json.loads(s)) for s in lines]}
        return BeFineData(**data)
