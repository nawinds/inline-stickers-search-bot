import numpy as np
from pyxdameraulevenshtein import normalized_damerau_levenshtein_distance_seqs
import string
from data.db_session import create_session, global_init
from data.search_data import SearchData
from difflib import SequenceMatcher


def summed_dict(lst: list):
    res = {}
    for i in lst:
        if i[0] in res.keys():
            res[i[0]] += i[1]
        else:
            res[i[0]] = i[1]
    return res


class Search:
    def __init__(self, q, user_id):
        self.q = self.clear_q(q)
        self.uid = user_id
        self.known_words = self.get_known_words()

    @property
    def results(self):
        return self.search_and_range()

    @property
    def corrected_q(self):
        res = []
        for word in self.q.split():
            res.append(self.correct_word(word))
        return " ".join(res) if res else None

    @staticmethod
    def clear_q(q):
        return q.strip().lower().translate(str.maketrans('', '', string.punctuation))

    @staticmethod
    def similarity_rate(a, b):
        return SequenceMatcher(None, a, b).ratio()

    def get_known_words(self):
        with open("known_words.txt", encoding="utf-8") as known_words_file:
            known_words = known_words_file.read().strip().split()
        return known_words

    def correct_word(self, word):
        array = np.array(self.known_words)
        result = list(zip(self.known_words,
                          list(normalized_damerau_levenshtein_distance_seqs(word, array))))
        corrected_word, rate = min(result, key=lambda x: x[1])
        if rate > 0.4:
            return word
        return corrected_word

    def search_list(self):
        return list(zip(
            [self.q, self.corrected_q] + self.q.split() + self.corrected_q.split(),
            [len(self.q.split()), len(self.corrected_q.split()) / 2] +
            [1] * len(self.q) + [0.5] * len(self.corrected_q)
        ))

    def search_term(self, term, k=1):
        session = create_session()
        found = session.query(SearchData).filter(SearchData.user_id == self.uid,
                                                 SearchData.keyword.like(f"%{term}%")).all()
        return [(res.sticker_id, res.use / 20 +
                 k * self.similarity_rate(term, res.keyword) / res.sticker_count) for res in found]

    def search_and_range(self):
        results = []
        for term, k in self.search_list():
            results += self.search_term(term, k)
        results = summed_dict(results)
        results = {results[key]: key for key in results.keys()}
        return [results[r] for r in sorted(results.keys(), reverse=True)]


global_init("data/db/main.db")
# session = create_session()
# session.add(SearchData(user_id=1, sticker_id=1, sticker_count=3, keyword="привет", use=0))
# session.add(SearchData(user_id=1, sticker_id=1, sticker_count=3, keyword="как дела", use=0))
# session.add(SearchData(user_id=1, sticker_id=1, sticker_count=3, keyword="так дела привет", use=0))
# session.add(SearchData(user_id=1, sticker_id=2, sticker_count=3, keyword="привет кfк дела", use=0))
# session.add(SearchData(user_id=1, sticker_id=2, sticker_count=3, keyword="дела", use=0))
# session.add(SearchData(user_id=1, sticker_id=2, sticker_count=3, keyword="так вот", use=0))
# session.add(SearchData(user_id=1, sticker_id=3, sticker_count=1, keyword="привет", use=0))
# session.commit()
print(Search("привет", user_id=1).results)
