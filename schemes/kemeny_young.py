# Kemeny Young - implemented by Jonathan Houge
# pyright: strict

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


# create summary matrix (used whenever a condorcet matrix is needed to be made)
def summary_matrix_generator(
    ballots: list[Ballot], candidates: list[Hashable]
) -> list[list[int]]:
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

        matrix[c1][c2] = votes[0]
        matrix[c2][c1] = votes[1]

    return matrix


# evaluate summary matrix, return winner of the best permutation
def summary_matrix_resolver(
    matrix: list[list[int]], candidates: list[Hashable]
) -> Hashable:
    winner: Hashable = -1
    winning_score: int = 0
    permutations: list[tuple[Hashable, ...]] = list(itertools.permutations(candidates))

    for permutation in permutations:
        current_score: int = 0
        i: int = 1
        for prefer in permutation[: len(permutation) - 1]:
            for over in permutation[i:]:
                prefer_index: int = candidates.index(prefer)
                over_index: int = candidates.index(over)
                current_score += matrix[prefer_index][over_index]
            i += 1

        # either we have a new winner or two candidates are tying
        if current_score > winning_score:
            winning_score = current_score
            winner = permutation[0]
        elif current_score == winning_score and winner != permutation[0]:
            winner = -1

    return winner


# kemeny_young main function
def kemeny_young(ballots: list[Ballot]) -> Result:
    candidates: list[Hashable] = total_candidates(ballots)
    summary_matrix: list[list[int]] = summary_matrix_generator(ballots, candidates)
    winner: Hashable = summary_matrix_resolver(summary_matrix, candidates)

    if winner == -1:
        return None, False
    return winner, True


scheme: Scheme = kemeny_young
name: str = "Kemeny Young"


def main() -> None:
    print(shared_main("kemeny_young", scheme))


if __name__ == "__main__":
    main()
