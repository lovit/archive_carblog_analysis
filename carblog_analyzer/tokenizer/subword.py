from collections import Counter
from collections import defaultdict
from soynlp.normalizer import normalize

class SubwordTokenizer:
    def __init__(self, subwords=None):
        if not subwords:
            raise ValueError('subwords must be non-empty dictionary')
        self.subwords = subwords

    def tokenize(self, sent, flatten=True):
        def tokenize(word):
            subwords = find_subwords(word)
            return [sub for sub in subwords if sub in self.subwords]
        sent = normalize(sent, alphabet=True, number=True)
        sent = [tokenize(word) for word in sent.split()]
        if flatten:
            sent = [sub for subwords in sent for sub in subwords]
        return sent

def find_subwords(word):
    return [word[:i] for i in range(1, len(word)+1)]

def count_subword(documents, min_count=50):
    counter = defaultdict(int)
    for doc in documents:
        for word in doc.split():
            for sub in find_subwords(word):
                counter[sub] += 1
    counter = {sub:count for sub, count in counter.items() if count >= min_count}
    return counter

def train_droprate(subword_counter):
    droprates = defaultdict(lambda: 0)
    for longer, longer_count in subword_counter.items():
        if len(longer) <= 2:
            continue
        shorter = longer[:-1]
        shorter_count = subword_counter.get(shorter, 0)
        if shorter_count == 0:
            continue
        droprate = longer_count / shorter_count
        droprates[shorter] = max(droprates[shorter], droprate)
    return dict(droprates)

def droprate_to_word_score(droprates):
    return {sub:1-dr for sub, dr in droprates.items()}

def word_score_by_droprate(documents, min_count=50):
    counter = count_subword(documents, min_count)
    droprates = train_droprate(counter)
    word_scores = droprate_to_word_score(droprates)
    return word_scores
