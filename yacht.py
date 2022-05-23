import abc
import dataclasses
import random
from typing import ClassVar, Tuple, Protocol


DICE_NUMBERS = tuple(range(1, 7))
Combination = Tuple[int, ...]
COMBINATION_LENGTH = 5


def rand_combination(k: int = COMBINATION_LENGTH) -> Combination:
    return tuple(random.choices(DICE_NUMBERS, k=k))


if __name__ == '__main__':
    assert len(rand_combination()) == COMBINATION_LENGTH
    assert all(each in DICE_NUMBERS for each in rand_combination())


@runtime_checkable
class Category(Protocol):
    @classmethod
    @abc.abstractmethod
    def match(cls, combination: Combination) -> bool:
        return False

    @classmethod
    @abc.abstractmethod
    def _measure(cls, combination: Combination) -> int:
        raise NotImplementedError('Implement .measure()')

    @classmethod
    def measure(cls, combination: Combination) -> int:
        if not cls.match(combination):
            return 0
        return cls._measure(combination)


class MatchSpecific(Category):
    specific: ClassVar[int] = 0

    @classmethod
    def match(cls, combination: Combination) -> bool:
        return True

    @classmethod
    def _measure(cls, combination: Combination) -> int:
        return sum(each for each in combination if each == cls.specific)


class Ones(MatchSpecific):
    specific: ClassVar[int] = 1


class Twos(MatchSpecific):
    specific: ClassVar[int] = 2


class Threes(MatchSpecific):
    specific: ClassVar[int] = 3


class Fours(MatchSpecific):
    specific: ClassVar[int] = 4


class Fives(MatchSpecific):
    specific: ClassVar[int] = 5


class Sixs(MatchSpecific):
    specific: ClassVar[int] = 6


if __name__ == '__main__':
    my_combination = (1, 2, 3, 4, 5)
    assert 1 == Ones.measure(my_combination)
    assert 2 == Twos.measure(my_combination)

    my_combination = (2, 3, 4, 5, 6)
    assert 0 == Ones.measure(my_combination)
    assert 2 == Twos.measure(my_combination)

    my_combination = rand_combination()
    assert sum(filter(lambda x: x == 1, my_combination)) == Ones.measure(my_combination)
    assert sum(filter(lambda x: x == 2, my_combination)) == Twos.measure(my_combination)


@dataclasses.dataclass(frozen=True)
class ScoreBoardRow:
    combination: Combination
    category: Category
    score: int = dataclasses.field(init=False)

    def __post_init__(self):
        if not isinstance(self.combination, tuple) or not all(isinstance(each, int) for each in self.combination):
            raise TypeError(f'self.combination should be Combination type. Got {type(self.combination)}')
        if not isinstance(self.category, Category):
            raise TypeError(f'self.category should be Category. Got {type(self.category)}')
        object.__setattr__(self, 'score', self.category.measure(combination=self.combination))


if __name__ == '__main__':
    my_combination = (1, 1, 2, 5, 5)
    my_row = ScoreBoardRow(combination=my_combination, category=Ones)
    assert 2 == my_row.score

    my_row = ScoreBoardRow(combination=my_combination, category=Twos)
    assert 2 == my_row.score

    my_row = ScoreBoardRow(combination=my_combination, category=Threes)
    assert 0 == my_row.score


class ScoreBoard:
    pass


class Game:
    pass
