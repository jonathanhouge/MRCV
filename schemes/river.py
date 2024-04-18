# River Algorithm - implemented by Jonathan Houge
# i am not proud of this code
# pyright: strict

import math
from typing import Hashable, Iterator
import itertools
from collections import defaultdict

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


# create symmetric matrix - no need to find pairwise if we just use that to find symmetric
def symmetric_matrix_generation(ballots: list[Ballot]) -> list[list[int]]:
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

        matrix[c1][c2] = votes[0] - votes[1]
        matrix[c2][c1] = votes[1] - votes[0]

    return matrix


# multiple potential arcs found - if there are two legal ones, it's a tie.
# returns the singular legal arc if there is one, -1 if there's a tie, and -2 if all were illegal.
def multiple_arcs(
    matrix: list[list[int]],
    graph: defaultdict[int, list[int]],
    highest: int,
    lowest: int,
    results: list[int],
) -> int:
    legal: int = -2

    for i in range(0, len(results)):
        result: int = results[i]
        if result == 0:
            continue

        row: list[int] = matrix[i]
        arcs: list[int] = [i for i in range(len(row)) if row[i] == highest]

        for arc in arcs:
            legality: bool = legality_check(graph, arc, i)
            if legality and legal == -2:
                legal = i
            elif legality:
                return -1
            else:
                matrix[i][arc] = lowest - 1

    return legal


# check arc legality - no cycles, single parent
def legality_check(
    directed_graph: defaultdict[int, list[int]], lost: int, won: int
) -> bool:
    possibleCycle: int = 0
    for key, values in directed_graph.items():
        for value in values:
            if lost == value:
                return False
            elif won == value:
                possibleCycle += 1
        if lost == key:
            possibleCycle += 1

    if possibleCycle > 2:
        return False
    return True


def handle_winner(
    root: int, won: int, lost: int, directed_graph: defaultdict[int, list[int]]
) -> int:
    if root == -1:
        root = won
    elif lost == root:
        root = won

    if won in directed_graph:
        directed_graph[won].append(lost)
    else:
        directed_graph[won] = [lost]

    return root


# find the highest symmetry, put in the graph, repeat
# end if a legal arc tie is found, all possible arcs are found, zero is the
# highest found value, or all estimated positives have been explored
def directed_graph(symmetric_matrix: list[list[int]]) -> int:
    root: int = -1
    num_cans: int = len(symmetric_matrix[0])
    directed_graph: defaultdict[int, list[int]] = defaultdict()
    arc_count: int = 0

    lowest: int = min(list(min(row) for row in symmetric_matrix))
    max_positive_values: int = math.ceil((num_cans * num_cans) / 2)
    for _ in range(0, max_positive_values):
        highest: int = max(list(max(row) for row in symmetric_matrix))

        if highest == lowest - 1:
            break

        won: int
        results: list[int] = list(row.count(highest) for row in symmetric_matrix)
        if sum(results) > 1 or results.count(1) > 1:
            if root == -1:
                break  # legal arc tie - we're done

            won = multiple_arcs(
                symmetric_matrix, directed_graph, highest, lowest, results
            )

            if won == -1:
                root = -1  # legal arc tie - we're done
                break
            elif won == -2:
                continue  # all arcs were illegal - let's check out the next ones
        else:
            won = results.index(1)

        lost: int = symmetric_matrix[won].index(highest)
        symmetric_matrix[won][lost] = lowest - 1

        if not legality_check(directed_graph, lost, won):
            continue  # illegal arc

        root = handle_winner(root, won, lost, directed_graph)

        arc_count += 1
        if arc_count == num_cans - 1:
            break  # all arcs found - end

    return root


def river(ballots: list[Ballot]) -> Result:
    symmetric_matrix: list[list[int]] = symmetric_matrix_generation(ballots)
    winner_index: int = directed_graph(symmetric_matrix)

    # -1 if no winner (tie), otherwise grab it
    winner: Hashable = (
        None if winner_index == -1 else total_candidates(ballots)[winner_index]
    )

    return winner, winner is not None


scheme: Scheme = river
name: str = "River"


def main() -> None:
    print(shared_main("river", scheme))


if __name__ == "__main__":
    main()
