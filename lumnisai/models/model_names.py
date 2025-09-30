"""
Model Catalog for Lumnis API

Provides easy-to-use constants for all supported model names.
Instead of typing "openai:gpt-4.1-mini", you can use Models.GPT_4_1_MINI.

Example:
    >>> from lumnisai import AgentConfig, Models
    >>> config = AgentConfig(
    ...     coordinator_model_name=Models.GPT_4O,
    ...     planner_model_name=Models.GPT_4O,
    ...     fast_model_name=Models.GPT_4O_MINI
    ... )
"""


class Models:
    """
    Constants for all supported model names in the Lumnis API.
    
    Use these constants instead of typing model name strings manually.
    Provides IDE autocomplete and prevents typos.
    
    Example:
        >>> config = AgentConfig(
        ...     coordinator_model_name=Models.O3,
        ...     planner_model_name=Models.GPT_4O
        ... )
    """
    
    # ==================== OpenAI Models ====================
    
    # GPT-5 Series (Latest)
    GPT_5 = "openai:gpt-5"
    """OpenAI GPT-5 - Next generation model"""
    
    GPT_5_MINI = "openai:gpt-5-mini"
    """OpenAI GPT-5-mini - Efficient next generation"""
    
    GPT_5_NANO = "openai:gpt-5-nano"
    """OpenAI GPT-5-nano - Ultra-efficient next generation"""
    
    # O-Series Reasoning Models
    O3 = "openai:o3"
    """OpenAI o3 - Advanced reasoning model (default for REASONING_MODEL)"""
    
    O3_MINI = "openai:o3-mini"
    """OpenAI o3-mini - Compact reasoning model"""
    
    O4_MINI = "openai:o4-mini"
    """OpenAI o4-mini - Next-gen compact reasoning"""
    
    O1 = "openai:o1"
    """OpenAI o1 - Previous generation reasoning model"""
    
    O1_MINI = "openai:o1-mini"
    """OpenAI o1-mini - Compact reasoning model"""
    
    O1_PREVIEW = "openai:o1-preview"
    """OpenAI o1-preview - Preview reasoning model"""
    
    O1_PRO = "openai:o1-pro"
    """OpenAI o1-pro - Professional reasoning model"""
    
    # GPT-4.1 Series
    GPT_4_1 = "openai:gpt-4.1"
    """OpenAI GPT-4.1 - Latest generation model"""
    
    GPT_4_1_MINI = "openai:gpt-4.1-mini"
    """OpenAI GPT-4.1-mini - Efficient latest generation"""
    
    GPT_4_1_NANO = "openai:gpt-4.1-nano"
    """OpenAI GPT-4.1-nano - Ultra-efficient model"""
    
    # GPT-4o Series
    GPT_4O = "openai:gpt-4o"
    """OpenAI GPT-4o - High-quality general-purpose model"""
    
    GPT_4O_MINI = "openai:gpt-4o-mini"
    """OpenAI GPT-4o-mini - Efficient general-purpose model"""
    
    GPT_4O_MINI_2024_07_18 = "openai:gpt-4o-mini-2024-07-18"
    """OpenAI GPT-4o-mini - Specific snapshot from July 2024"""
    
    # GPT-4 Classic Series
    GPT_4 = "openai:gpt-4"
    """OpenAI GPT-4 - Original GPT-4 model"""
    
    GPT_4_TURBO = "openai:gpt-4-turbo"
    """OpenAI GPT-4-turbo - Faster GPT-4 variant"""
    
    GPT_4_TURBO_PREVIEW = "openai:gpt-4-turbo-preview"
    """OpenAI GPT-4-turbo-preview - Preview of turbo model"""
    
    # GPT-3.5 Series
    GPT_3_5_TURBO = "openai:gpt-3.5-turbo"
    """OpenAI GPT-3.5-turbo - Cost-effective model"""
    
    GPT_3_5_TURBO_16K = "openai:gpt-3.5-turbo-16k"
    """OpenAI GPT-3.5-turbo-16k - Extended context variant"""
    
    # ==================== Anthropic Models ====================
    
    # Claude 3.7 Series
    CLAUDE_3_7_SONNET = "anthropic:claude-3-7-sonnet-20250219"
    """Anthropic Claude 3.7 Sonnet - Latest high-quality reasoning"""
    
    # Claude 3.5 Series
    CLAUDE_3_5_SONNET = "anthropic:claude-3-5-sonnet"
    """Anthropic Claude 3.5 Sonnet - Balanced performance"""
    
    CLAUDE_3_5_SONNET_20241022 = "anthropic:claude-3-5-sonnet-20241022"
    """Anthropic Claude 3.5 Sonnet - Specific snapshot from October 2024"""
    
    CLAUDE_3_5_HAIKU = "anthropic:claude-3-5-haiku"
    """Anthropic Claude 3.5 Haiku - Fast and efficient"""
    
    # Claude 3 Series
    CLAUDE_3_OPUS = "anthropic:claude-3-opus"
    """Anthropic Claude 3 Opus - Most capable Claude 3 model"""
    
    CLAUDE_3_OPUS_20240229 = "anthropic:claude-3-opus-20240229"
    """Anthropic Claude 3 Opus - Specific snapshot from February 2024"""
    
    CLAUDE_3_SONNET = "anthropic:claude-3-sonnet"
    """Anthropic Claude 3 Sonnet - Balanced Claude 3 model"""
    
    CLAUDE_3_SONNET_20240229 = "anthropic:claude-3-sonnet-20240229"
    """Anthropic Claude 3 Sonnet - Specific snapshot from February 2024"""
    
    CLAUDE_3_HAIKU = "anthropic:claude-3-haiku"
    """Anthropic Claude 3 Haiku - Fast Claude 3 model"""
    
    CLAUDE_3_HAIKU_20240307 = "anthropic:claude-3-haiku-20240307"
    """Anthropic Claude 3 Haiku - Specific snapshot from March 2024"""
    
    # ==================== Google Models ====================
    
    # Gemini 2.5 Series
    GEMINI_2_5_PRO = "google_genai:gemini-2.5-pro"
    """Google Gemini 2.5 Pro - Advanced multimodal model"""
    
    GEMINI_2_5_FLASH = "google_genai:gemini-2.5-flash"
    """Google Gemini 2.5 Flash - Fast multimodal model"""
    
    # Gemini 2.0 Series
    GEMINI_2_0_FLASH = "google_genai:gemini-2.0-flash"
    """Google Gemini 2.0 Flash - Efficient multimodal model"""
    
    GEMINI_2_0_FLASH_LITE = "google_genai:gemini-2.0-flash-lite"
    """Google Gemini 2.0 Flash Lite - Ultra-efficient multimodal"""
    
    # Gemini 1.5 Series
    GEMINI_1_5_PRO = "google_genai:gemini-1.5-pro"
    """Google Gemini 1.5 Pro - Previous generation pro model"""
    
    GEMINI_1_5_FLASH = "google_genai:gemini-1.5-flash"
    """Google Gemini 1.5 Flash - Previous generation flash model"""
    
    # Gemma Series (Open source)
    GEMMA_3 = "google_genai:gemma-3"
    """Google Gemma 3 - Latest open source model"""
    
    GEMMA_2 = "google_genai:gemma-2"
    """Google Gemma 2 - Previous generation open source model"""
    
    # ==================== DeepSeek Models ====================
    
    DEEPSEEK_CHAT = "deepseek:deepseek-chat"
    """DeepSeek Chat - Latest DeepSeek v3 model"""
    
    DEEPSEEK_V3 = "deepseek:deepseek-v3"
    """DeepSeek v3 - Third generation model"""
    
    DEEPSEEK_REASONER = "deepseek:deepseek-reasoner"
    """DeepSeek Reasoner - DeepSeek r1 reasoning model"""
    
    DEEPSEEK_R1 = "deepseek:deepseek-r1"
    """DeepSeek R1 - First generation reasoning model"""
    
    DEEPSEEK_CODER = "deepseek:deepseek-coder"
    """DeepSeek Coder - Specialized for code generation"""
    
    # ==================== Qwen Models ====================
    
    QWEN_2_5_CODER_32B = "qwen:qwen2.5-coder-32b"
    """Qwen 2.5 Coder 32B - Code-specialized model"""
    
    QWEN_2_5_72B = "qwen:qwen2.5-72b"
    """Qwen 2.5 72B - Large general-purpose model"""
    
    QWEN_2_5_72B_INSTRUCT = "qwen:qwen2.5-72b-instruct"
    """Qwen 2.5 72B Instruct - Instruction-tuned variant"""
    
    QWEN_2_5_32B = "qwen:qwen2.5-32b"
    """Qwen 2.5 32B - Medium general-purpose model"""
    
    QWEN_2_5_14B = "qwen:qwen2.5-14b"
    """Qwen 2.5 14B - Efficient general-purpose model"""
    
    QWEN_2_5_7B = "qwen:qwen2.5-7b"
    """Qwen 2.5 7B - Compact general-purpose model"""
    
    QWEN_2_5_3B = "qwen:qwen2.5-3b"
    """Qwen 2.5 3B - Ultra-compact model"""
    
    QWQ = "qwen:qwq"
    """Qwen with Questions (QwQ) - Reasoning-focused model"""
    
    QWQ_32B_PREVIEW = "qwen:qwq-32b-preview"
    """Qwen with Questions 32B Preview - Preview reasoning model"""
    
    # ==================== Mistral Models ====================
    
    MISTRAL_LARGE = "mistralai:mistral-large"
    """Mistral Large - Most capable Mistral model"""
    
    MISTRAL_MEDIUM = "mistralai:mistral-medium"
    """Mistral Medium - Balanced Mistral model"""
    
    MISTRAL_SMALL = "mistralai:mistral-small"
    """Mistral Small - Efficient Mistral model"""
    
    MISTRAL_7B_INSTRUCT = "mistralai:mistral-7b-instruct"
    """Mistral 7B Instruct - Compact instruction-tuned model"""
    
    MISTRAL_NEMO = "mistralai:mistral-nemo"
    """Mistral Nemo - Extended context model"""
    
    MIXTRAL_8X7B = "mistralai:mixtral-8x7b"
    """Mixtral 8x7B - Mixture of experts model"""
    
    MIXTRAL_8X22B = "mistralai:mixtral-8x22b"
    """Mixtral 8x22B - Large mixture of experts model"""
    
    # ==================== Meta Llama Models ====================
    
    LLAMA_3_3_70B = "meta:llama-3.3-70b"
    """Meta Llama 3.3 70B - Latest large Llama model"""
    
    LLAMA_3_2_90B = "meta:llama-3.2-90b"
    """Meta Llama 3.2 90B - Very large Llama model"""
    
    LLAMA_3_2_70B = "meta:llama-3.2-70b"
    """Meta Llama 3.2 70B - Large Llama model"""
    
    LLAMA_3_1_405B = "meta:llama-3.1-405b"
    """Meta Llama 3.1 405B - Largest Llama model"""
    
    LLAMA_3_1_70B = "meta:llama-3.1-70b"
    """Meta Llama 3.1 70B - Large Llama 3.1 model"""
    
    LLAMA_3_1_8B = "meta:llama-3.1-8b"
    """Meta Llama 3.1 8B - Compact Llama 3.1 model"""
    
    LLAMA_3_70B = "meta:llama-3-70b"
    """Meta Llama 3 70B - Original large Llama 3"""
    
    LLAMA_3_8B = "meta:llama-3-8b"
    """Meta Llama 3 8B - Original compact Llama 3"""
    
    # ==================== Microsoft Phi Models ====================
    
    PHI_4 = "microsoft:phi-4"
    """Microsoft Phi-4 - Latest small language model"""
    
    PHI_3 = "microsoft:phi-3"
    """Microsoft Phi-3 - Capable small model"""
    
    PHI_3_MEDIUM = "microsoft:phi-3-medium"
    """Microsoft Phi-3 Medium - Medium-sized variant"""
    
    PHI_3_MINI = "microsoft:phi-3-mini"
    """Microsoft Phi-3 Mini - Compact variant"""
    
    # ==================== Cohere Models ====================
    
    COMMAND_R_PLUS = "cohere:command-r-plus"
    """Cohere Command R+ - Most capable Command R model"""
    
    COMMAND_R = "cohere:command-r"
    """Cohere Command R - Efficient Command R model"""
    
    # ==================== xAI Models ====================
    
    GROK_2 = "xai:grok-2"
    """xAI Grok 2 - Latest Grok model"""
    
    GROK_2_MINI = "xai:grok-2-mini"
    """xAI Grok 2 Mini - Efficient Grok model"""
    
    # ==================== Other Models ====================
    
    YI_LARGE = "01ai:yi-large"
    """01.AI Yi Large - Large Yi model"""
    
    YI_34B = "01ai:yi-34b"
    """01.AI Yi 34B - Compact Yi model"""
    
    @classmethod
    def all_models(cls) -> list[str]:
        """
        Get a list of all available model names.
        
        Returns:
            List of all model name strings
            
        Example:
            >>> models = ModelName.all_models()
            >>> print(models)
            ['openai:o3', 'openai:o3-mini', ...]
        """
        return [
            value for name, value in vars(cls).items()
            if not name.startswith('_') and isinstance(value, str)
        ]
    
    @classmethod
    def openai_models(cls) -> list[str]:
        """Get all OpenAI model names."""
        return [m for m in cls.all_models() if m.startswith('openai:')]
    
    @classmethod
    def anthropic_models(cls) -> list[str]:
        """Get all Anthropic model names."""
        return [m for m in cls.all_models() if m.startswith('anthropic:')]
    
    @classmethod
    def google_models(cls) -> list[str]:
        """Get all Google model names."""
        return [m for m in cls.all_models() if m.startswith('google_genai:')]
    
    @classmethod
    def deepseek_models(cls) -> list[str]:
        """Get all DeepSeek model names."""
        return [m for m in cls.all_models() if m.startswith('deepseek:')]
    
    @classmethod
    def qwen_models(cls) -> list[str]:
        """Get all Qwen model names."""
        return [m for m in cls.all_models() if m.startswith('qwen:')]
    
    @classmethod
    def mistral_models(cls) -> list[str]:
        """Get all Mistral model names."""
        return [m for m in cls.all_models() if m.startswith('mistralai:')]
    
    @classmethod
    def llama_models(cls) -> list[str]:
        """Get all Meta Llama model names."""
        return [m for m in cls.all_models() if m.startswith('meta:')]
    
    @classmethod
    def microsoft_models(cls) -> list[str]:
        """Get all Microsoft model names."""
        return [m for m in cls.all_models() if m.startswith('microsoft:')]
    
    @classmethod
    def cohere_models(cls) -> list[str]:
        """Get all Cohere model names."""
        return [m for m in cls.all_models() if m.startswith('cohere:')]
    
    @classmethod
    def xai_models(cls) -> list[str]:
        """Get all xAI model names."""
        return [m for m in cls.all_models() if m.startswith('xai:')]


