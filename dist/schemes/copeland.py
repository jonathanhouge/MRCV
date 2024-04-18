# Copeland's Method - implemented by Jonathan Houge
# pyright: strict

from typing import Hashable, Iterator
from collections import defaultdict
import itertools

from common.shared_main import shared_main
from common.types import Ballot, Result, Scheme


# main function - takes ballots from generator.py
def copeland(ballots: list[Ballot]) -> Result:
    scores: defaultdict[Hashable, float] = defaultdict()
    candidates: set[Hashable] = set()
    for ballot in ballots:
        for candidate in ballot.ranking:
            candidates.add(candidate)
            scores[candidate] = 0  # set before incrementing later

    calculate(candidates, ballots, scores)

    # code from 'borda.py'
    max_score: float = max(scores.values())
    winners: list[Hashable] = [
        candidate for candidate, score in scores.items() if score == max_score
    ]

    return winners[0], len(winners) == 1


# calculate copeland score
def calculate(
    candidates: set[Hashable],
    ballots: list[Ballot],
    scores: defaultdict[Hashable, float],
) -> None:
    combinations: Iterator[tuple[Hashable, ...]] = itertools.combinations(candidates, 2)
    positions: list[int] = [0, 0]

    # copeland - pairwise faceoffs to determine how a point is assigned
    for combination in combinations:
        votes: list[int] = [0, 0]
        for ballot in ballots:
            positions[0] = get_index(ballot.ranking, combination[0])
            positions[1] = get_index(ballot.ranking, combination[1])

            if positions[0] >= 0 and (
                positions[1] == -1 or positions[0] < positions[1]
            ):
                votes[0] += ballot.tally
            elif positions[1] >= 0 and (
                (positions[0] == -1 or positions[1] < positions[0])
            ):
                votes[1] += ballot.tally

        # copeland - majority vote gets 1, tie splits the 1
        if votes[0] > votes[1]:
            scores[combination[0]] += 1.0
        elif votes[1] > votes[0]:
            scores[combination[1]] += 1.0
        elif votes[0] == votes[1]:
            scores[combination[0]] += 0.5
            scores[combination[1]] += 0.5


# find candidate in ranking, return index position
# '.index()', if not found, throws an error --> set to -1 (not found in other languages)
def get_index(ranking: tuple[Hashable, ...], candidate: Hashable) -> int:
    position: int
    try:
        position = ranking.index(candidate)
    except ValueError:
        position = -1

    return position


scheme: Scheme = copeland
name: str = "Copeland's Method"


def main():
    print(shared_main("copeland", scheme))


if __name__ == "__main__":
    main()
