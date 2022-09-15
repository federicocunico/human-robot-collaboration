import os
import time
from typing import Any, List, Optional, Union
import open3d as o3d
import numpy as np
from trimesh import PointCloud


class Open3DSkeleton:
    def __init__(
        self,
        points: List[o3d.geometry.TriangleMesh],
        lines: Optional[o3d.geometry.LineSet] = None,
        links: List[List[int]] = None,
    ) -> None:
        self.points = points
        self.lines = lines

        if lines is not None:
            assert links is not None, "If lines is provided, include also the links "
        self.links = links

    def update(
        self,
        points_locations: List[List[int]],
        relative: bool = False,
        new_colors: List[List[int]] = None,
    ) -> None:
        assert len(points_locations) == len(
            self.points
        ), "Expected the new locations to have the same number of elements of self.points!"

        if new_colors is not None:
            assert len(new_colors) == len(
                self.points
            ), "Expected the new colors to have the same number of elements of self.points!"

        for i, pt in enumerate(self.points):
            pt.translate(points_locations[i], relative=relative)
            if new_colors is not None:
                pt.paint_uniform_color(new_colors[i])

        # from docs:
        # line_set.points = o3d.utility.Vector3dVector(points)
        # line_set.lines = o3d.utility.Vector2iVector(lines)
        # line_set.colors = o3d.utility.Vector3dVector(colors)

        if self.lines is not None:
            self.lines.points = o3d.utility.Vector3dVector(points_locations)
            # self.lines.lines = o3d.utility.Vector2iVector(self.links)  # necessario solo se cambia self.links

            if new_colors is not None:
                self.lines.colors = o3d.utility.Vector3dVector(new_colors)