# Aliases for backward compatibility and convenience
class OpenAIModels:
    """OpenAI-specific model names (convenience class)."""
    # GPT-5 Series
    GPT_5 = Models.GPT_5
    GPT_5_MINI = Models.GPT_5_MINI
    GPT_5_NANO = Models.GPT_5_NANO
    # O-Series
    O3 = Models.O3
    O3_MINI = Models.O3_MINI
    O4_MINI = Models.O4_MINI
    O1 = Models.O1
    O1_MINI = Models.O1_MINI
    O1_PREVIEW = Models.O1_PREVIEW
    O1_PRO = Models.O1_PRO
    # GPT-4.1 Series
    GPT_4_1 = Models.GPT_4_1
    GPT_4_1_MINI = Models.GPT_4_1_MINI
    GPT_4_1_NANO = Models.GPT_4_1_NANO
    # GPT-4o Series
    GPT_4O = Models.GPT_4O
    GPT_4O_MINI = Models.GPT_4O_MINI
    GPT_4O_MINI_2024_07_18 = Models.GPT_4O_MINI_2024_07_18
    # GPT-4 Classic
    GPT_4 = Models.GPT_4
    GPT_4_TURBO = Models.GPT_4_TURBO
    GPT_4_TURBO_PREVIEW = Models.GPT_4_TURBO_PREVIEW
    # GPT-3.5
    GPT_3_5_TURBO = Models.GPT_3_5_TURBO
    GPT_3_5_TURBO_16K = Models.GPT_3_5_TURBO_16K


