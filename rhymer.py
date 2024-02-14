import re


class PhonemeTrie:
    # Trie data structure for storing the phoneme sequences of words

    def __init__(self):
        # Initialize the trie with an empty list of words and dictionary of children
        self.children = {}
        self.words = []

    def __setitem__(self, key, value):
        # Traverse the trie recursively (DFS) to the node corresponding to the key and set the value
        node = self
        for head in key:
            if head not in node.children:
                node.children[head] = PhonemeTrie()
            node = node.children[head]
        node.words.append(value)  # Add the key word to the final node

    def __getitem__(self, key):
        # Traverse the trie recursively (DFS) to the node corresponding to the key and return the value
        node = self
        for head in key:
            if head not in node.children:
                raise KeyError(key)
            node = node.children[head]
        if node.words:
            return node.words
        else:
            raise KeyError(key)

    def __delitem__(self, key, value):
        # Traverse the trie recursively (DFS) to the node corresponding to the key and remove the value
        node = self
        for head in key:
            if head in node.children:
                node = node.children[head]
            else:
                raise KeyError(key)
        if value in node.words:
            node.words.remove(value)
        else:
            raise ValueError(key)

    def __contains__(self, key):
        # Check if the key is in the trie
        try:
            self.__getitem__(key)
        except KeyError:
            return False
        return True

    def __len__(self):
        # Count the number of words in the trie
        n = len(self.words)
        for child in self.children.values():
            n += len(child)
        return n

    def get(self, key, default=None):
        # Get the value for the key if it exists or return the default value
        try:
            return self.__getitem__(key)
        except KeyError:
            return default

    def node_count(self):
        # Count the number of nodes in the trie
        n = 0
        for k in self.children.keys():
            n = n + 1 + self.children[k].node_count()
        return n

    def keys(self, prefix=[]):
        # Return all keys in the trie from the specified starting prefix
        return self.__keys__(prefix)

    def __keys__(self, prefix=[]):
        # Return all keys in the trie from the specified starting prefix
        result = []
        if self.words:
            result.append((tuple(prefix), self.words))

        # Recursively collect keys from all children nodes (DFS)
        for phoneme, child in self.children.items():
            # Extend the current prefix with the next phoneme and recurse
            result.extend(child.keys(prefix=prefix + [phoneme]))

        return result

    def __iter__(self):
        # Iterator the trie
        for k in self.keys():
            yield k
        raise StopIteration

    def __add__(self, other):
        # + function to combine the two tries (Union)
        result = PhonemeTrie()
        result += self
        result += other
        return result

    def __sub__(self, other):
        # - function to remove elements in one tree from another (Subtraction)
        result = PhonemeTrie()
        result += self
        result -= other
        return result

    def __iadd__(self, other):
        # + function to combine the two tries (Union)
        def add_words(node, phoneme_sequence, words):
            # Base case: If phoneme_sequence is empty, merge the specified words and remove duplicates
            if not phoneme_sequence:
                node.words = list(set(node.words + words))
                return
            # Recursive case: Navigate to or create the next node in the sequence
            head = phoneme_sequence[0]
            if head not in node.children:
                node.children[head] = PhonemeTrie()
            add_words(node.children[head], phoneme_sequence[1:], words)

        # Iterate through all keys and words in the other trie and add them
        for ps, ws in other.keys():
            add_words(self, ps, ws)
        return self

    def __isub__(self, other):
        # - function to remove elements in one tree from another (Subtraction)
        def remove_words(node, phoneme_sequence, words):
            # Base case: If phoneme_sequence is empty, remove the specified words and return whether the node is empty
            if not phoneme_sequence:
                for word in words:
                    if word in node.words:
                        node.words.remove(word)
                return not node.words and not node.children
            # Recursive case: Navigate to the next node in the sequence
            head = phoneme_sequence[0]
            if head in node.children:
                child_empty = remove_words(node.children[head], phoneme_sequence[1:], words)
                if child_empty:
                    del node.children[head]
                return not node.words and not node.children  # Check if this node is now empty (no words or children)
            return False  # Phoneme sequence not found, no change

        # Iterate through all keys and words in the other trie and remove them
        for ps, ws in other.keys():
            remove_words(self, ps, ws)
        return self


