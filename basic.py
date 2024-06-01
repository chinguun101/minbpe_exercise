
class BasicTokenizer:
    def train(self, text, vocab_size, verbose=False):
        assert vocab_size >= 256
        num_merges = vocab_size - 256

        # input text preprocessing
        text_bytes = text.encode("utf-8") 
        ids = list(text_bytes) 


        merges = {} # (int, int) -> int
        vocab = {idx: bytes([idx]) for idx in range(256)} # int -> bytes
        for i in range(num_merges):
            stats = get_stats(ids)
            pair = max(stats, key=stats.get)
            idx = 256 + i
            ids = merge(ids, pair, idx)
            merges[pair] = idx
            vocab[idx] = vocab[pair[0]] + vocab[pair[1]]
            if verbose:
                print(f"merge {i+1}/{num_merges}: {pair} -> {idx} ({vocab[idx]}) had {stats[pair]} occurrences")

        self.merges = merges
        self.vocab = vocab 

    def decode(ids):
        # given ids (list of integers), return Python string
        tokens = b"".join(vocab[idx] for idx in ids) #Concatenate 
        text = tokens.decode("utf-8", errors="replace") #Replace avoids the unknown character
        return text

    def encode(text):
        #Strings to integers
        tokens=list(text.encode("utf-8"))
        while True:
            stats = get_stats(tokens)
            pair = min(stats, key=lambda p: merges.get(p, float("inf")))
            if pair not in merges:
                break
            idx=merges[pair]
            tokens=merge(tokens,pair,idx)
        return tokens