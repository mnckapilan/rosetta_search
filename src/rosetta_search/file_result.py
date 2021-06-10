from rosetta_search.matched_token import MatchedToken


class FileResult:
    def __init__(self, filepath):
        self.filepath = filepath
        self.query_tokens = set()
        self.matched_tokens: list[MatchedToken] = []

    def __hash__(self):
        return hash(self.filepath)

    def __eq__(self, other):
        return isinstance(other, FileResult) and self.filepath == other.filepath

    def add_matched_token(self, matched_token, tf_idf):
        self.matched_tokens.append(MatchedToken(matched_token, tf_idf))

    def add_query_token(self, query_token):
        self.query_tokens.add(query_token)

    def __gt__(self, other):
        if len(self.query_tokens) > len(other.query_tokens):
            return True
        if len(self.query_tokens) < len(other.query_tokens):
            return False
        if sum(t.tf_idf for t in self.matched_tokens) > sum(t.tf_idf for t in other.matched_tokens):
            return True
        if sum(t.tf_idf for t in self.matched_tokens) < sum(t.tf_idf for t in other.matched_tokens):
            return False
