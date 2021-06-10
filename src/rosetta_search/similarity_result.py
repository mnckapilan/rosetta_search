from rosetta_search.nlp_server import get_similarity


class SimilarityResult:
    def __init__(self, query_token, matched_token, matched_token_id):
        self.query_token = query_token
        self.matched_token = matched_token
        self.matched_token_id = matched_token_id
        self.similarity = get_similarity(self.query_token, self.matched_token)
