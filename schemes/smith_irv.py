# Woodall's Method / Smith IRV - implemented by Jonathan Houge
# pyright: strict

from typing import Hashable, Iterator
from collections import defaultdict, Counter
import itertools

from common.shared_main import shared_main
from common.types import Ballot, Result, Scheme


# my copeland - uses 'calculate_copeland', 'copeland_count_votes', 'get_index', and 'add_to_smith_set'
# modified to calculate the full smith set - if no condorcet winner
def copeland(ballots: list[Ballot]) -> list[Hashable]:
    scores: defaultdict[Hashable, float] = defaultdict()
    candidates: set[Hashable] = set()
    for ballot in ballots:
        for candidate in ballot.ranking:
            candidates.add(candidate)
            scores[candidate] = 0  # set before incrementing later

    calculate_copeland(candidates, ballots, scores)

    # code from 'borda.py'
    max_score: float = max(scores.values())
    winners: list[Hashable] = [
        candidate for candidate, score in scores.items() if score == max_score
    ]

    # modification - redo copeland score for every smith set entry
    if max_score != len(candidates) - 1:
        i: int = 0
        while i < len(winners):
            calculate_copeland(candidates, ballots, scores, winners, i)
            i += 1

    return winners


# modified calculate copeland score - optional arguments to complete smith set
def calculate_copeland(
    candidates: set[Hashable],
    ballots: list[Ballot],
    scores: defaultdict[Hashable, float],
    smith_set: list[Hashable] = [],
    smith_set_index: int = 0,
) -> None:
    combinations: Iterator[tuple[Hashable, ...]] = itertools.combinations(candidates, 2)
    positions: list[int] = [0, 0]

    # copeland - pairwise faceoffs to determine how a point is assigned
    for combination in combinations:
        votes: list[int] = [0, 0]

        # only evaluate those that are going against the current smith_set index
        if len(smith_set) != 0 and smith_set[smith_set_index] not in combination:
            continue

        copeland_count_votes(ballots, combination, positions, votes)

        # copeland - majority vote gets 1, tie splits the 1
        if votes[0] > votes[1]:
            scores[combination[0]] += 1.0

            add_to_smith_set(smith_set, combination[0])
        elif votes[1] > votes[0]:
            scores[combination[1]] += 1.0

            add_to_smith_set(smith_set, combination[1])
        elif votes[0] == votes[1]:
            scores[combination[0]] += 0.5
            scores[combination[1]] += 0.5

            add_to_smith_set(smith_set, combination[0])
            add_to_smith_set(smith_set, combination[1])


# NEW - used when creating smith set
def add_to_smith_set(smith_set: list[Hashable], candidate: Hashable) -> None:
    if len(smith_set) == 0:
        return
    elif candidate not in smith_set:
        smith_set.append(candidate)


# calculate pairwise match-up
def copeland_count_votes(
    ballots: list[Ballot],
    combination: tuple[Hashable, ...],
    positions: list[int],
    votes: list[int],
) -> None:
    for ballot in ballots:
        positions[0] = get_index(ballot.ranking, combination[0])
        positions[1] = get_index(ballot.ranking, combination[1])

        if positions[0] >= 0 and (positions[1] == -1 or positions[0] < positions[1]):
            votes[0] += ballot.tally
        elif positions[1] >= 0 and (
            (positions[0] == -1 or positions[1] < positions[0])
        ):
            votes[1] += ballot.tally


# find candidate in ranking, return index position
# '.index()', if not found, throws an error --> set to -1 (not found in other languages)
def get_index(ranking: tuple[Hashable, ...], candidate: Hashable) -> int:
    position: int
    try:
        position = ranking.index(candidate)
    except ValueError:
        position = -1

    return position


# get all candidates
def total_candidates(ballots: list[Ballot]) -> list[Hashable]:
    candidates_set: set[Hashable] = set()
    for ballot in ballots:
        for candidate in ballot.ranking:
            candidates_set.add(candidate)

    return list(candidates_set)


# count all votes - make sure those that have zero are counted too
def irv_count_votes(
    candidates: list[Hashable], ballots: list[Ballot]
) -> Counter[Hashable]:
    votes: Counter[Hashable] = Counter()
    for candidate in candidates:
        votes[candidate] = 0

    for ballot in ballots:
        winner: Hashable = ballot.ranking[0]
        votes[winner] += ballot.tally

    return votes


# remove irv loser from 'ballot.ranking'
def remove_loser(ballots: list[Ballot], loser: Hashable) -> list[Ballot]:
    new_ballots: list[Ballot] = []
    for ballot in ballots:
        if loser in ballot.ranking:
            temporary: list[Hashable] = list(ballot.ranking)
            temporary.remove(loser)
            if len(temporary) != 0:
                new_ballot: Ballot = Ballot(tuple(temporary), ballot.tally)
                new_ballots.append(new_ballot)
        else:
            new_ballots.append(ballot)

    return new_ballots


# my irv - uses 'remove_loser', 'irv_count_votes', and 'total_candidates'
# modified to elect a candidate of the smith set
def irv(ballots: list[Ballot], smith_set: list[Hashable]) -> Result:
    candidates: list[Hashable] = total_candidates(ballots)

    winners: list[Hashable]
    losers: list[Hashable]

    while True:
        votes: Counter[Hashable] = irv_count_votes(candidates, ballots)

        highest: int = max(votes.values())
        winners = [candidate for candidate, score in votes.items() if score == highest]

        lowest: int = min(votes.values())
        losers = [candidate for candidate, score in votes.items() if score == lowest]

        # tie for last, someone loses and there's only one left in the smith set, tie for first
        if len(losers) > 1:
            winners = losers
            break
        elif len(losers) == 1:
            ballots = remove_loser(ballots, losers[0])
            candidates.remove(losers[0])

            if losers[0] in smith_set:
                smith_set.remove(losers[0])
            if len(smith_set) == 1:
                break
        elif len(winners) > 1:
            break

    return smith_set[0], len(smith_set) == 1


# main - calculate smith_set with copeland, run irv if needed
def smith_irv(ballots: list[Ballot]) -> Result:
    smith_set: list[Hashable] = copeland(ballots)
    if len(smith_set) == 1:
        return smith_set[0], len(smith_set) == 1

    return irv(ballots, smith_set)


scheme: Scheme = smith_irv
name: str = "Smith IRV: Woodall's Method"


def main() -> None:
    print(shared_main("smith_irv", scheme))


if __name__ == "__main__":
    main()
