import hashlib

class TokenGenerator:
    def __init__(self, shared_key: str, initial_counter: int = 0):
        self.shared_key = shared_key
        self.counter = initial_counter

    def generate_token(self) -> str:
        """Generate token and increment internal counter."""
        data_to_hash = self.shared_key + str(self.counter)
        self.counter += 1

        encoded_data = data_to_hash.encode('utf-8')
        hash_result = hashlib.sha256(encoded_data)

        return hash_result.hexdigest()
