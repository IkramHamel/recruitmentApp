from enum import Enum



class Providers(str,Enum):
    GroqCloud = "GroqCloud"
    Gemini = "Gemini"


# List of supported providers
SUPPORTED_PROVIDERS = [Providers.Gemini,Providers.GroqCloud]