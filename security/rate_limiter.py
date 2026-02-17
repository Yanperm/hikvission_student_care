from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"
)

# Custom limits
LOGIN_LIMIT = "5 per minute"
API_LIMIT = "100 per minute"
UPLOAD_LIMIT = "10 per minute"
