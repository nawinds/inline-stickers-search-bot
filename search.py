import numpy as np
from pyxdameraulevenshtein import normalized_damerau_levenshtein_distance_seqs
import string
from data.db_session import create_session
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


def clear_q(q):
    return q.strip().lower().translate(str.maketrans('', '', string.punctuation))


class Search:
    def __init__(self, q, user_id):
        self.q = q.lower()
        self.uid = user_id
        self.known_words = self.get_known_words()

    def get_results(self):
        return self.search_and_range()

    @property
    def corrected_q(self):
        res = []
        for orig_word in self.q.split():
            word = clear_q(orig_word)
            if word.lower() in self.known_words:
                res.append(word)
            else:
                corrected = self.correct_word(word)
                if corrected in self.known_words:
                    res.append(corrected)
                else:
                    if 97 <= any([ord(i) for i in word]) <= 122:
                        fixed_lang = clear_q(self.en_to_ru_keyboard(orig_word))
                    elif 1072 <= any([ord(i) for i in word]) <= 1103:
                        fixed_lang = clear_q(self.ru_to_en_keyboard(orig_word))
                    else:
                        fixed_lang = word
                    if fixed_lang in self.known_words:
                        res.append(fixed_lang)
                    else:
                        print(12)
                        res.append(self.correct_word(fixed_lang))
        return " ".join(res) if res else None

    @staticmethod
    def en_to_ru_keyboard(text):
        layout = dict(zip(map(ord, '''qwertyuiop[]asdfghjkl;'zxcvbnm,./`QWERTYUIOP{}ASDFGHJKL:"ZXCVBNM<>?~'''),
                          '''йцукенгшщзхъфывапролджэячсмитьбю.ёЙЦУКЕНГШЩЗХЪФЫВАПРОЛДЖЭЯЧСМИТЬБЮ,Ё'''))
        return text.translate(layout)

    @staticmethod
    def ru_to_en_keyboard(text):
        layout = dict(zip(map(ord, '''йцукенгшщзхъфывапролджэячсмитьбю.ёЙЦУКЕНГШЩЗХЪФЫВАПРОЛДЖЭЯЧСМИТЬБЮ,Ё'''),
                          '''qwertyuiop[]asdfghjkl;'zxcvbnm,./`QWERTYUIOP{}ASDFGHJKL:"ZXCVBNM<>?~'''))
        return text.translate(layout)

    @staticmethod
    def similarity_rate(a, b):
        return SequenceMatcher(None, a, b).ratio()

    @staticmethod
    def get_known_words():
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
        if self.corrected_q:
            return list(zip(
                [self.q, self.corrected_q] + self.q.split() + self.corrected_q.split(),
                [len(self.q.split()), len(self.corrected_q.split()) / 2] +
                [1] * len(self.q) + [0.5] * len(self.corrected_q)
            ))
        return list(zip(
            [self.q] + self.q.split(),
            [len(self.q.split())] + [1] * len(self.q)
        ))

    def search_term(self, term, k=1):
        term = clear_q(term)
        session = create_session()
        found = session.query(SearchData).filter(SearchData.user_id == self.uid,
                                                 SearchData.keyword.like(f"%{term}%")).all()
        return [(res.sticker_id, res.use / 20 +
                 k * self.similarity_rate(term, res.keyword) /
                 len(session.query(SearchData).filter(SearchData.sticker_id == res.sticker_id).all()))
                for res in found]

    def search_and_range(self):
        results = []
        for term, k in self.search_list():
            results += self.search_term(term, k)
        results = summed_dict(results)
        results = {results[key]: key for key in results.keys()}
        return [results[r] for r in sorted(results.keys(), reverse=True)]

# global_init("data/db/main.db")
# session = create_session()
# session.add(SearchData(user_id=1, sticker_id=1, sticker_count=3, keyword="привет", use=0))
# session.add(SearchData(user_id=1, sticker_id=1, sticker_count=3, keyword="как дела", use=0))
# session.add(SearchData(user_id=1, sticker_id=1, sticker_count=3, keyword="так дела привет", use=0))
# session.add(SearchData(user_id=1, sticker_id=2, sticker_count=3, keyword="привет кfк дела", use=0))
# session.add(SearchData(user_id=1, sticker_id=2, sticker_count=3, keyword="дела", use=0))
# session.add(SearchData(user_id=1, sticker_id=2, sticker_count=3, keyword="так вот", use=0))
# session.add(SearchData(user_id=1, sticker_id=3, sticker_count=1, keyword="привет", use=0))
# session.commit()
# print(Search("привет", user_id=1).results)
