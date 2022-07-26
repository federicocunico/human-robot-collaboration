# Human-Robot Collaboration
Utils for "[Pose Forecasting in Industrial Human-Robot Collaboration](https://pythondig.com/r/repository-for-pose-forecasting-in-industrial-humanrobot-collaboration-eccv)" paper accepted at ECCV'22. 

The code for the forecasting is available [here](https://github.com/AlessioSam/CHICO-PoseForecasting/).
In this repository there is a torch dataloader for the inspection of the dataset, with utils for visualization using Open3D. 

NOTE: the suggested version for open3d is 0.15.2, as the API keeps changing and the older versions may differ a lot.


## Requirements:
Python 3.x (suggested 3.8+)
    - Numpy
    - PyTorch
    - open3d>=0.15.2

## Dataset
The dataset is available [here](https://univr-my.sharepoint.com/:f:/g/personal/federico_cunico_univr_it/Eh3Mau4d7WpLpP06TsMimzABKD344Bmy3xFFk473QlPrhA?e=rwLhhV) and presents both 3D poses (for human and robot) and the RGB video frames.

## Run the visualization
The current code visualize the 3D poses only.
The code to run is `show_poses.py`. 
