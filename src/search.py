from langchain.prompts import PromptTemplate
from langchain_postgres import PGVector
from langchain_core.runnables import RunnableLambda
from commons import get_embeddings, get_chat, get_collection_data_size
from config import get_collection_name, get_connection_string

PROMPT_TEMPLATE = """
CONTEXTO:
{contexto}

REGRAS:
- Responda somente com base no CONTEXTO.
- Se a informação não estiver explicitamente no CONTEXTO, responda:
  "Não tenho informações necessárias para responder sua pergunta."
- Nunca invente ou use conhecimento externo.
- Nunca produza opiniões ou interpretações além do que está escrito.

EXEMPLOS DE PERGUNTAS FORA DO CONTEXTO:
Pergunta: "Qual é a capital da França?"
Resposta: "Não tenho informações necessárias para responder sua pergunta."

Pergunta: "Quantos clientes temos em 2024?"
Resposta: "Não tenho informações necessárias para responder sua pergunta."

Pergunta: "Você acha isso bom ou ruim?"
Resposta: "Não tenho informações necessárias para responder sua pergunta."

PERGUNTA DO USUÁRIO:
{pergunta}

RESPONDA A "PERGUNTA DO USUÁRIO"
"""


def validate_collection_data_exists():
    data_count = get_collection_data_size()

    if data_count is None:
        raise ValueError(
            f"A collection '{get_collection_name()}' não existe no banco de dados. "
            "Execute primeiro o processo de ingestão (python src/ingest.py)."
        )

    if data_count.total_embeddings == 0:
        raise ValueError(
            f"A collection '{get_collection_name()}' existe, mas não possui documentos/embeddings. "
            "Execute novamente o processo de ingestão (python src/ingest.py)."
        )


def search_prompt():
    validate_collection_data_exists()

    chat_prompt = PromptTemplate(
        input_variables=["contexto", "pergunta"],
        template=PROMPT_TEMPLATE
    )

    embeddings = get_embeddings()

    store = PGVector(
        embeddings=embeddings,
        collection_name=get_collection_name(),
        connection=get_connection_string(),
        use_jsonb=True
    )

    def retrieve_context(input_data):
        question = input_data["pergunta"]

        if not question:
            raise ValueError("Question cannot be empty!")

        question_vector = embeddings.embed_query(question)

        results = store.similarity_search_with_score_by_vector(question_vector, k=10)

        contexto = "\n\n".join(
            document.page_content
            for document, score in results
        )

        return {
            "contexto": contexto,
            "pergunta": question
        }

    chain = RunnableLambda(retrieve_context) | chat_prompt | get_chat()

    return chain
