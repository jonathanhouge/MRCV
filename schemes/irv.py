# IRV - implemented by Jonathan Houge
# pyright: strict

from collections import Counter
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
def count_votes(candidates: list[Hashable], ballots: list[Ballot]) -> Counter[Hashable]:
    votes: Counter[Hashable] = Counter()
    for candidate in candidates:
        votes[candidate] = 0

    for ballot in ballots:
        winner: Hashable = ballot.ranking[0]
        votes[winner] += ballot.tally

    return votes


# remove irv loser from 'ballot.ranking'
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


def irv(ballots: list[Ballot]) -> Result:
    candidates: list[Hashable] = total_candidates(ballots)

    winners: list[Hashable]
    losers: list[Hashable]

    while True:
        total_votes: int = sum(ballot.tally for ballot in ballots)
        majority: float = total_votes * 0.5
        votes: Counter[Hashable] = count_votes(candidates, ballots)

        highest: int = max(votes.values())
        winners = [candidate for candidate, score in votes.items() if score == highest]

        lowest: int = min(votes.values())
        losers = [candidate for candidate, score in votes.items() if score == lowest]

        # someone has majority, tie for last, someone loses, tie for first
        if float(highest) > majority and len(winners) == 1:
            break
        elif len(losers) > 1:
            winners = losers
            break
        elif len(losers) == 1:
            ballots = remove_loser(candidates, ballots, losers[0])
        elif len(winners) > 1:
            break

    return winners[0], len(winners) == 1


scheme: Scheme = irv
name: str = "IRV"


def main() -> None:
    print(shared_main("irv", scheme))


if __name__ == "__main__":
    main()
