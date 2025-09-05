
from enum import Enum


class Scope(str, Enum):

    USER = "user"
    TENANT = "tenant"


class ApiProvider(str, Enum):
    """Supported external API providers"""

    OPENAI_API_KEY = "OPENAI_API_KEY"
    ANTHROPIC_API_KEY = "ANTHROPIC_API_KEY"
    GOOGLE_API_KEY = "GOOGLE_API_KEY"
    COHERE_API_KEY = "COHERE_API_KEY"
    GROQ_API_KEY = "GROQ_API_KEY"
    NVIDIA_API_KEY = "NVIDIA_API_KEY"
    FIREWORKS_API_KEY = "FIREWORKS_API_KEY"
    MISTRAL_API_KEY = "MISTRAL_API_KEY"
    TOGETHER_API_KEY = "TOGETHER_API_KEY"
    XAI_API_KEY = "XAI_API_KEY"
    PPLX_API_KEY = "PPLX_API_KEY"  # Perplexity
    HUGGINGFACE_API_KEY = "HUGGINGFACE_API_KEY"
    DEEPSEEK_API_KEY = "DEEPSEEK_API_KEY"
    IBM_API_KEY = "IBM_API_KEY"
    EXA_API_KEY = "EXA_API_KEY"  # For search functionality
    SERPAPI_API_KEY = "SERPAPI_API_KEY"  # For search functionality
    E2B_API_KEY = "E2B_API_KEY"


class ApiKeyMode(str, Enum):

    BYO_KEYS = "byo_keys"
    PLATFORM = "platform"


class ModelType(str, Enum):
    """Types of models available for configuration."""

    CHEAP_MODEL = "CHEAP_MODEL"
    FAST_MODEL = "FAST_MODEL"
    SMART_MODEL = "SMART_MODEL"
    REASONING_MODEL = "REASONING_MODEL"
    VISION_MODEL = "VISION_MODEL"


class ModelProvider(str, Enum):
    """Supported model providers."""

    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    AZURE_OPENAI = "azure_openai"
    AZURE_AI = "azure_ai"
    GOOGLE_VERTEXAI = "google_vertexai"
    GOOGLE_GENAI = "google_genai"
    BEDROCK = "bedrock"
    BEDROCK_CONVERSE = "bedrock_converse"
    COHERE = "cohere"
    FIREWORKS = "fireworks"
    TOGETHER = "together"
    MISTRALAI = "mistralai"
    HUGGINGFACE = "huggingface"
    GROQ = "groq"
    OLLAMA = "ollama"
    GOOGLE_ANTHROPIC_VERTEX = "google_anthropic_vertex"
    DEEPSEEK = "deepseek"
    IBM = "ibm"
    NVIDIA = "nvidia"
    XAI = "xai"
    PERPLEXITY = "perplexity"
