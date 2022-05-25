from typing import Tuple

from . import base
from ..yacht import ScoreBoard, Combination


class RandomAgent(base.Agent):
    def decide(self, environment: Tuple[ScoreBoard, Combination]) -> base.Action:
        pass