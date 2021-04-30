import operator
from nltk import word_tokenize
from nltk.util import ngrams
from collections import Counter


class NgramStats:
    """ Collect unigram and bigram statistics. """

    def __init__(self):
        self.bigram_to_count = Counter([])
        self.unigram_to_count = dict()

    def collect_ngram_counts(self, corpus):
        """Collect unigram and bigram counts from the given corpus."""
        unigram_counter = Counter([])
        for sentence in corpus:
            tokens = word_tokenize(sentence)
            bigrams = ngrams(tokens, 2)
            unigrams = ngrams(tokens, 1)
            self.bigram_to_count += Counter(bigrams)
            unigram_counter += Counter(unigrams)
        self.unigram_to_count = {k[0]: int(v) for k, v in unigram_counter.items()}


class AbsDist:
    """
     Implementation of Interpolated Absolute Discounting

     Reference: slide 25 in https://nlp.stanford.edu/~wcmac/papers/20050421-smoothing-tutorial.pdf
    """

    def __init__(self, ngram_stats):
        """ Initialization

            Args:
                ngram_stats (NgramStats) : ngram statistics.
        """
        self.unigram_freq = float(sum(ngram_stats.unigram_to_count.values()))
        self.stats = ngram_stats

    def compute_prop(self, bigram, discount=0.75):
        """ Compute probability p(y | x)

            Args:
                bigram (string tuple) : a bigram (x, y), where x and y denotes an unigram respectively.
                discount (float) : the discounter factor for the linear interpolation.
        """
        preceding_word_count = 0
        if bigram[0] in self.stats.unigram_to_count:
            preceding_word_count = self.stats.unigram_to_count[bigram[0]]
        if preceding_word_count > 0:
            left_term = 0
            if bigram in self.stats.bigram_to_count:
                bigram_count = float(self.stats.bigram_to_count[bigram])
                left_term = (bigram_count - discount) / preceding_word_count
            right_term = 0
            if bigram[1] in self.stats.unigram_to_count:
                current_word_count = self.stats.unigram_to_count[bigram[1]]
                num_bigram_preceding_word = 0
                for c_bigram in self.stats.bigram_to_count.keys():
                    if c_bigram[0] == bigram[0]:
                        num_bigram_preceding_word += 1
                normalization_param = (discount * num_bigram_preceding_word) / preceding_word_count
                p_unigram = current_word_count / self.unigram_freq
                right_term = normalization_param * p_unigram
            return left_term + right_term

        return 0


class KNSmoothing:
    def __init__(self, ngram_stats):
        """ Initialization

            Args:
                ngram_stats (NgramStats) : ngram statistics.
        """
        self.unigram_freq = float(sum(ngram_stats.unigram_to_count.values()))
        self.stats = ngram_stats

    def compute_prop(self, bigram, discount=0.75):
        """ Compute probability p(y | x) incorporating KNSmoothing

            Args:
                bigram (string tuple) : a bigram (x, y), where x and y denotes an unigram respectively.
                discount (float) : the discounter factor for the linear interpolation.
        """
        preceding_word_count = 0
        if bigram[0] in self.stats.unigram_to_count:
            preceding_word_count = self.stats.unigram_to_count[bigram[0]]

        if preceding_word_count > 0:
            left_term = 0
            if bigram in self.stats.bigram_to_count:
                bigram_count = float(self.stats.bigram_to_count[bigram])
                left_term = (bigram_count - discount) / preceding_word_count
            right_term = 0
            if bigram[1] in self.stats.unigram_to_count:
                num_bigram_preceding_word = 0
                for c_bigram in self.stats.bigram_to_count.keys():
                    if c_bigram[0] == bigram[0]:
                        num_bigram_preceding_word += 1
                normalization_param = (discount * num_bigram_preceding_word) / preceding_word_count
                count = 0
                for bigram_count in self.stats.bigram_to_count:
                    if bigram[1] == bigram_count[1]:
                        count += 1
                p_continuation = count / len(self.stats.bigram_to_count)
                right_term = normalization_param * p_continuation
            return left_term + right_term
        return 0


def compute_prop(prop_computer, ngram_stats, preceding_unigram, d=0.75):
    """ Compute the distribution p(y | x) of all y given preceding_unigram

        Args:
            preceding_unigram (string) : the preceding unigram.
            d (float) : the discounter factor for the linear interpolation.
    """
    model = prop_computer(ngram_stats)
    c_unigram_to_prob = dict()
    for c_unigram in ngram_stats.unigram_to_count.keys():
        if not c_unigram in c_unigram_to_prob:
            c_unigram_to_prob[c_unigram] = model.compute_prop((preceding_unigram, c_unigram), d)

    sorted_prob = sorted(c_unigram_to_prob.items(), key=operator.itemgetter(1))
    return sorted_prob


ngram_corpus = ['Sam eats apple',
                "Granny plays with Sam",
                "Sam plays with Smith",
                "Sam likes Smith",
                "Sam likes apple",
                "Sam likes sport",
                "Sam plays tennis",
                "Sam likes games",
                "Sam plays games",
                "Sam likes apple Granny Smith"]

stats = NgramStats()
stats.collect_ngram_counts(ngram_corpus)
print(stats.bigram_to_count)
print(stats.unigram_to_count)

print(f'AbsDist: {compute_prop(AbsDist, stats, "Granny")}')

print(f'KNSmooth: {compute_prop(KNSmoothing, stats, "Granny")}')