import abc
import dataclasses
import random
from typing import Sequence, ClassVar, Tuple, Protocol, Dict, runtime_checkable, Optional

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


class SumAll(Category):
    @classmethod
    def _measure(cls, combination: Combination) -> int:
        return sum(combination)


class Choice(SumAll):
    @classmethod
    def match(cls, combination: Combination) -> bool:
        return True


class FourOfAKind(SumAll):
    NUM_DUPLICATES = 4

    @classmethod
    def match(cls, combination: Combination) -> bool:
        uniques = set(int(each) for each in combination)
        return any(combination.count(each) >= cls.NUM_DUPLICATES for each in uniques)


class FullHouse(SumAll):
    @classmethod
    def match(cls, combination: Combination) -> bool:
        if len(combination) != 5:
            raise ValueError(f'{cls.__name__} needs the combination exactly 5-length. Got {len(combination)}')
        uniques = set(int(each) for each in combination)
        return len(uniques) == 2 and set(combination.count(each) for each in uniques) == {2, 3}


if __name__ == '__main__':
    assert 15 == Choice.measure(combination=(1, 2, 3, 4, 5))

    assert 0 == FourOfAKind.measure(combination=(1, 1, 1, 2, 2))
    assert 6 == FourOfAKind.measure(combination=(1, 1, 1, 1, 2))

    try:
        assert 3 == FullHouse.measure(combination=(1, 1, 1))
    except ValueError as e:
        print(f"Caught ValueError: {e}")
    assert 0 == FullHouse.measure(combination=(1, 1, 1, 1, 1))
    assert 7 == FullHouse.measure(combination=(1, 1, 1, 2, 2))


class ContainsTemplate(Category, Protocol):
    @classmethod
    @abc.abstractmethod
    def templates(cls) -> Tuple[Tuple[int, ...], ...]:
        return tuple()

    @classmethod
    def match(cls, combination: Combination) -> bool:
        for template in cls.templates():
            if all(combination.count(each) >= template.count(each) for each in set(template)):
                return True
        return False


if __name__ == '__main__':
    class MyTemplate(ContainsTemplate):
        @classmethod
        def _measure(cls, combination: Combination) -> int:
            return 42

        @classmethod
        def templates(cls) -> Tuple[Tuple[int, ...], ...]:
            return (1, 3, 1), (3, 2, 1)


    assert 42 == MyTemplate.measure((1, 2, 3))
    assert 0 == MyTemplate.measure((1, 1))
    assert 0 == MyTemplate.measure((1, 3))
    assert 42 == MyTemplate.measure((3, 1, 1))


class Straight(ContainsTemplate, Protocol):
    STRAIGHT_LENGTH = int(1e+10)

    @classmethod
    def templates(cls) -> Tuple[Tuple[int, ...], ...]:
        return tuple(tuple(range(start, start + cls.STRAIGHT_LENGTH)) for start in range(min(DICE_NUMBERS), max(DICE_NUMBERS) - cls.STRAIGHT_LENGTH + 2))


class SmallStraight(Straight):
    STRAIGHT_LENGTH = 4

    @classmethod
    def _measure(cls, combination: Combination) -> int:
        return 15


class LargeStraight(Straight):
    STRAIGHT_LENGTH = 5

    @classmethod
    def _measure(cls, combination: Combination) -> int:
        return 30


if __name__ == '__main__':
    assert 0 == SmallStraight.measure((1, 2, 2, 2, 2))
    assert 0 == SmallStraight.measure((1, 2, 3, 2, 2))
    assert 15 == SmallStraight.measure((1, 2, 3, 4, 2))
    assert 0 == SmallStraight.measure((2, 2, 2, 2, 2))
    assert 0 == SmallStraight.measure((2, 2, 3, 4, 2))
    assert 15 == SmallStraight.measure((2, 2, 3, 4, 5))


class Yacht(Category):
    @classmethod
    def match(cls, combination: Combination) -> bool:
        return 1 == len(set(int(each) for each in combination))

    @classmethod
    def _measure(cls, combination: Combination) -> int:
        return 50


if __name__ == '__main__':
    assert 0 == Yacht.measure((3, 3, 3, 3, 2))
    assert 50 == Yacht.measure((3, 3, 3, 3, 3))
    for _i in range(int(1e+10)):
        my_combination = rand_combination()
        if Yacht.measure(my_combination) == 50:
            print(f"Yacht! out of {_i} times. {my_combination}")
            break
        else:
            assert len(set(my_combination)) >= 2


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
    categories: ClassVar[Sequence[Category]] = Ones, Twos, Threes, Fours, Fives, Sixs

    def __init__(self):
        self.rows: Dict[Category, ScoreBoardRow] = dict()

    def add(self, combination: Combination, category: Category):
        if category in self.rows:
            raise ValueError(f"Category {category} already in self.rows.")
        self.rows[category] = ScoreBoardRow(combination=combination, category=category)

    @property
    def score(self):
        total_score = 0
        for row_category, row in self.rows.items():
            total_score += row.score
        return total_score

    @staticmethod
    def _summary_row(category: Category, row: Optional[ScoreBoardRow]) -> str:
        prefix = f"{category.__name__}: "
        if row is not None:
            if category != row.category:
                raise ValueError(f'self.rows category is not matching. {category} vs {row.category}')
            return prefix + f"{row.score} ({', '.join(map(str, sorted(row.combination)))})"
        else:
            return prefix

    @property
    def summary(self) -> str:
        summaries = [self._summary_row(category=category, row=self.rows.get(category)) for category in self.categories]
        return "\n".join(summaries)


if __name__ == '__main__':
    board = ScoreBoard()
    my_combination = (1, 1, 3, 5, 4)
    board.add(combination=my_combination, category=Ones)
    try:
        board.add(combination=(5, 5, 5, 5, 5), category=Ones)
    except ValueError as e:
        print(f'Caught ValueError: {e}')
    board.add(combination=(4, 4, 4, 4, 4), category=Fours)
    print(board.summary)

    board = ScoreBoard()
    board.add(combination=(1, 4, 1, 2, 1), category=Twos)
    board.add(combination=(1, 4, 1, 2, 1), category=Ones)
    try:
        board.add(combination=(1, 4, 1, 2, 5), category=Twos)
    except ValueError as e:
        print(f'Caught ValueError: {e}')
    board.add(combination=(5, 5, 5, 5, 5), category=Fours)
    print(board.summary)


class Game:
    pass
