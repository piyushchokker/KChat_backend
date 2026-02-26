from services.redis_queue import get_queue_length, pop_from_queue, peek_queue


# Print the current queue length
print("Queue length:", get_queue_length())

# Peek at the next item (does not remove it)
print("Next item:", peek_queue())

