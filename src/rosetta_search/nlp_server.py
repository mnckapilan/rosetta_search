import requests

localhost = "http://127.0.0.1:8000"


def get_nltk_wup_similarity(a: str, b: str) -> float:
    url = f"{localhost}/nltk/wup"
    response = requests.get(url, params={'a': a, 'b': b})
    return float(response.content.decode("utf-8"))


def get_similarities(a: str, b: str):
    url = f"{localhost}/similarity_scores"
    response = requests.get(url, params={'a': a, 'b': b})
    return response.json()