class Open3DWrapper:
    def __init__(self) -> None:
        self.vis: o3d.visualization.Visualizer = None

        self.geometries = []

    def initialize_visualizer(self) -> o3d.visualization.Visualizer:
        vis = o3d.visualization.Visualizer()
        vis.create_window()
        self.vis = vis

        return vis

    def set_camera_visualization(self) -> None:
        if self.vis is None:
            return

        if not os.path.isfile("camera_config.json"):
            print("Camera parameters not found!! Press ctrl+p to generate.")
            return

        wc = self.vis.get_view_control()
        # depends on your screen, when running press ctrl+p to generate a new file with visualization info
        camera_parameters = o3d.io.read_pinhole_camera_parameters("camera_config.json")
        wc.convert_from_pinhole_camera_parameters(camera_parameters)

        self.vis.poll_events()
        self.vis.update_renderer()

    # def set_camera_transform(self, location, rotation):
    #     ctrl = self.vis.get_view_control()
    #     ctrl.translate(0,0)

    def save(self, fname):
        self.vis.capture_screen_image(fname)

    def update(self) -> None:
        # Step 1: update geometries transforms
        for geom in self.geometries:
            self.vis.update_geometry(geom)

        # Step 2: wait for events
        self.vis.poll_events()

        # Step 3: update renderer view
        self.vis.update_renderer()

    def wait(self, seconds: int) -> None:
        # TODO: inspect self.vis.run()
        start = time.time()
        while True:
            if time.time() - start > seconds:
                break
            self.update()

    def add_geometry(self, geometry: Union[PointCloud, List[PointCloud]]) -> None:
        assert (
            self.vis is not None
        ), "Visualizer is required, try to call initialize_visualizer()"
        if isinstance(geometry, list):
            [self.vis.add_geometry(geom) for geom in geometry]
            self.geometries += geometry
        else:
            self.vis.add_geometry(geometry)
            self.geometries.append(geometry)

    def create_box(
        self,
        location: Optional[List[int]] = None,
        rotation: Optional[List[int]] = None,
        color: Optional[List[int]] = None,
    ) -> o3d.geometry.TriangleMesh:
        if color is None:
            color = [1.0, 0.0, 0.0]  # red

        mesh_box = o3d.geometry.TriangleMesh.create_box(
            width=1.0, height=1.0, depth=1.0
        )
        mesh_box.compute_vertex_normals()
        mesh_box.paint_uniform_color([0.9, 0.1, 0.1])
        # mesh_cylinder = o3d.geometry.TriangleMesh.create_cylinder(
        #     radius=0.3, height=4.0
        # )
        # mesh_cylinder.compute_vertex_normals()
        # mesh_cylinder.paint_uniform_color([0.1, 0.9, 0.1])
        return mesh_box

    def create_sphere(
        self,
        location: Optional[List[int]] = None,
        radius: float = 1.0,
        color: Optional[List[int]] = None,
    ):

        if color is None:
            color = [1.0, 0.0, 0.0]  # red

        if location is None:
            location = [0, -1, 0]

        mesh_sphere = o3d.geometry.TriangleMesh.create_sphere(radius=radius)
        mesh_sphere.compute_vertex_normals()

        mesh_sphere.translate(location, relative=False)
        mesh_sphere.paint_uniform_color(color)

        self.add_geometry(mesh_sphere)

        return mesh_sphere

    def create_coordinate_system(
        self, origin: List[int] = None, size: float = 0.6
    ) -> o3d.geometry.TriangleMesh:
        if origin is None:
            origin = [0, 0, 0]
        mesh_frame = o3d.geometry.TriangleMesh.create_coordinate_frame(
            size=size, origin=origin
        )

        self.add_geometry(mesh_frame)
        return mesh_frame

    def craete_lines(self, points, lines, colors, scale=5) -> None:
        if not lines:
            return
        line_set = o3d.geometry.LineSet(
            points=o3d.utility.Vector3dVector(points),
            lines=o3d.utility.Vector2iVector(lines),
        )
        # line_set.scale(scale)
        line_set.colors = o3d.utility.Vector3dVector(colors)
        self.add_geometry(line_set)
        return line_set

    def create_points(
        self, points, point_colors, radius
    ) -> List[o3d.geometry.TriangleMesh]:
        res: List[o3d.geometry.TriangleMesh] = []
        for (i, p) in enumerate(points):
            s = self.create_sphere(p, radius, color=point_colors[i])
            res.append(s)
        return res

    def create_skeleton(
        self,
        points: List[List[int]],
        links: List[List[int]],
        line_colors: Optional[List[List[int]]] = None,
        point_colors: Optional[List[List[int]]] = None,
        radius: float = 0.5,
    ) -> Open3DSkeleton:
        if point_colors is None:
            point_colors = [[125 / 255, 125 / 255, 125 / 255]] * len(points)

        if line_colors is None:
            line_colors = [[125 / 255, 125 / 255, 125 / 255]] * len(points)

        # Draw points
        mesh_pts = self.create_points(points, point_colors, radius)
        mesh_lines = self.craete_lines(points, links, line_colors)

        skeleton = Open3DSkeleton(mesh_pts, mesh_lines, links)

        return skeleton

    def clear(self):
        for geom in self.geometries:
            self.vis.remove_geometry(geom)

        self.geometries.clear()

    def destroy_window(self):
        if self.vis is not None:
            self.vis.destroy_window()
            self.vis = None

        self.geometries.clear()


