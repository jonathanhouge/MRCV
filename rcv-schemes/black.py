# Black's Method - implemented by Jonathan Houge
# pyright: strict

from collections import Counter
from typing import Hashable, Iterator
import itertools

from common.types import Ballot, Result, Scheme
from common.shared_main import shared_main


# get all candidates
def total_candidates(ballots: list[Ballot]) -> list[Hashable]:
    candidates_set: set[Hashable] = set()
    for ballot in ballots:
        for candidate in ballot.ranking:
            candidates_set.add(candidate)

    return list(candidates_set)


# initialize pairwise comparison matrix with 0 in every entry
def matrix_creation(candidates: list[Hashable]) -> list[list[int]]:
    matrix: list[list[int]] = []
    for _ in range(0, len(candidates)):
        row: list[int] = []
        for _ in range(0, len(candidates)):
            row.append(0)
        matrix.append(row)

    return matrix


# find condorcet winner - winner will have wins == candidate count - 1
def condorcet_winner(candidates: list[Hashable], matrix: list[list[int]]) -> Hashable:
    winner: Hashable = None
    for i in range(0, len(candidates)):
        candidate_wins: list[int] = matrix[i]
        wins: int = sum(candidate_wins)
        if wins == len(candidates) - 1:
            winner = candidates[i]
            break

    return winner


# find condorcet winner, if there is one (used whenever a condorcet matrix is needed to be made)
def condorcet_calculator(ballots: list[Ballot]) -> Hashable:
    candidates: list[Hashable] = total_candidates(ballots)
    matrix: list[list[int]] = matrix_creation(candidates)

    combinations: Iterator[tuple[Hashable, ...]] = itertools.combinations(candidates, 2)
    for combination in combinations:
        votes: list[int] = [0, 0]
        for ballot in ballots:
            c1_present: int = ballot.ranking.count(combination[0])
            c2_present: int = ballot.ranking.count(combination[1])

            if c1_present and not c2_present:
                votes[0] += ballot.tally
            elif not c1_present and c2_present:
                votes[1] += ballot.tally
            elif c1_present and c2_present:
                c1_position: int = ballot.ranking.index(combination[0])
                c2_position: int = ballot.ranking.index(combination[1])
                if c1_position < c2_position:
                    votes[0] += ballot.tally
                elif c1_position > c2_position:
                    votes[1] += ballot.tally

        c1: int = candidates.index(combination[0])
        c2: int = candidates.index(combination[1])
        if votes[0] > votes[1]:
            matrix[c2][c1] = 0
            matrix[c1][c2] = 1
        elif votes[1] > votes[0]:
            matrix[c1][c2] = 0
            matrix[c2][c1] = 1
        else:
            matrix[c1][c2] = 0
            matrix[c2][c1] = 0

    return condorcet_winner(candidates, matrix)


# todd's borda
def borda(ballots: list[Ballot]) -> Result:
    size: int = len(set(c for ballot in ballots for c in ballot.ranking))
    points: list[int] = [c for c in range(size - 1, -1, -1)]
    scores: Counter[Hashable] = Counter()
    for ballot in ballots:
        for i, candidate in enumerate(ballot.ranking):
            scores[candidate] += points[i] * ballot.tally
    max_score: int = max(scores.values())
    winners: list[Hashable] = [
        candidate for candidate, score in scores.items() if score == max_score
    ]
    return winners[0], len(winners) == 1


def black(ballots: list[Ballot]) -> Result:
    condorcet_winner: Hashable = condorcet_calculator(ballots)

    if condorcet_winner is None:
        return borda(ballots)
    else:
        return condorcet_winner, True


scheme: Scheme = black
name: str = "Black"


def main() -> None:
    shared_main("black", scheme)


if __name__ == "__main__":
    main()
