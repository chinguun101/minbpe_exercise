def get_stats(ids):
    """
    Calculates the frequency of consecutive pairs of elements in a list of IDs.

    Parameters:
    ids (list): A list of IDs (elements) from which consecutive pairs will be extracted and counted.

    Returns:
    dict: A dictionary where keys are pairs of consecutive elements and values are their respective counts.
    """
    counts = {}  # Initialize dictionary for key: pair value: count
    for pair in zip(ids, ids[1:]): #fetching consecutive pairs and looping
        counts[pair] = + counts.get(pair, 0) + 1  # Python right-hand side evaluation invoke get() first. If the pair is not there, put 0.
    return counts

def merge(ids, pair, idx):
    """
    Merges consecutive pairs of elements in a list into a single element.

    Parameters:
    ids (list): A list of IDs (elements) to be processed.
    pair (tuple): A pair of consecutive elements to be merged.
    idx (any): The new element that will replace the pair.

    Returns:
    list: A new list of IDs with the specified pairs merged.
    """
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

def replace_control_characters(s: str) -> str:
    chars = []
    for ch in s:
        if unicodedata.category(ch)[0] != "C":
            chars.append(ch) # this character is ok
        else:
            chars.append(f"\\u{ord(ch):04x}") # escape
    return "".join(chars)

def render_token(t: bytes) -> str:
    s = t.decode('utf-8', errors='replace')
    s = replace_control_characters(s)
    return s

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

    def _build_vocab(self):
        vocab = {idx: bytes([idx]) for idx in range(256)}
        for (p0, p1), idx in self.merges.items():
            vocab[idx] = vocab[p0] + vocab[p1]
        for special, idx in self.special_tokens.items():
            vocab[idx] = special.encode("utf-8")
        return vocab
    
    def save(self, file_prefix):
        """
        Saves two files: file_prefix.vocab and file_prefix.model
        - model file is the critical one, intended for load()
        - vocab file is just a pretty printed version for human inspection only
        """
        # Construct the model filename by appending ".model" to the file prefix
        model_file = file_prefix + ".model"
        with open(model_file, 'w') as f:
            # Write the version and pattern to the model file
            f.write("minbpe v1\n")
            f.write(f"{self.pattern}\n")
            
            # Write the number of special tokens, followed by each special token and its index
            f.write(f"{len(self.special_tokens)}\n")
            for special, idx in self.special_tokens.items():
                f.write(f"{special} {idx}\n")
            
            # Write each merge pair in the merges dictionary
            for idx1, idx2 in self.merges:
                f.write(f"{idx1} {idx2}\n")
        
        # Construct the vocab filename by appending ".vocab" to the file prefix
        vocab_file = file_prefix + ".vocab"
        # Invert the merges dictionary to find the children of each token
        inverted_merges = {idx: pair for pair, idx in self.merges.items()}
        with open(vocab_file, "w", encoding="utf-8") as f:
            for idx, token in self.vocab.items():
                # Render the token for human-readable output
                s = render_token(token)
                
                if idx in inverted_merges:
                    # If the token has children, render it as a merge
                    idx0, idx1 = inverted_merges[idx]
                    s0 = render_token(self.vocab[idx0])
                    s1 = render_token(self.vocab[idx1])
                    f.write(f"[{s0}][{s1}] -> [{s}] {idx}\n")
                else:
                    # If the token is a leaf, just print it
                    f.write(f"[{s}] {idx}\n")

    def load(self, model_file):
        """Inverse of save() but only for the model file"""
        assert model_file.endswith(".model")
        
        # Initialize dictionaries for merges and special tokens
        merges = {}
        special_tokens = {}
        idx = 256  # Start index for non-special tokens
        
        with open(model_file, 'r', encoding="utf-8") as f:
            # Read and verify the version
            version = f.readline().strip()
            assert version == "minbpe v1"
            
            # Read the pattern
            self.pattern = f.readline().strip()
            
            # Read the number of special tokens
            num_special = int(f.readline().strip())
            for _ in range(num_special):
                special, special_idx = f.readline().strip().split()
                special_tokens[special] = int(special_idx)
            
            # Read the merge pairs and construct the merges dictionary
            for line in f:
                idx1, idx2 = map(int, line.split())
                merges[(idx1, idx2)] = idx
                idx += 1
        
        # Set the instance variables
        self.merges = merges
        self.special_tokens = special_tokens
        self.vocab = self._build_vocab()