class Rhymer:

    def __init__(self, phoneme_dictionary_path, phonemes_description_path):
        # Initialize the Rhymer with a word pronunciation dictionary, a set of vowels, and 4 phoneme tries
        self.end_lookup = PhonemeTrie()
        self.start_lookup = PhonemeTrie()
        self.end_rhyme_lookup = PhonemeTrie()
        self.start_rhyme_lookup = PhonemeTrie()
        self.vowels = set()
        self.dictionary = {}

        # Load phonemes description to identify vowels
        with open(phonemes_description_path, 'r', encoding='latin1') as file:
            for line in file:
                phoneme, description = line.strip().split()
                if description == "vowel":
                    self.vowels.add(phoneme)

        # Load phoneme dictionary
        with open(phoneme_dictionary_path, 'r', encoding='latin1') as file:
            for line in file:
                if not line.startswith(";;;"):  # Skip comments
                    parts = line.strip().split()
                    word = parts[0].upper()
                    pronunciation = tuple(parts[1:])
                    self.dictionary[word] = pronunciation

                    # Add the full pronunciation to the start_lookup trie
                    self.start_lookup[pronunciation] = word

                    # Add the full reversed pronunciation to the end_lookup trie
                    self.end_lookup[pronunciation[::-1]] = word

                    # Find the first vowel and its index in normal order.
                    # Then, map from the start of the word to the first vowel in the start_rhyme_lookup trie
                    first_vowel_index = next((i for i, phoneme in
                                              enumerate(pronunciation) if self.is_vowel(phoneme)), None)
                    if first_vowel_index is not None:
                        self.start_rhyme_lookup[pronunciation[:first_vowel_index + 1]] = word

                    # Find the last vowel and its index in reverse order.
                    # Then, map from the last vowel to the end of the word in the end_rhyme_lookup trie
                    last_vowel_index = next((len(pronunciation) - i - 1 for i, phoneme in
                                             enumerate(reversed(pronunciation)) if self.is_vowel(phoneme)), None)
                    if last_vowel_index is not None:
                        self.end_rhyme_lookup[pronunciation[last_vowel_index:]] = word  # Map from last vowel to the end

    def rhymes(self, word, match_stress=True):
        # Use the end_rhyme_lookup trie to get all rhymes for the specified word
        word = word.upper()
        if word in self.dictionary:
            pronunciation = self.dictionary[word]
            last_vowel_index = None
            for i, phoneme in enumerate(reversed(pronunciation)):
                if self.is_vowel(phoneme):
                    last_vowel_index = len(pronunciation) - 1 - i
                    break
            if last_vowel_index is None:
                return []  # No vowels found

            # Collect rhymes from the end_rhyme_lookup trie
            matches = []
            for key, words in self.end_rhyme_lookup.keys():
                if pronunciation[last_vowel_index:] == key[:len(pronunciation) - last_vowel_index]:
                    if match_stress:
                        stress = pronunciation[last_vowel_index][2]
                        for w in words:
                            if self.dictionary[w][len(self.dictionary[w]) - len(key)][2] == stress:
                                matches.append(w)
                    else:
                        matches.extend(words)

            matches = list(set(matches))  # Remove duplicates
            if word in matches:
                matches.remove(word)  # Exclude the original word
            return matches
        return []

    def pronunciation(self, word):
        # Get the main pronunciation for the specified word
        word = word.upper()
        return self.dictionary.get(word, [])

    def alternates(self, word):
        # Get all alternate pronunciations for the specified word
        n = 1
        word = word.upper()
        alternates = []
        alternate = f"{word}({n})"
        while alternate in self.dictionary:
            alternates.append(alternate)
            n += 1
            alternate = f"{word}({n})"
        return alternates

    def phoneme_trie_size(self):
        # Get the total number of nodes in all 4 phoneme tries
        return (self.end_lookup.node_count() + self.start_lookup.node_count() +
                self.end_rhyme_lookup.node_count() + self.start_rhyme_lookup.node_count())

    def in_dictionary(self, word):
        # Check if the specified word is in the dictionary
        return word in self.dictionary

    def is_vowel(self, phoneme):
        # Check if the specified phoneme is a vowel
        return re.sub(r'[0-9]+', '', phoneme) in self.vowels

    def is_consonant(self, phoneme):
        # Check if the specified phoneme is a consonant
        return not self.is_vowel(phoneme)

    def get_end_lookup_keys(self):
        # Get all keys in the end_lookup trie
        return self.end_lookup.keys()

    def get_start_lookup_keys(self):
        # Get all keys in the start_lookup trie
        return self.start_lookup.keys()

    def get_end_rhyme_lookup_keys(self):
        # Get all keys in the end_rhyme_lookup trie
        return self.end_rhyme_lookup.keys()

    def get_start_rhyme_lookup_keys(self):
        # Get all keys in the start_rhyme_lookup trie
        return self.start_rhyme_lookup.keys()

    def get_end_trie(self):
        # Return the end_lookup trie
        return self.end_lookup

    def get_start_trie(self):
        # Return the end_lookup trie
        return self.start_lookup

    def get_end_rhyme_trie(self):
        # Return the end_rhyme_lookup trie
        return self.end_rhyme_lookup

    def get_start_rhyme_trie(self):
        # Return the start_rhyme_lookup trie
        return self.start_rhyme_lookup

    def get_dictionary(self):
        # Return the phoneme dictionary
        return self.dictionary
