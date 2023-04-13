import nltk
from textblob import TextBlob
from utils import current_milli_time
from protos import benchmark_pb2 as pb2

# nltk.download('punkt')


def analyze_sentiment(request, request_received_time_ms):
    blob = TextBlob(request.input_text)
    res = {
        "polarity": 0,
        "subjectivity": 0
    }

    for sentence in blob.sentences:
        res["subjectivity"] = res["subjectivity"] + sentence.sentiment.subjectivity
        res["polarity"] = res["polarity"] + sentence.sentiment.polarity

    total = len(blob.sentences)

    res["sentence_count"] = total
    res["polarity"] = res["polarity"] / total
    res["subjectivity"] = res["subjectivity"] / total

    analysis_response = pb2.SentimentAnalysisResponse()
    analysis_response.sentence_count = total
    analysis_response.polarity = res["polarity"]
    analysis_response.subjectivity = res["subjectivity"]
    analysis_response.request_time_ms = request.request_time_ms
    analysis_response.request_received_time_ms = request_received_time_ms
    analysis_response.response_time_ms = current_milli_time()

    return analysis_response
