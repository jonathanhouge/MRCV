# TODO - incomplete
# Single Transferrable Vote - implemented by Jonathan Houge
# pyright: strict

from collections import Counter
from typing import Hashable
from math import floor

from common.types import Ballot, Result, Scheme
from common.shared_main import shared_main


# get all candidates
def total_candidates(ballots: list[Ballot]) -> list[Hashable]:
    candidates_set: set[Hashable] = set()
    for ballot in ballots:
        for candidate in ballot.ranking:
            candidates_set.add(candidate)

    return list(candidates_set)


# count all votes - make sure those that have zero are counted too
def count_votes(candidates: list[Hashable], ballots: list[Ballot]) -> Counter[Hashable]:
    votes: Counter[Hashable] = Counter()
    for candidate in candidates:
        votes[candidate] = 0

    for ballot in ballots:
        if ballot.ranking:
            winner: Hashable = ballot.ranking[0]
            votes[winner] += ballot.tally

    return votes


# remove stv loser from 'ballot.ranking'
# TODO - redistribute votes
def remove(
    candidates: list[Hashable], votes: int, ballots: list[Ballot], loser: Hashable
) -> list[Ballot]:
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

    candidates.remove(loser)
    return new_ballots


def stv(ballots: list[Ballot]) -> Result:
    candidates: list[Hashable] = total_candidates(ballots)

    stv_winners: list[Hashable] = []
    winners: list[Hashable] = []
    losers: list[Hashable]
    total_votes: int = sum(ballot.tally for ballot in ballots)
    droop_quota: int = floor((total_votes / (5 + 1))) + 1

    while len(stv_winners) < 5:
        votes: Counter[Hashable] = count_votes(candidates, ballots)

        winners = [
            candidate for candidate, score in votes.items() if score >= droop_quota
        ]

        lowest: int = min(votes.values())
        losers = [candidate for candidate, score in votes.items() if score == lowest]

        # someone has majority, tie for last, someone loses, tie for first
        if len(winners) != 0:
            for winner in winners:
                ballots = remove(candidates, votes[winner], ballots, winner)
                stv_winners.append(winner)
        elif len(losers) > 1:
            winners = losers
            break
        elif len(losers) == 1:
            ballots = remove(candidates, 0, ballots, losers[0])
        elif len(winners) > 1:
            break

    return winners[0], len(winners) == 1


scheme: Scheme = stv
name: str = "Single Transferrable Vote"


def main() -> None:
    print(shared_main("stv", scheme))


if __name__ == "__main__":
    main()
