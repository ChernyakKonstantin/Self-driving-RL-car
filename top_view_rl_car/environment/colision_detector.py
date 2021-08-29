class ColisionDetector:
    def __init__(self, min_distance_to_obstacle: float):
        self._min_distance_to_obstacle = min_distance_to_obstacle

    def check(self, observation: list) -> bool:
        return min(observation) <= self._min_distance_to_obstacle