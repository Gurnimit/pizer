import string
import itertools

class BruteForceGenerator:
    def __init__(self, max_length=4, use_lower=True, use_upper=True, use_digits=True, use_symbols=False):
        self.max_length = max_length
        self.charset = ""
        if use_lower:
            self.charset += string.ascii_lowercase
        if use_upper:
            self.charset += string.ascii_uppercase
        if use_digits:
            self.charset += string.digits
        if use_symbols:
            # Expanded symbols
            self.charset += "!@#$%^&*()-_=+[]{};:,./?"
            
        if not self.charset:
            raise ValueError("At least one character set must be selected.")

    def generate(self):
        """Yields password combinations."""
        length = 1
        while True:
            # If max_length is set (greater than 0) and we've exceeded it, stop.
            if self.max_length > 0 and length > self.max_length:
                break
            
            for combo in itertools.product(self.charset, repeat=length):
                yield ''.join(combo)
            
            length += 1
