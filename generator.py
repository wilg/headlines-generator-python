from collections import defaultdict
from random import randint
from random import random
import os
import itertools
import sys
import re
from titlecase import titlecase

from timeit import default_timer as timer

# Settings
max_corpus_size = int(os.getenv('MAX_CORPUS_SIZE', 20000))

def frag_or_none(fragment):
    if fragment:
        return fragment.fragment
    return ''

def comparison_string(s):
    s = s.strip().lower().replace("\"", "")
    re.sub('[^0-9a-zA-Z]+', '', s)
    return s

class HeadlineSourcePhrase:
    def __init__(self, phrase, source_id):
        self.phrase = phrase.strip()
        self.source_id = source_id
        self.comparison_string = comparison_string(self.phrase)
    def __eq__(self, other):
        return self.comparison_string == other.comparison_string
    def __hash__(self):
        return self.comparison_string.__hash__()

class HeadlineFragment:
    def __init__(self, source_phrase, fragment):
        self.source_phrase = source_phrase
        self.fragment = fragment
        self.comparison_string = comparison_string(self.fragment)
    def __eq__(self, other):
        return self.comparison_string == other.comparison_string
    def __hash__(self):
        return self.comparison_string.__hash__()

class HeadlineResultPhrase:
    def __init__(self):
        self.fragments = []
    def append(self, frag):
        self.fragments.append(frag)

    def merge_fragment_groups(self, fragment_groups):
        fragments = []
        for group in fragment_groups:
            if len(group) > 1:
                fragments.append(HeadlineFragment(group[-1].source_phrase, ' '.join([fragment.fragment for fragment in group])))
            else:
                fragments.append(group[0])
        return fragments

    def reduced_fragments(self):
        fragments = self.fragments
        this_str = str(self)

        # Combine fragments from the same source
        last_source_phrase = None
        current_group = []
        groups = []
        for fragment in fragments:
            if fragment.fragment != '':
                if last_source_phrase != None and last_source_phrase != fragment.source_phrase:
                    groups.append(current_group)
                    current_group = []
                current_group.append(fragment)
                last_source_phrase = fragment.source_phrase
        groups.append(current_group)
        fragments = self.merge_fragment_groups(groups)

        # Combine fragments that start the source phrase
        groups = []
        current_group = []
        sentence = []
        start = 0
        i = 0
        for fragment in fragments:
            sentence.append(fragment.fragment)
            phrase_so_far = ' '.join(sentence[start:])
            if phrase_so_far in fragment.source_phrase.phrase:
                current_group.append(fragment)
            else:
                start = i
                if len(current_group) > 0:
                    groups.append(current_group)
                    current_group = []
                    current_group.append(fragment)
            i += 1
        groups.append(current_group)
        fragments = self.merge_fragment_groups(groups)

        return fragments

    def fragment_hashes(self):
        fragments = []

        char_index = 0
        for frag in self.reduced_fragments():
            hsh = {'index': char_index, 'fragment': titlecase(frag.fragment), 'source_id':frag.source_phrase.source_id, 'source_phrase':frag.source_phrase.phrase}
            fragments.append(hsh)
            char_index += len(frag.fragment)

        return fragments
    def __str__(self):
        return titlecase(' '.join([fragment.fragment for fragment in self.fragments]).strip())

class HeadlineGenerator:

    def generate(self, sources, depth):

        self.depth = depth

        start = timer()

        # Import multiple dictionaries
        dir = os.path.dirname(__file__)
        imported_titles = []
        per_dictionary_limit = max_corpus_size / len(sources)
        for source_id in sources:
            filename = os.path.join(dir, "vendor/headline-sources/db/" + source_id + ".txt")

            archive = open(filename)
            dict_titles = archive.read().split("\n")
            archive.close()

            if len(dict_titles) > per_dictionary_limit:
                window_start = randint(0,len(dict_titles) - per_dictionary_limit)
                dict_titles = dict_titles[window_start:window_start+per_dictionary_limit]

            source_phrases = [HeadlineSourcePhrase(headline, source_id) for headline in dict_titles]

            imported_titles = imported_titles + source_phrases

        self.source_phrases = imported_titles

        print "-> import time " + str(timer() - start)
        start = timer()

        self.markov_map = defaultdict(lambda:defaultdict(int))

        # Generate map in the form word1 -> word2 -> occurences of word2 after word1
        for source_phrase in self.source_phrases[:-1]:
            title = source_phrase.phrase.split()
            if len(title) > self.depth:
                for i in xrange(len(title)+1):
                    a = HeadlineFragment(source_phrase, ' '.join(title[max(0,i-self.depth):i]))
                    b = HeadlineFragment(source_phrase, ' '.join(title[i:i+1]))
                    self.markov_map[a][b] += 1

        # Convert map to the word1 -> word2 -> probability of word2 after word1
        for word, following in self.markov_map.items():
            total = float(sum(following.values()))
            for key in following:
                following[key] /= total


        print "-> map time " + str(timer() - start)
        start = timer()

        results = []
        for _ in itertools.repeat(None, 10):
            results.append(self.get_sentence())

        print "-> sample time " + str(timer() - start)
        return results

    # Typical sampling from a categorical distribution
    def sample(self, items):
        next_word = ''
        t = 0.0
        for k, v in items:
            t += v
            if t and random() < v/t:
                next_word = k
        return next_word

    def get_sentence(self, length_max=140):
        while True:
            sentence = HeadlineResultPhrase()
            next_word = self.sample(self.markov_map[HeadlineFragment(None, '')].items())
            while next_word != '':
                sentence.append(next_word)
                tmp_frag_list = [frag_or_none(frag) for frag in sentence.fragments[-self.depth:]]
                tmp_item = HeadlineFragment(None, ' '.join(tmp_frag_list))
                next_word = self.sample(self.markov_map[tmp_item].items())
            str_sentence = comparison_string(str(sentence))
            if any(str_sentence in phrase.comparison_string for phrase in self.source_phrases):
                continue # Prune titles that are substrings of actual titles
            if len(str_sentence) > length_max:
                continue
            return sentence
