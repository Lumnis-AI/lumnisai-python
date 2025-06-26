
from enum import Enum


class Scope(str, Enum):

    USER = "user"
    TENANT = "tenant"


class ApiProvider(str, Enum):

    OPENAI_API_KEY = "OPENAI_API_KEY"
    ANTHROPIC_API_KEY = "ANTHROPIC_API_KEY"
    COHERE_API_KEY = "COHERE_API_KEY"
    GOOGLE_API_KEY = "GOOGLE_API_KEY"
    EXA_API_KEY = "EXA_API_KEY"
    SERPAPI_API_KEY = "SERPAPI_API_KEY"


class ApiKeyMode(str, Enum):

    BYO_KEYS = "byo_keys"
    PLATFORM = "platform"
