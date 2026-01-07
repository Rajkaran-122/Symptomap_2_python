from slowapi import Limiter
from slowapi.util import get_remote_address

# Initialize global rate limiter
# Uses memory storage by default. For distributed production, plug in Redis here.
limiter = Limiter(key_func=get_remote_address)
