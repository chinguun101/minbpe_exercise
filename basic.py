
class BasicTokenizer:
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