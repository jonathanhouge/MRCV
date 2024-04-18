# Bucklin Voting - implemented by Jonathan Houge
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


# count votes for the passed in ranking index - accounts for incompletes
def count_votes(votes: Counter[Hashable], ballots: list[Ballot], index: int) -> None:
    for ballot in ballots:
        if index < len(ballot.ranking):
            winner: Hashable = ballot.ranking[index]
            votes[winner] += ballot.tally


# bucklin main - iterate through ballots, index at a time
def bucklin(ballots: list[Ballot]) -> Result:
    candidates: list[Hashable] = total_candidates(ballots)
    winners: list[Hashable] = []

    total_votes: int = sum(ballot.tally for ballot in ballots)
    majority: float = total_votes * 0.5

    votes: Counter[Hashable] = Counter()
    for i in range(0, len(candidates)):
        count_votes(votes, ballots, i)

        highest: int = max(votes.values())
        winners = [candidate for candidate, score in votes.items() if score == highest]

        # someone has majority
        if float(highest) > majority:
            break

    return winners[0], len(winners) == 1


scheme: Scheme = bucklin
name: str = "Bucklin Voting"


def main() -> None:
    print(shared_main("bucklin", scheme))


if __name__ == "__main__":
    main()
