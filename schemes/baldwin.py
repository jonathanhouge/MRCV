# Baldwin's Method - implemented by Jonathan Houge
# pyright: strict

from collections import Counter
from typing import Hashable

from common.types import Ballot, Result, Scheme
from common.shared_main import shared_main


# todd's borda - modifed to calculate average and return candidates at or below
def borda(ballots: list[Ballot]) -> list[Hashable]:
    size: int = max(len(ballot.ranking) for ballot in ballots)  # different
    points: list[int] = [c for c in range(size - 1, -1, -1)]
    scores: Counter[Hashable] = Counter()
    for ballot in ballots:
        for i, candidate in enumerate(ballot.ranking):
            scores[candidate] += points[i] * ballot.tally

    min_score: int = min(scores.values())
    losers: list[Hashable] = [
        candidate for candidate, score in scores.items() if score == min_score
    ]

    return losers


# modified candidate removal from irv - remove candidate with lowest borda score
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


# baldwin's method main - call borda as long as more than one candidate exists
def baldwin(ballots: list[Ballot]) -> Result:
    num_candidates: int = len(set(c for ballot in ballots for c in ballot.ranking))
    to_eliminate: list[Hashable] = []
    while num_candidates > 1:
        to_eliminate = borda(ballots)

        # tie - for first or last
        if len(to_eliminate) == num_candidates or len(to_eliminate) > 1:
            break

        ballots = remove_loser(ballots, to_eliminate[0])

        num_candidates -= len(to_eliminate)

    winners: list[Hashable] = list(set(c for ballot in ballots for c in ballot.ranking))
    return winners[0], len(winners) == 1


scheme: Scheme = baldwin
name: str = "Baldwin's Method"


def main() -> None:
    print(shared_main("baldwin", scheme))


if __name__ == "__main__":
    main()
