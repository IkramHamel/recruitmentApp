import heapq
import threading

class KeysBalancer:
    def __init__(self, api_keys):
        """
        Initialize the balancer with a list of API keys.

        :param api_keys: List of API keys (strings)
        """
        self.lock = threading.Lock()  # Simple integer to represent lock state
        self.api_keys = set(api_keys)  # Store keys in a set for fast lookup
        self.workload = {key: 0 for key in api_keys}  # Track workload for each key
        self.min_heap = [(0, key) for key in api_keys]  # Priority queue based on workload
        heapq.heapify(self.min_heap)

    def get_least_used_key(self):
        """
        Get the API key with the least workload.

        :return: The least-used API key (string)
        """
        try:
            workload, key = heapq.heappop(self.min_heap)
        finally:
            return key

    def register_request(self, api_key):
        """
        Register a request for a given API key, increasing its workload.

        :param api_key: The API key (string)
        """
        
        self.workload[api_key] += 1
        heapq.heappush(self.min_heap, (self.workload[api_key], api_key))
            

    def allocate_key(self):
        """
        Allocate an API key for the next request, balancing the load.

        :return: The allocated API key (string)
        """
        self.lock.acquire_lock()
        try:
            key = self.get_least_used_key()
            self.register_request(key)
            return key
        finally:
            self.lock.release_lock()

    def add_key(self, api_key):
        """
        Add a new API key to the balancer. If the key already exists, do not add it.

        :param api_key: The new API key (string)
        """
        self.lock.acquire_lock()
        try:
            if api_key not in self.api_keys:
                self.api_keys.add(api_key)
                self.workload[api_key] = 0
                heapq.heappush(self.min_heap, (0, api_key))
            else:
                print(f"API key '{api_key}' already exists. Not adding.")
        finally:
            self.lock.release_lock()

    def remove_key(self, api_key):
        """
        Remove an API key from the balancer.

        :param api_key: The API key to remove (string)
        """
        self.lock.acquire_lock()
        try:
            if api_key in self.api_keys:
                self.api_keys.remove(api_key)
                del self.workload[api_key]

                # Rebuild the heap to remove the key from the heap
                self.min_heap = [(workload, key) for key, workload in self.workload.items()]
                heapq.heapify(self.min_heap)
            else:
                print(f"API key '{api_key}' does not exist. Cannot remove.")
        finally:
            self.lock.release_lock()
