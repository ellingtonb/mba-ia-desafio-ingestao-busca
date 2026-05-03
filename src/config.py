import os
from dotenv import load_dotenv

load_dotenv()

DEFAULT_PROVIDER = os.getenv("DEFAULT_PROVIDER", "openai")
VALID_PROVIDERS = ["google", "openai"]

DEFAULT_GOOGLE_EMBEDDING_DIMENSIONS = 768

REQUIRED_ENV_VARS = (
    "PDF_PATH",
    "PG_VECTOR_COLLECTION_NAME",
    "DATABASE_URL",
    "PROVIDER",
)

PROVIDER_REQUIRED_ENV_VARS = {
    "google": (
        "GOOGLE_API_KEY",
        "GOOGLE_EMBEDDING_MODEL",
        "GOOGLE_EMBEDDING_DIMENSIONS",
        "GOOGLE_RESPONSE_MODEL",
    ),
    "openai": (
        "OPENAI_API_KEY",
        "OPENAI_EMBEDDING_MODEL",
        "OPENAI_RESPONSE_MODEL",
    ),
}


def require_env_vars(keys, provider=""):
    context = f" for provider {provider}" if provider else ""
    for key in keys:
        if not os.getenv(key) and key != "PROVIDER" and key != "GOOGLE_EMBEDDING_DIMENSIONS":
            raise RuntimeError(f"Environment variable {key} is not set{context}!")


def validate_config():
    require_env_vars(REQUIRED_ENV_VARS)

    pdf_path = os.getenv("PDF_PATH")
    if pdf_path and not os.path.exists(pdf_path):
        raise FileNotFoundError(f"The file {pdf_path} does not exist!")


def validate_provider_config():
    provider_name = os.getenv("PROVIDER")
    if not provider_name:
        provider_name = DEFAULT_PROVIDER
        os.environ["PROVIDER"] = provider_name

    provider_required_env_vars = PROVIDER_REQUIRED_ENV_VARS.get(provider_name, ())
    if provider_name not in VALID_PROVIDERS or not provider_required_env_vars:
        raise ValueError(f"Invalid provider: {provider_name}")

    require_env_vars(provider_required_env_vars, provider_name)


def get_embedding_model():
    provider = os.getenv("PROVIDER")

    validate_provider_config()

    if provider == "google":
        return os.getenv("GOOGLE_EMBEDDING_MODEL")
    elif provider == "openai":
        return os.getenv("OPENAI_EMBEDDING_MODEL")
    else:
        raise ValueError(f"Invalid provider: {provider}")


def get_embedding_dimensions():
    value = os.getenv("GOOGLE_EMBEDDING_DIMENSIONS", DEFAULT_GOOGLE_EMBEDDING_DIMENSIONS)

    if value in (None, ""):
        return None

    return int(value)


def get_response_model():
    provider = os.getenv("PROVIDER")

    validate_provider_config()

    if provider == "google":
        return os.getenv("GOOGLE_RESPONSE_MODEL")
    elif provider == "openai":
        return os.getenv("OPENAI_RESPONSE_MODEL")
    else:
        raise ValueError(f"Invalid provider: {provider}")


def get_provider_key():
    provider = os.getenv("PROVIDER")

    validate_provider_config()

    if provider == "google":
        return os.getenv("GOOGLE_API_KEY")
    elif provider == "openai":
        return os.getenv("OPENAI_API_KEY")
    else:
        raise ValueError(f"Invalid provider: {provider}")


def get_provider_name():
    validate_provider_config()

    return os.getenv("PROVIDER")


def get_collection_name():
    validate_provider_config()

    return f"{os.getenv("PG_VECTOR_COLLECTION_NAME")}_{get_provider_name()}"


def get_connection_string():
    return os.getenv("DATABASE_URL")


def get_file_path():
    return os.getenv("PDF_PATH")


validate_config()