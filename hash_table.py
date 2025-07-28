# Custom HashTable for WGUPS (C950)

class HashTable:
    def __init__(self, size=40):
        # Initialize the hash table with empty buckets (chaining method)
        self.table = [[] for _ in range(size)]

    def _hash(self, key):
        # Simple hash function using modulo
        return key % len(self.table)

    def insert(self, key, item):
        # Insert key-value pair, updating if key already exists
        bucket_index = self._hash(key)
        bucket = self.table[bucket_index]

        for i, kv in enumerate(bucket):
            if kv[0] == key:
                bucket[i] = (key, item)
                return
        bucket.append((key, item))

    def lookup(self, key):
        # Retrieve value by key
        bucket_index = self._hash(key)
        bucket = self.table[bucket_index]

        for k, v in bucket:
            if k == key:
                return v
        return None

    def remove(self, key):
        # Remove key-value pair
        bucket_index = self._hash(key)
        bucket = self.table[bucket_index]

        for i, (k, _) in enumerate(bucket):
            if k == key:
                del bucket[i]
                return True
        return False
    
