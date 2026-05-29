#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import math
import yaml
import numpy as np
from PIL import Image
from pathlib import Path

try:
    from scipy.ndimage import distance_transform_edt
except ImportError:
    distance_transform_edt = None


class AutoPointSelector:
    def __init__(
        self,
        map_yaml_path: str,
        num_points: int = 3,
        safety_distance_m: float = 0.35,
        candidate_step_px: int = 10,
        min_point_distance_m: float = 0.8,
    ):
        self.map_yaml_path = Path(map_yaml_path)
        self.num_points = num_points
        self.safety_distance_m = safety_distance_m
        self.candidate_step_px = candidate_step_px
        self.min_point_distance_m = min_point_distance_m

    def load_map(self):
        with open(self.map_yaml_path, "r") as f:
            info = yaml.safe_load(f)

        pgm_path = self.map_yaml_path.parent / info["image"]
        img = Image.open(pgm_path).convert("L")
        grid = np.array(img)

        resolution = float(info["resolution"])
        origin = info["origin"]

        return grid, resolution, origin

    def select_points(self):
        grid, resolution, origin = self.load_map()

        # map_server系のpgmでは白に近いほど自由空間、黒に近いほど障害物
        free = grid > 250

        safety_px = max(1, int(self.safety_distance_m / resolution))

        if distance_transform_edt is None:
            raise RuntimeError(
                "scipyが必要です。sudo apt install python3-scipy または pip install scipy を実行してください。"
            )

        dist = distance_transform_edt(free)
        safe_area = dist >= safety_px

        candidates = []
        h, w = safe_area.shape

        for y in range(0, h, self.candidate_step_px):
            for x in range(0, w, self.candidate_step_px):
                if safe_area[y, x]:
                    candidates.append((x, y))

        if len(candidates) == 0:
            raise RuntimeError("安全距離を満たす候補点がありません。safety_distance_mを小さくしてください。")

        selected = self._farthest_point_sampling(candidates, resolution)

        waypoints = []
        for x_px, y_px in selected:
            x_ros, y_ros = self.pixel_to_ros(x_px, y_px, h, resolution, origin)
            yaw = 0.0
            waypoints.append((x_ros, y_ros, yaw))

        return waypoints

    def _farthest_point_sampling(self, candidates, resolution):
        selected = []

        # 1点目：候補群の中心に近い点
        arr = np.array(candidates)
        center = arr.mean(axis=0)
        first_idx = np.argmin(np.linalg.norm(arr - center, axis=1))
        selected.append(tuple(arr[first_idx]))

        min_dist_px = self.min_point_distance_m / resolution

        while len(selected) < self.num_points:
            best = None
            best_score = -1.0

            for c in candidates:
                if any(self._dist_px(c, s) < min_dist_px for s in selected):
                    continue

                score = min(self._dist_px(c, s) for s in selected)

                if score > best_score:
                    best_score = score
                    best = c

            if best is None:
                break

            selected.append(best)

        return selected

    def _dist_px(self, p1, p2):
        return math.hypot(p1[0] - p2[0], p1[1] - p2[1])

    def pixel_to_ros(self, x_px, y_px, height, resolution, origin):
        x_ros = origin[0] + x_px * resolution
        y_ros = origin[1] + (height - y_px) * resolution
        return x_ros, y_ros