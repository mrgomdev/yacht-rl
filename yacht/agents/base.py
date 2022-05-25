import abc
import dataclasses

from ..yacht import ScoreBoard, Combination, Aces


@dataclasses.dataclass
class Environment:
    pass


@dataclasses.dataclass
class SoloEnvironment:
    score_board: ScoreBoard
    combination: Combination


class Action:
    pass


class Agent:
    @abc.abstractmethod
    def decide(self, environment: Environment) -> Action:
        raise NotImplementedError(f"{self.__class__.__name__}.decide() not implemented")
