import requests

localhost = "http://127.0.0.1:8000"


def get_nltk_wup_similarity(a: str, b: str) -> float:
    url = f"{localhost}/nltk/wup"
    response = requests.get(url, params={'a': a, 'b': b})
    return float(response.content.decode("utf-8"))


def get_similarity(a: str, b: str):
    url = f"{localhost}/ft_similarity"
    response = requests.get(url, params={'a': a, 'b': b})
    return float(response.content.decode("utf-8"))


if __name__ == '__main__':
    get_similarity("apple", "banana")
