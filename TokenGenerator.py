import hashlib

class TokenGenerator:
    def __init__(self, shared_key: str, initial_counter: int = 0):
        """
        Inicjalizuje obiekt przechowujący współdzielony klucz oraz licznik.
        """
        self.shared_key = shared_key
        self.counter = initial_counter

    def generate_token(self) -> str:
        """
        Oblicza SHA-256 dla połączonego ciągu: shared_key + str(counter).
        Zwraca wynik w postaci szesnastkowej (hex).
        """
        data_to_hash = self.shared_key + str(self.counter)
        self.counter += 1

        encoded_data = data_to_hash.encode('utf-8')
        hash_result = hashlib.sha256(encoded_data)
        
        return hash_result.hexdigest()
