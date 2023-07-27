import string
from difflib import SequenceMatcher

import numpy as np
from pyxdameraulevenshtein import normalized_damerau_levenshtein_distance_seqs

from db_models.db_session import create_session
from db_models.search_data import SearchData
from db_models.user_sets import UserSet


def summed_dict(lst: list) -> dict:
    res = {}
    for i in lst:
        if i[0] in res.keys():
            res[i[0]] += i[1]
        else:
            res[i[0]] = i[1]
    return res


def clear_q(q: str) -> str:
    return q.strip().lower().translate(str.maketrans('', '', string.punctuation)).replace("ё", "е")


class Search:
    def __init__(self, q: str, user_id: (str, int)) -> None:
        session = create_session()
        self.q = q.lower()
        self.dictionary = self.get_dictionary()
        self.user_set_list = [i[0] for i in session.query(UserSet.set_id).filter(UserSet.user_id == user_id).all()]

    def get_results(self) -> list:
        return self.search_and_range()

    @property
    def corrected_q(self) -> str:
        res = []
        for orig_word in self.q.split():
            word = clear_q(orig_word)
            if word.lower() in self.dictionary:
                res.append(word)
            else:
                corrected = self.correct_word(word)
                if corrected in self.dictionary:
                    res.append(corrected)
                else:
                    if any([97 <= ord(i) <= 122 for i in word]):
                        fixed_lang = clear_q(self.en_to_ru_keyboard(orig_word))
                    elif any([1072 <= ord(i) <= 1103 for i in word]):
                        fixed_lang = clear_q(self.ru_to_en_keyboard(orig_word))
                    else:
                        fixed_lang = word
                    if fixed_lang in self.dictionary:
                        res.append(fixed_lang)
                    else:
                        res.append(self.correct_word(fixed_lang))
        return " ".join(res) if res else None

    @staticmethod
    def en_to_ru_keyboard(text: str) -> str:
        layout = dict(zip(map(ord, '''qwertyuiop[]asdfghjkl;'zxcvbnm,./`QWERTYUIOP{}ASDFGHJKL:"ZXCVBNM<>?~'''),
                          '''йцукенгшщзхъфывапролджэячсмитьбю.ёЙЦУКЕНГШЩЗХЪФЫВАПРОЛДЖЭЯЧСМИТЬБЮ,Ё'''))
        return text.translate(layout)

    @staticmethod
    def ru_to_en_keyboard(text: str) -> str:
        layout = dict(zip(map(ord, '''йцукенгшщзхъфывапролджэячсмитьбю.ёЙЦУКЕНГШЩЗХЪФЫВАПРОЛДЖЭЯЧСМИТЬБЮ,Ё'''),
                          '''qwertyuiop[]asdfghjkl;'zxcvbnm,./`QWERTYUIOP{}ASDFGHJKL:"ZXCVBNM<>?~'''))
        return text.translate(layout)

    @staticmethod
    def similarity_rate(a: str, b: str) -> float:
        return SequenceMatcher(None, a, b).ratio()

    @staticmethod
    def get_dictionary() -> list:
        with open("data/dictionary.txt", encoding="utf-8") as dictionary_file:
            dictionary = dictionary_file.read().strip().split()
        return dictionary

    def correct_word(self, word: str) -> str:
        array = np.array(self.dictionary)
        result = list(zip(self.dictionary,
                          list(normalized_damerau_levenshtein_distance_seqs(word, array))))
        try:
            corrected_word, rate = min(result, key=lambda x: x[1])
            if rate > 0.4:
                return word
        except ValueError:
            return word
        return corrected_word

    def search_list(self) -> list:
        corrected_q = self.corrected_q
        if corrected_q:
            return list(zip(
                [self.q, corrected_q] + self.q.split() + corrected_q.split(),
                [len(self.q.split()), len(corrected_q.split()) / 2] +
                [1] * len(self.q.split()) + [0.5] * len(corrected_q.split())
            ))
        return list(zip(
            [self.q] + self.q.split(),
            [len(self.q.split())] + [1] * len(self.q.split())
        ))

    def search_term(self, term: str, k: float = 1) -> list:
        term = clear_q(term)
        session = create_session()
        found = session.query(SearchData).filter(SearchData.set_id.in_(self.user_set_list),
                                                 SearchData.keyword.like(f"%{term}%")).all()
        return [(res.sticker.sticker_file_id,
                 k * self.similarity_rate(term, res.keyword) /
                 len(session.query(SearchData).filter(
                     SearchData.sticker_unique_id == res.sticker_unique_id).all()))
                for res in found]

    def search_and_range(self) -> list:
        results = []
        for term, k in self.search_list():
            results += self.search_term(term, k)
        results = summed_dict(results)
        results = {results[key]: key for key in results.keys()}
        return [results[r] for r in sorted(results.keys(), reverse=True)]
