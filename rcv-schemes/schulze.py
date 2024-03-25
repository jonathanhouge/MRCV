# Schulze's Method - implemented by Jonathan Houge
# pyright: strict

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


# initialize matrix with 0 in every entry
def matrix_creation(candidates: list[Hashable]) -> list[list[int]]:
    matrix: list[list[int]] = []
    for _ in range(0, len(candidates)):
        row: list[int] = []
        for _ in range(0, len(candidates)):
            row.append(0)
        matrix.append(row)

    return matrix


# create matrix of edges - just keep track of heaviest weights b/w comparisons
def heaviest_edges_generation(ballots: list[Ballot]) -> list[list[int]]:
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
            matrix[c1][c2] = votes[0]
        elif votes[1] > votes[0]:
            matrix[c2][c1] = votes[1]

    return matrix


# make a graph from the edges
def directed_graph_generation(edges: list[list[int]]) -> defaultdict[int, list[int]]:
    directed_graph: defaultdict[int, list[int]] = defaultdict()
    for i in range(0, len(edges)):
        for j in range(0, len(edges[0])):
            if edges[i][j] == 0:
                continue

            if i in directed_graph:
                directed_graph[i].append(j)
            else:
                directed_graph[i] = [j]

    return directed_graph


# find a condorcet winner or strongest edge path
def find_winner(graph: defaultdict[int, list[int]], ballots: list[Ballot]) -> int:
    candidates: list[Hashable] = total_candidates(ballots)
    condorcet: int = -1

    # a condorcet winner would have every candidate in their edgelist
    for key in graph.keys():
        potential_condorcet: int = key
        if len(graph[potential_condorcet]) == len(candidates) - 1:
            condorcet = potential_condorcet
            break

    if condorcet != -1:
        return condorcet

    # TODO find strongest path if no condorcet winner

    return -1


def schulze(ballots: list[Ballot]) -> Result:
    matrix: list[list[int]] = heaviest_edges_generation(ballots)
    graph: defaultdict[int, list[int]] = directed_graph_generation(matrix)
    winner_index: int

    if len(graph) == 1:
        winner_index = list(graph.keys())[0]
        return total_candidates(ballots)[winner_index], True

    winner_index = find_winner(graph, ballots)

    # -1 if no winner (tie), otherwise grab it
    winner: Hashable = (
        None if winner_index == -1 else total_candidates(ballots)[winner_index]
    )

    return winner, winner is not None


scheme: Scheme = schulze
name: str = "Schulze's Method"


def main() -> None:
    shared_main("schulze", scheme)


if __name__ == "__main__":
    main()
