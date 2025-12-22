try:
    import os
    def random_bytes(n):
        return os.urandom(n)
except:
    import urandom
    def random_bytes(n):
        return bytes([urandom.getrandbits(8) for _ in range(n)])