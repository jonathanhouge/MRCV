# Topmost Median Rank - implemented by Jonathan Houge
# pyright: strict

from statistics import mean
from collections import defaultdict
from typing import Hashable

from common.types import Ballot, Result, Scheme
from common.shared_main import shared_main


# get all candidates
def total_candidates(ballots: list[Ballot]) -> list[Hashable]:
    candidates_set: set[Hashable] = set()
    for ballot in ballots:
        for candidate in ballot.ranking:
            candidates_set.add(candidate)

    return list(candidates_set)


# get the ranks of all candidates
def calculate_ranks(
    ballots: list[Ballot], candidates: list[Hashable]
) -> defaultdict[Hashable, list[float]]:
    positions: list[int] = list(range(len(candidates)))
    ranks: defaultdict[Hashable, list[float]] = defaultdict()
    for candidate in candidates:
        ranks[candidate] = []

    for ballot in ballots:
        candidates_absent: list[Hashable] = candidates.copy()

        position: int = 0
        for i in range(0, len(ballot.ranking)):
            present: Hashable = ballot.ranking[i]
            candidates_absent.remove(present)
            ranks[present].extend([positions[i]] * ballot.tally)
            position += 1

        # all candidates absent from ballot get ranked the same
        if len(candidates_absent) != 0:
            average: float = mean(positions[position:])
            for absent in candidates_absent:
                ranks[absent].extend([average] * ballot.tally)

    for key, values in ranks.items():
        ranks[key] = sorted(values)

    return ranks


# pro (# of ranks below median) & opp (above median) difference
def typical_judgement(ranks: defaultdict[Hashable, list[float]]) -> list[Hashable]:
    winners: list[Hashable] = []
    max_difference: int | None = None
    for key, values in ranks.items():
        median_index: int = len(values) // 2
        median = values[median_index]

        # help from https://stackoverflow.com/a/15375122 - i am not good at generator expressions yet
        proponents: int = sum(value < median for value in values)
        opponents: int = sum(value > median for value in values)
        difference: int = proponents - opponents

        if max_difference is None or difference > max_difference:
            max_difference = difference
            winners = [key]
        elif max_difference == difference:
            winners.append(key)

    return winners


# main func - get cands & ranks, find max rank - if not unique, typical judgement
def topmost_median_rank(ballots: list[Ballot]) -> Result:
    candidates: list[Hashable] = total_candidates(ballots)
    ranks: defaultdict[Hashable, list[float]] = calculate_ranks(ballots, candidates)

    max_median_rank: float | None = None
    winners: list[Hashable] = []
    for key, values in ranks.items():
        median_index: int = len(values) // 2
        median = values[median_index]

        if max_median_rank is None or median < max_median_rank:
            max_median_rank = median
            winners = [key]
        elif median == max_median_rank:
            winners.append(key)

    # typical judgement - remove all non-contenders first
    if len(winners) != 0:
        for candidate in candidates:
            if candidate not in winners:
                ranks.pop(candidate)

        winners = typical_judgement(ranks)

    return winners[0], len(winners) == 1


scheme: Scheme = topmost_median_rank
name: str = "Topmost Median Rank"


def main() -> None:
    print(shared_main("topmost_median_rank", scheme))


if __name__ == "__main__":
    main()
