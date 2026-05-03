import os
from sqlalchemy import create_engine, text
from langchain_openai import OpenAIEmbeddings
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from config import DEFAULT_PROVIDER, VALID_PROVIDERS, get_connection_string, get_collection_name, get_provider_name, get_embedding_model, get_provider_key, get_response_model, get_embedding_dimensions, validate_provider_config


def get_collection_data_size():
    engine = create_engine(get_connection_string())

    query = text("""
        SELECT 
            c.uuid AS collection_id,
            COUNT(e.id) AS total_embeddings
        FROM langchain_pg_collection c
        LEFT JOIN langchain_pg_embedding e 
            ON e.collection_id = c.uuid
        WHERE c.name = :collection_name
        GROUP BY c.uuid
    """)

    with engine.connect() as connection:
        result = connection.execute(
            query,
            {"collection_name": get_collection_name()}
        ).fetchone()

    return result


def select_provider():
    while True:
        provider = input("Selecione o provider [google/openai] (default: openai): ").strip().lower()

        if not provider:
            provider = DEFAULT_PROVIDER

        if provider in VALID_PROVIDERS:
            os.environ["PROVIDER"] = provider

            validate_provider_config()

            return provider

        print("Opção inválida. Digite 'google' ou 'openai'.")


def get_embeddings():
    provider = get_provider_name()

    if provider == "google":
        dimensions = get_embedding_dimensions()

        kwargs = {
            "model": get_embedding_model(),
            "google_api_key": get_provider_key(),
            "transport": "rest",
        }

        if dimensions is not None:
            kwargs["output_dimensionality"] = dimensions

        return GoogleGenerativeAIEmbeddings(**kwargs)
    elif provider == "openai":
        return OpenAIEmbeddings(model=get_embedding_model(), api_key=get_provider_key())
    else:
        raise ValueError(f"Invalid provider: {provider}")


def get_chat():
    if get_provider_name() == "google":
        return ChatGoogleGenerativeAI(
            model=get_response_model(),
            google_api_key=get_provider_key(),
            transport="rest",
            temperature=0.5
        )
    elif get_provider_name() == "openai":
        return ChatOpenAI(
            model=get_response_model(),
            api_key=get_provider_key(),
            temperature=0.5
        )
    else:
        raise ValueError(f"Provider '{get_provider_name()}' not supported")

