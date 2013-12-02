from collections import defaultdict
from random import randint
from random import random
import os
import itertools
import sys
from titlecase import titlecase

from timeit import default_timer as timer

# Settings
max_corpus_size = int(os.getenv('MAX_CORPUS_SIZE', 20000))

class HeadlineGenerator:

    def generate(self, sources, depth):

        self.depth = depth

        start = timer()

        # import multiple dictionaries
        dir = os.path.dirname(__file__)
        imported_titles = []
        per_dictionary_limit = max_corpus_size / len(sources)
        for source_name in sources:
            filename = os.path.join(dir, "vendor/headline-sources/db/" + source_name + ".txt")

            archive = open(filename)
            dict_titles = archive.read().split("\n")
            archive.close()

            if len(dict_titles) > per_dictionary_limit:
                window_start = randint(0,len(dict_titles) - per_dictionary_limit)
                dict_titles = dict_titles[window_start:window_start+per_dictionary_limit]

            imported_titles = imported_titles + dict_titles


        self.titles = []

        print "-> import time " + str(timer() - start)
        start = timer()

        # lowercase everything, remove quotes (to prevent dangling quotes)
        # we're also going to create a mapping back to the original case if it's a weird word (like iPad)
        self.titlecase_mappings = {}
        for title in imported_titles:
            self.titles.append(title.lower().replace("\"", ""))
            for original_word in title.replace("\"", "").split(" "):
                self.titlecase_mappings[original_word.lower()] = original_word

        self.markov_map = defaultdict(lambda:defaultdict(int))

        #Generate map in the form word1 -> word2 -> occurences of word2 after word1
        for title in self.titles[:-1]:
            title = title.split()
            if len(title) > self.depth:
                for i in xrange(len(title)+1):
                    self.markov_map[' '.join(title[max(0,i-self.depth):i])][' '.join(title[i:i+1])] += 1

        #Convert map to the word1 -> word2 -> probability of word2 after word1
        for word, following in self.markov_map.items():
            total = float(sum(following.values()))
            for key in following:
                following[key] /= total


        print "-> map time " + str(timer() - start)
        start = timer()

        results = []
        for _ in itertools.repeat(None, 10):
            results.append(self.retitlize_sentence(self.get_sentence()))

        print "-> sample time " + str(timer() - start)
        return results

    #Typical sampling from a categorical distribution
    def sample(self, items):
        next_word = None
        t = 0.0
        for k, v in items:
            t += v
            if t and random() < v/t:
                next_word = k
        return next_word

    def get_sentence(self, length_max=140):
        while True:
            sentence = []
            next_word = self.sample(self.markov_map[''].items())
            while next_word != '':
                sentence.append(next_word)
                next_word = self.sample(self.markov_map[' '.join(sentence[-self.depth:])].items())
            sentence = ' '.join(sentence)
            if any(sentence in title for title in self.titles):
                continue #Prune titles that are substrings of actual titles
            if len(sentence) > length_max:
                continue
            return sentence

    def retitlize_sentence(self, sentence):
        lowercase_sentence = sentence.split(" ")
        uppercase_sentence = []

        for word in lowercase_sentence:
            uppercase_sentence.append(self.titlecase_mappings.get(word, word))

        return titlecase(" ".join(uppercase_sentence))

