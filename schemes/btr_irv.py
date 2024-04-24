# Bottom-Two-Runoff IRV - implemented by Jonathan Houge
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
        if ballot.ranking:
            winner: Hashable = ballot.ranking[0]
            votes[winner] += ballot.tally

    return votes


def face_off(ballots: list[Ballot], losers: list[Hashable]) -> Hashable:
    votes: list[int] = [0, 0]
    for ballot in ballots:
        c1_present: int = ballot.ranking.count(losers[0])
        c2_present: int = ballot.ranking.count(losers[1])

        if c1_present and not c2_present:
            votes[0] += ballot.tally
        elif not c1_present and c2_present:
            votes[1] += ballot.tally
        elif c1_present and c2_present:
            c1_position: int = ballot.ranking.index(losers[0])
            c2_position: int = ballot.ranking.index(losers[1])
            if c1_position < c2_position:
                votes[0] += ballot.tally
            elif c1_position > c2_position:
                votes[1] += ballot.tally

    if votes[0] > votes[1]:
        return losers[1]
    elif votes[1] > votes[0]:
        return losers[0]
    else:
        return -1


# remove btr_irv loser from 'ballot.ranking'
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


def btr_irv(ballots: list[Ballot]) -> Result:
    candidates: list[Hashable] = total_candidates(ballots)

    winners: list[Hashable]
    losers: list[Hashable]

    while True:
        total_votes: int = sum(ballot.tally for ballot in ballots)
        majority: float = total_votes * 0.5
        votes: Counter[Hashable] = count_votes(candidates, ballots)

        votes_ascending: list[int] = list(votes.values())
        votes_ascending.sort()

        highest: int = votes_ascending[-1]
        winners = [candidate for candidate, score in votes.items() if score == highest]

        lowest: int = votes_ascending[0]
        second_lowest: int = votes_ascending[1]
        losers = [
            candidate
            for candidate, score in votes.items()
            if score == lowest or score == second_lowest
        ]

        # someone has majority, tie for last, someone loses, tie for first
        if float(highest) > majority and len(winners) == 1:
            break
        elif len(losers) > 2:
            winners = losers
            break
        elif len(losers) == 2:
            loser: Hashable = face_off(ballots, losers)
            if loser == -1:
                winners = losers
                break
            ballots = remove_loser(candidates, ballots, loser)
        elif len(winners) > 1:
            break

    return winners[0], len(winners) == 1


scheme: Scheme = btr_irv
name: str = "Bottom-Two-Runoff IRV"


def main() -> None:
    print(shared_main("btr_irv", scheme))


if __name__ == "__main__":
    main()
