
from .base import Tokenizer, get_stats, merge


class BasicTokenizer(Tokenizer):

    def __init__(self):
        super().__init__()

    def train(self, text, vocab_size, verbose=False):
        """
        Trains a BPE (Byte Pair Encoding) tokenizer on the given text.

        Parameters:
        text (str): The input text to be tokenized.
        vocab_size (int): The desired size of the vocabulary after training.
        verbose (bool): If True, prints detailed information about each merge operation.

        Returns:
        None
        """
        assert vocab_size >= 256, "Vocab size must be at least 256."
        num_merges = vocab_size - 256

        # Input text preprocessing
        text_bytes = text.encode("utf-8")  # Encode text to bytes
        ids = list(text_bytes)  # Convert bytes to list of integers

        merges = {}  # Dictionary to store merge operations (pair -> new index)
        vocab = {idx: bytes([idx]) for idx in range(256)}  # Initialize vocabulary with single-byte tokens

        for i in range(num_merges):
            stats = get_stats(ids)  # Get frequency of consecutive pairs
            pair = max(stats, key=stats.get)  # Find the most frequent pair
            idx = 256 + i  # New index for the merged pair
            ids = merge(ids, pair, idx)  # Merge the most frequent pair
            merges[pair] = idx  # Record the merge operation
            vocab[idx] = vocab[pair[0]] + vocab[pair[1]]  # Update the vocabulary

            if verbose:
                print(f"merge {i + 1}/{num_merges}: {pair} -> {idx} ({vocab[idx]}) had {stats[pair]} occurrences")

        self.merges = merges  # Save the merge operations
        self.vocab = vocab  # Save the vocabulary

    def decode(ids):
        """
        Decodes a list of token IDs back into a string.

        Parameters:
        ids (list of int): The list of token IDs to decode.

        Returns:
        str: The decoded string.
        """
        tokens = b"".join(vocab[idx] for idx in ids)  # Concatenate bytes for each token ID
        text = tokens.decode("utf-8", errors="replace")  # Decode bytes to string, replacing errors
        return text

    def encode(text):
        """
        Encodes a string into a list of token IDs using the trained BPE model.

        Parameters:
        text (str): The input text to be encoded.

        Returns:
        list of int: The list of token IDs.
        """
        tokens = list(text.encode("utf-8"))  # Convert string to list of byte values

        while True:
            stats = get_stats(tokens)  # Get frequency of consecutive pairs
            pair = min(stats, key=lambda p: merges.get(p, float("inf")))  # Find the least frequent pair in merges
            if pair not in merges:
                break  # Exit if no more pairs can be merged
            idx = merges[pair]  # Get the new index for the merged pair
            tokens = merge(tokens, pair, idx)  # Merge the pair

        return tokens
