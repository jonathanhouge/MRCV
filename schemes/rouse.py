# Rouse's Method - implemented by Jonathan Houge
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


# todd's borda - modified to be the 'average' method
def borda(ballots: list[Ballot]) -> list[Hashable]:
    unmentioned_candidates: list[Hashable]
    size: int = len(set(c for ballot in ballots for c in ballot.ranking))
    points: list[int] = [c for c in range(size - 1, -1, -1)]

    scores: defaultdict[Hashable, float] = defaultdict()
    for candidate in total_candidates(ballots):
        scores[candidate] = 0

    for ballot in ballots:
        if ballot.tally == 0:
            continue

        unmentioned_candidates = total_candidates(ballots)
        unmentioned_index: int = 0

        for i, candidate in enumerate(ballot.ranking):
            scores[candidate] += points[i] * ballot.tally
            unmentioned_candidates.remove(candidate)
            unmentioned_index = i

        # divide remaining points equally amongst the unmentioned candidates
        if len(unmentioned_candidates) != 0:
            unmentioned_points: float = 0
            for remaining in points[unmentioned_index + 1 :]:
                unmentioned_points += (
                    remaining * ballot.tally / len(unmentioned_candidates)
                )

            for unmentioned_candidate in unmentioned_candidates:
                scores[unmentioned_candidate] += unmentioned_points

    max_score: float = max(scores.values())
    winners: list[Hashable] = [
        candidate for candidate, score in scores.items() if score == max_score
    ]

    return winners


# modified candidate removal from irv - remove candidate, either temporarily or permanently
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


# rouse's method main - call borda as long as more than one candidate exists
def rouse(ballots: list[Ballot]) -> Result:
    num_candidates: int = len(set(c for ballot in ballots for c in ballot.ranking))
    bucket: list[Hashable]

    while num_candidates > 1:
        bucket = []
        temp_ballots: list[Ballot] = ballots.copy()
        while len(bucket) != num_candidates - 1:
            bucket_candidate: list[Hashable] = borda(temp_ballots)
            if len(bucket_candidate) != 1:
                return None, False  # more than one winner

            # winner has immunity, remove them temporarily
            bucket.append(bucket_candidate[0])
            temp_ballots = remove_loser(temp_ballots, bucket_candidate[0])

        # remove the candidate not in the bucket permanently
        ballots = remove_loser(ballots, temp_ballots[0].ranking[0])

        num_candidates -= 1

    winners: list[Hashable] = list(set(c for ballot in ballots for c in ballot.ranking))
    return winners[0], len(winners) == 1


scheme: Scheme = rouse
name: str = "Rouse's Method"


def main() -> None:
    print(shared_main("rouse", scheme))


if __name__ == "__main__":
    main()
