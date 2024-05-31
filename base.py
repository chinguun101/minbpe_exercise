def get_stats(ids):
    counts = {}  # Initialize dictionary for key: pair value: count
    for pair in zip(ids, ids[1:]): #fetching consecutive pairs and looping
        counts[pair] = + counts.get(pair, 0) + 1  # Python right-hand side evaluation invoke get() first. If the pair is not there, put 0.
    return counts

def merge(ids, pair, idx):
    new_ids = []
    i=0
    while i < len(ids): #len(ids)-1 dismisses the last element so we iterate thoroughly with len(ids)
        if i < len(ids) - 1 and ids[i]==pair[0] and ids[i+1]== pair[1]: #If the pairs match while ensuring i+1 doesn't go out of range
            new_ids.append(idx) #replace with new id 
            i+=2
        else:
            new_ids.append(ids[i]) #copy the original id
            i+=1
    return new_ids
""""
#Fix for train function later on
vocab_size=276
merge_num=vocab_size-256
ids=list(tokens)
merges={}

ids=list(tokens)
for i in range(merge_num):
    stats=get_stats(ids)
    pair=max(stats, key=stats.get)
    idx=256+i
    print(f"merging {pair} into new token {idx}")
    ids=merge(ids,pair,idx)
    merges[pair]=idx 
"""

class Tokenizer:
    """Base class for Tokenizers"""

    def __init__(self):
        # default: vocab size of 256 (all bytes), no merges, no patterns
        self.merges = {} # (int, int) -> int
        self.pattern = "" # str
        self.special_tokens = {} # str -> int, e.g. {'<|endoftext|>': 100257}
        self.vocab = self._build_vocab() # int -> bytes

    def train(self, text, vocab_size, verbose=False):
        # Tokenizer can train a vocabulary of size vocab_size from text
        raise NotImplementedError

    def encode(self, text):
        # Tokenizer can encode a string into a list of integers
        raise NotImplementedError

    def decode(self, ids):
        # Tokenizer can decode a list of integers into a string
        raise NotImplementedError
    