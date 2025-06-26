
# API URLs
DEFAULT_BASE_URL = "https://api.lumnis.ai"
CUSTOMER_API_URL = "https://customer-app.lemonhill-a0ee8763.eastus.azurecontainerapps.io"

# Polling configuration
DEFAULT_POLL_INTERVAL = 2.0  # seconds
LONG_POLL_TIMEOUT = 10  # seconds
MAX_LONG_POLL_RETRIES = 10

# HTTP timeouts and retries
DEFAULT_TIMEOUT = 30.0  # seconds
DEFAULT_MAX_RETRIES = 3
DEFAULT_BACKOFF_FACTOR = 0.5

# Rate limiting
TENANT_WARNING_BUCKET_CAPACITY = 10  # tokens
TENANT_WARNING_BUCKET_REFILL_RATE = 10  # tokens per minute

# Pagination defaults
DEFAULT_LIMIT = 50
MAX_LIMIT = 100

# Hash lengths
TENANT_ID_HASH_LENGTH = 16  # characters for hashed tenant ID
