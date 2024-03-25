# Coombs' Method - implemented by Jonathan Houge
# pyright: strict

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


# count all votes - make sure those that have zero are counted too
# 'i' is index of 'ballot.ranking' to attribute points to - first or last (0 or -1)
def count_votes(
    candidates: list[Hashable], ballots: list[Ballot], i: int
) -> defaultdict[Hashable, float]:
    votes: defaultdict[Hashable, float] = defaultdict()
    for candidate in candidates:
        votes[candidate] = 0

    for ballot in ballots:
        if ballot.tally == 0:
            continue

        # if all candidates aren't present, split vote between those left off
        if len(ballot.ranking) != len(candidates) and i == -1:
            left_off: list[Hashable] = list(set(candidates) - set(ballot.ranking))
            amount: float = ballot.tally / len(left_off)
            for off in left_off:
                votes[off] += amount
        else:
            winner: Hashable = ballot.ranking[i]
            votes[winner] += ballot.tally

    return votes


# remove coombs loser from 'ballot.ranking'
def remove_loser(
    candidates: list[Hashable], ballots: list[Ballot], loser: Hashable
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


# coombs - irv but remove those with highest last place votes
def coombs(ballots: list[Ballot]) -> Result:
    candidates: list[Hashable] = total_candidates(ballots)

    winners: list[Hashable]
    losers: list[Hashable]

    while True:
        total_votes: int = sum(ballot.tally for ballot in ballots)
        majority: float = total_votes * 0.5
        first: defaultdict[Hashable, float] = count_votes(candidates, ballots, 0)

        # check if someone has majority first place votes
        highest: float = max(first.values())
        winners = [candidate for candidate, score in first.items() if score == highest]
        if float(highest) > majority and len(winners) == 1:
            break

        # no one has majority so find who has majority last place votes
        last: defaultdict[Hashable, float] = count_votes(candidates, ballots, -1)
        highest = max(last.values())
        losers = [candidate for candidate, score in last.items() if score == highest]

        # tie for last, someone loses, tie for first
        if len(losers) > 1:
            winners = losers
            break
        elif len(losers) == 1:
            ballots = remove_loser(candidates, ballots, losers[0])
        elif len(winners) > 1:
            break

    return winners[0], len(winners) == 1


scheme: Scheme = coombs
name: str = "Coombs Method"


def main() -> None:
    shared_main("coombs", scheme)


if __name__ == "__main__":
    main()