def __test__():
    o3d.utility.set_verbosity_level(o3d.utility.VerbosityLevel.Debug)
    pcd_data = o3d.data.DemoICPPointClouds()
    source_raw = o3d.io.read_point_cloud(pcd_data.paths[0])
    target_raw = o3d.io.read_point_cloud(pcd_data.paths[1])

    source = source_raw.voxel_down_sample(voxel_size=0.02)
    target = target_raw.voxel_down_sample(voxel_size=0.02)
    trans = [
        [0.862, 0.011, -0.507, 0.0],
        [-0.139, 0.967, -0.215, 0.7],
        [0.487, 0.255, 0.835, -1.4],
        [0.0, 0.0, 0.0, 1.0],
    ]
    source.transform(trans)

    flip_transform = [[1, 0, 0, 0], [0, -1, 0, 0], [0, 0, -1, 0], [0, 0, 0, 1]]
    source.transform(flip_transform)
    target.transform(flip_transform)

    # vis = o3d.visualization.Visualizer()
    # vis.create_window()
    # vis.add_geometry(source)
    # vis.add_geometry(target)
    wrapper = Open3DWrapper()
    wrapper.initialize_visualizer()
    wrapper.add_geometry(source)
    wrapper.add_geometry(target)

    threshold = 0.05
    icp_iteration = 100

    for i in range(icp_iteration):
        reg_p2l = o3d.pipelines.registration.registration_icp(
            source,
            target,
            threshold,
            np.identity(4),
            o3d.pipelines.registration.TransformationEstimationPointToPlane(),
            o3d.pipelines.registration.ICPConvergenceCriteria(max_iteration=1),
        )
        source.transform(reg_p2l.transformation)
        wrapper.update()

    wrapper.destroy_window()
    o3d.utility.set_verbosity_level(o3d.utility.VerbosityLevel.Info)


def __test2__():
    wrapper = Open3DWrapper()
    wrapper.initialize_visualizer()
    wrapper.create_coordinate_system([-2, -2, -2])

    points = [
        [0, 0, 0],
        [1, 0, 0],
        [0, 1, 0],
        [1, 1, 0],
        [0, 0, 1],
        [1, 0, 1],
        [0, 1, 1],
        [1, 1, 1],
    ]
    [wrapper.create_sphere(p, 0.1) for p in points]

    lines = [
        [0, 1],
        [0, 2],
        [1, 3],
        [2, 3],
        [4, 5],
        [4, 6],
        [5, 7],
        [6, 7],
        [0, 4],
        [1, 5],
        [2, 6],
        [3, 7],
    ]
    colors = [[1, 0, 0] for i in range(len(lines))]

    wrapper.craete_lines(points, lines, colors)

    wrapper.update()
    wrapper.wait(5)
    wrapper.clear()
    wrapper.wait(5)

    wrapper.destroy_window()


def __demo__():
    o3d.utility.set_verbosity_level(o3d.utility.VerbosityLevel.Debug)
    pcd_data = o3d.data.DemoICPPointClouds()
    source_raw = o3d.io.read_point_cloud(pcd_data.paths[0])
    target_raw = o3d.io.read_point_cloud(pcd_data.paths[1])

    source = source_raw.voxel_down_sample(voxel_size=0.02)
    target = target_raw.voxel_down_sample(voxel_size=0.02)
    trans = [
        [0.862, 0.011, -0.507, 0.0],
        [-0.139, 0.967, -0.215, 0.7],
        [0.487, 0.255, 0.835, -1.4],
        [0.0, 0.0, 0.0, 1.0],
    ]
    source.transform(trans)

    flip_transform = [[1, 0, 0, 0], [0, -1, 0, 0], [0, 0, -1, 0], [0, 0, 0, 1]]
    source.transform(flip_transform)
    target.transform(flip_transform)

    vis = o3d.visualization.Visualizer()
    vis.create_window()
    vis.add_geometry(source)
    vis.add_geometry(target)
    threshold = 0.05
    icp_iteration = 100
    save_image = False

    for i in range(icp_iteration):
        reg_p2l = o3d.pipelines.registration.registration_icp(
            source,
            target,
            threshold,
            np.identity(4),
            o3d.pipelines.registration.TransformationEstimationPointToPlane(),
            o3d.pipelines.registration.ICPConvergenceCriteria(max_iteration=1),
        )
        source.transform(reg_p2l.transformation)
        vis.update_geometry(source)
        vis.poll_events()
        vis.update_renderer()
        if save_image:
            vis.capture_screen_image("temp_%04d.jpg" % i)
    vis.destroy_window()
    o3d.utility.set_verbosity_level(o3d.utility.VerbosityLevel.Info)


if __name__ == "__main__":
    # __demo__()
    # __test__()
    __test2__()
