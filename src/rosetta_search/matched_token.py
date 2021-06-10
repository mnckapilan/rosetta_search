class MatchedToken:
    def __init__(self, token, tf_idf):
        self.token: str = token
        self.tf_idf: float = tf_idf
