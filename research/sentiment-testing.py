# Testing of 'vaderSentiment' and 'TextBlob' (flair didn't install)

sentences = [
    "Ridley Scott promises Apple he'll make another Gladiator and takes $200 million of their money to make a comedy about how much Napoleon sucks and what a weird loser he is. A legend. I bet the four-hour cut is gonna get at least an extra half star.",
]

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

analyzer = SentimentIntensityAnalyzer()
for sentence in sentences:
    vs = analyzer.polarity_scores(sentence)
    print(vs)
    # print("{:-<65} {}".format(sentence, str(vs)))

from textblob import TextBlob

review = TextBlob(sentences[0])
print(review.sentiment)
