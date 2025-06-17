
from enum import Enum


class Scope(str, Enum):

    USER = "user"
    TENANT = "tenant"


class ApiProvider(str, Enum):

    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    AZURE = "azure"


class ApiKeyMode(str, Enum):

    BRING_YOUR_OWN = "byo"
    USE_PLATFORM = "platform"
    