class AnthropicModels:
    """Anthropic-specific model names (convenience class)."""
    # Claude 3.7
    CLAUDE_3_7_SONNET = Models.CLAUDE_3_7_SONNET
    # Claude 3.5
    CLAUDE_3_5_SONNET = Models.CLAUDE_3_5_SONNET
    CLAUDE_3_5_SONNET_20241022 = Models.CLAUDE_3_5_SONNET_20241022
    CLAUDE_3_5_HAIKU = Models.CLAUDE_3_5_HAIKU
    # Claude 3
    CLAUDE_3_OPUS = Models.CLAUDE_3_OPUS
    CLAUDE_3_OPUS_20240229 = Models.CLAUDE_3_OPUS_20240229
    CLAUDE_3_SONNET = Models.CLAUDE_3_SONNET
    CLAUDE_3_SONNET_20240229 = Models.CLAUDE_3_SONNET_20240229
    CLAUDE_3_HAIKU = Models.CLAUDE_3_HAIKU
    CLAUDE_3_HAIKU_20240307 = Models.CLAUDE_3_HAIKU_20240307


class GoogleModels:
    """Google-specific model names (convenience class)."""
    # Gemini 2.5
    GEMINI_2_5_PRO = Models.GEMINI_2_5_PRO
    GEMINI_2_5_FLASH = Models.GEMINI_2_5_FLASH
    # Gemini 2.0
    GEMINI_2_0_FLASH = Models.GEMINI_2_0_FLASH
    GEMINI_2_0_FLASH_LITE = Models.GEMINI_2_0_FLASH_LITE
    # Gemini 1.5
    GEMINI_1_5_PRO = Models.GEMINI_1_5_PRO
    GEMINI_1_5_FLASH = Models.GEMINI_1_5_FLASH
    # Gemma
    GEMMA_3 = Models.GEMMA_3
    GEMMA_2 = Models.GEMMA_2


class DeepSeekModels:
    """DeepSeek-specific model names (convenience class)."""
    DEEPSEEK_CHAT = Models.DEEPSEEK_CHAT
    DEEPSEEK_V3 = Models.DEEPSEEK_V3
    DEEPSEEK_REASONER = Models.DEEPSEEK_REASONER
    DEEPSEEK_R1 = Models.DEEPSEEK_R1
    DEEPSEEK_CODER = Models.DEEPSEEK_CODER
