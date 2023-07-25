from typing import Tuple, Union

import numpy as np
import pygame

from .abstract import GameObject, Observer


class Sensor(GameObject, Observer):
    """
    A distance sensor class.
    Simulation of a laser or ultrasonic sensor.
    """

    def __init__(self,
                 x: Union[float, int],
                 y: Union[float, int],
                 orientation: float,
                 n_rays: int = 30,
                 angle_of_view: int = 120,
                 ray_length: float = 200):
        super(Sensor, self).__init__()
        self._position = pygame.Vector2(x, y)
        self._orientation = orientation  # Направление центра
        self._n_rays = n_rays
        self._angle_of_view = angle_of_view
        self._ray_length = ray_length
        # Storage format: x_source, y_source, x_end, y_end
        self._rays_coordinates = np.empty(shape=(4, n_rays), dtype=float)
        # Storage format: x, y
        self._intersection_points = None
        self._fill_rays_coordinates()
        self._rays_idx = np.arange(self._n_rays)

    def _get_deltas(self) -> Tuple[np.ndarray, np.ndarray]:
        """
        The method calculates shifts of the rays endpoints from the rays source.

        Returns: Deltas of x and deltas of y.
        """
        alphas = np.linspace(self._orientation - self._angle_of_view / 2,
                             self._orientation + self._angle_of_view / 2,
                             num=self._n_rays)
        alphas = np.deg2rad(alphas)
        deltas_x = np.sin(alphas) * self._ray_length
        deltas_y = np.cos(alphas) * self._ray_length
        return deltas_x, deltas_y

    def _calculate_rays_endpoints(self) -> Tuple[np.ndarray, np.ndarray]:
        """
        The method fill the storage of rays endpoints with calculated values.
        """
        deltas_x, deltas_y = self._get_deltas()
        return self._position.x + deltas_x, self._position.y + deltas_y

    def _fill_rays_coordinates(self) -> None:
        """
        The method  fills the storage with calculated  the rays source and end coordinates.
        """
        self._rays_coordinates[0] = [self._position.x] * self._n_rays
        self._rays_coordinates[1] = [self._position.y] * self._n_rays
        self._rays_coordinates[[2, 3]] = self._calculate_rays_endpoints()

    def get_view(self, obstacle_coordinates: np.ndarray) -> np.ndarray:
        """
        The method returns distances to the obstacles. This is how the sensor sees the world.
        Args:
            obstacle_coordinates: Coordinates of points that form obstacles.

        Returns: Distances to the obstacles.
        """
        x, y = self._cast(*self._rays_coordinates, *obstacle_coordinates)
        distances = self._get_distance(np.stack((x, y))).reshape(self._n_rays, -1)
        x = x.reshape(self._n_rays, -1)[self._rays_idx, distances.argmin(axis=1)]
        y = y.reshape(self._n_rays, -1)[self._rays_idx, distances.argmin(axis=1)]
        point_selection = np.invert(np.isnan(x) | np.isnan(y))
        self._intersection_points = np.stack((x, y))[:, point_selection]
        return distances.min(axis=1)

    def _get_distance(self, intersection_points: np.ndarray) -> np.ndarray:
        """
        The method computes the distance from the rays source to the intersection points.
        For absent intersection points "self._ray_length" is returned.

        Args:
            intersection_points: Points where the rays intersects obstacles.

        Returns: Distances from the rays source to the intersection points.
        """
        distances = np.sqrt(np.square(np.reshape(self._position, (-1, 1)) - intersection_points).sum(axis=0))
        distances[np.isnan(distances)] = self._ray_length
        self._distances = distances
        return distances

    def update(self, x: float, y: float, orientation: float) -> None:
        self._position.update(x, y)
        self._orientation = orientation
        self._fill_rays_coordinates()

    def _cast(self,
              x1: np.ndarray,
              y1: np.ndarray,
              x2: np.ndarray,
              y2: np.ndarray,
              x3: np.ndarray,
              y3: np.ndarray,
              x4: np.ndarray,
              y4: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        The method returns np.nan for rays that do not intersect an obstacle.
        The method precomputes reusable data and cache it.
        Args:
            x1: X coordinates of a ray source.
            y1: y coordinates of a ray source.
            x2: X coordinates of a ray end.
            y2: y coordinates of a ray end.
            x3: X coordinates of an obstacle line begin.
            y3: y coordinates of an obstacle line begin.
            x4: X coordinates of an obstacle line end.
            y4: y coordinates of an obstacle line end.

        Returns:
            X, Y coordinates of intersection points.
        """

        # Values that are reused while casting each of rays.
        cached_y3_sub_y4 = y3 - y4
        cached_x3_sub_x4 = x3 - x4
        cached_diff = x3 * y4 - y3 * x4

        def _cast_ray(rays_points: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
            """

            Args:
                rays_points: source X, source Y, end X, end Y coordinates of a ray.

            Returns:
                Found points where the ray intersects obstacles.
            """
            x1, y1, x2, y2 = rays_points
            # Reusable values
            x1_dif_x2 = x1 - x2
            y1_dif_y2 = y1 - y2
            common = x1 * y2 - y1 * x2

            denom = x1_dif_x2 * cached_y3_sub_y4 - y1_dif_y2 * cached_x3_sub_x4
            denom[denom == 0] = np.nan
            x_nom = common * cached_x3_sub_x4 - x1_dif_x2 * cached_diff
            y_nom = common * cached_y3_sub_y4 - y1_dif_y2 * cached_diff
            x = x_nom / denom
            y = y_nom / denom
            on_line_1 = ((((x1 <= x) & (x <= x2)) | ((x2 <= x) & (x <= x1)))
                         & (((y1 <= y) & (y <= y2)) | ((y2 <= y) & (y <= y1))))
            on_line_2 = ((((x3 <= x) & (x <= x4)) | ((x4 <= x) & (x <= x3)))
                         & (((y3 <= y) & (y <= y4)) | ((y4 <= y) & (y <= y3))))
            x[np.invert(on_line_1 & on_line_2)] = np.nan
            y[np.invert(on_line_1 & on_line_2)] = np.nan
            return x, y

        ray_points = np.stack((x1, y1, x2, y2))
        x, y = np.apply_along_axis(_cast_ray, axis=0, arr=ray_points)
        return x.T.reshape(-1), y.T.reshape(-1)

    def show(self, surface) -> None:
        """
        The methods draw the sensor rays
        Args:
            surface: Surface to draw on.
        """
        # Show sensor area
        for i in range(self._rays_coordinates.shape[-1]):
            pygame.draw.line(surface,
                             pygame.Color("green"),
                             *self._rays_coordinates[:, i].reshape(2, 2),
                             width=1)

        # Show points that are found by the sensor
        for i in range(self._intersection_points.shape[-1]):
            pygame.draw.circle(surface,
                               pygame.Color("green"),
                               self._intersection_points[:, i],
                               radius=3)
