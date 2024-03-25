# Minimax: Winning Votes Variant - implemented by Jonathan Houge
# pyright: strict

from typing import Hashable, Iterator
from collections import defaultdict
import itertools

from common.shared_main import shared_main
from common.types import Ballot, Result, Scheme


# get all candidates
def total_candidates(ballots: list[Ballot]) -> list[Hashable]:
    candidates_set: set[Hashable] = set()
    for ballot in ballots:
        for candidate in ballot.ranking:
            candidates_set.add(candidate)

    return list(candidates_set)


# initialize pairwise comparison matrix with 0 in every entry
def matrix_creation(candidates: list[Hashable]) -> list[list[float]]:
    matrix: list[list[float]] = []
    for _ in range(0, len(candidates)):
        row: list[float] = []
        for _ in range(0, len(candidates)):
            row.append(0)
        matrix.append(row)

    return matrix


# create pairwise matrix - floats in-case of match-ups not equaling total votes
def pairwise_matrix_generation(ballots: list[Ballot]) -> list[list[float]]:
    candidates: list[Hashable] = total_candidates(ballots)
    matrix: list[list[float]] = matrix_creation(candidates)
    total_votes: int = sum(ballot.tally for ballot in ballots)

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

        if votes[0] + votes[1] != total_votes:
            leftover_votes: int = total_votes - votes[0] - votes[1]
            difference: float = leftover_votes / 2
            matrix[c2][c1] += difference
            matrix[c1][c2] += difference

        matrix[c1][c2] += votes[0]
        matrix[c2][c1] += votes[1]

    return matrix


# main function - makes pairwise matrix, finds the maximum loss,
def minimax(ballots: list[Ballot]) -> Result:
    pairwise_matrix: list[list[float]] = pairwise_matrix_generation(ballots)
    max_losses: defaultdict[Hashable, float] = defaultdict()
    candidates: list[Hashable] = total_candidates(ballots)

    for i in range(0, len(candidates)):
        candidate: Hashable = candidates[i]
        max_loss: float = 0

        # if candidate lost and that loss is greater than 'max_loss'
        for j in range(0, len(candidates)):
            if (
                pairwise_matrix[j][i] > pairwise_matrix[i][j]
                and pairwise_matrix[j][i] > max_loss
            ):
                max_loss = pairwise_matrix[j][i]
        max_losses[candidate] = max_loss

    min_score: float = min(max_losses.values())
    winners: list[Hashable] = [
        candidate for candidate, score in max_losses.items() if score == min_score
    ]

    return winners[0], len(winners) == 1


scheme: Scheme = minimax
name: str = "Minimax: Winning Votes Variant"


def main() -> None:
    shared_main("minimax", scheme)


if __name__ == "__main__":
    main()
