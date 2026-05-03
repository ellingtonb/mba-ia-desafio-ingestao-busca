from sqlalchemy import create_engine, text
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_postgres import PGVector
from langchain_core.documents import Document
from config import get_file_path, get_collection_name, get_connection_string, get_provider_name
from commons import get_embeddings, select_provider, get_collection_data_size


def delete_collection_data():
    engine = create_engine(get_connection_string())

    with engine.begin() as connection:
        collection = connection.execute(
            text("""
                SELECT uuid AS collection_id FROM langchain_pg_collection
                WHERE name = :collection_name
            """),
            {"collection_name": get_collection_name()}
        ).fetchone()

        if collection is not None and collection.collection_id:
            connection.execute(
                text("""
                    DELETE FROM langchain_pg_embedding
                    WHERE collection_id = :collection_id
                """),
                {"collection_id": collection.collection_id}
            )

            connection.execute(
                text("""
                    DELETE FROM langchain_pg_collection
                    WHERE uuid = :collection_id
                """),
                {"collection_id": collection.collection_id}
            )

            print(
                f"Dados da collection '{get_collection_name()}' ({collection.collection_id}) removidos com sucesso. "
                "Iniciando nova ingestão..."
            )
        else:
            raise RuntimeError(f"Collection '{get_collection_name()}' não encontrada. Ingestão cancelada.")


def confirm_collection_cleanup():
    data_count = get_collection_data_size()

    if data_count is None:
        return

    confirmation = input(
        "Deseja excluir os dados existentes antes de executar uma nova ingestão? [s/N]: "
    ).strip().lower()

    if confirmation not in ("s", "sim", "y", "yes"):
        raise RuntimeError("Ingestão cancelada pelo usuário.")

    delete_collection_data()


def read_pdf_chunks(pdf_path, chunk_size, chunk_overlap):
    loader = PyPDFLoader(pdf_path)
    docs = loader.load()

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        add_start_index=False
    )

    chunks = splitter.split_documents(docs)
    if not chunks:
        raise ValueError("No chunks were returned from the file!")

    return chunks


def enrich_chunks_as_documents(chunks):
    enriched = [
        Document(
            page_content=chunk.page_content,
            metadata={k: v for k, v in chunk.metadata.items() if v not in ("", None)}
        )
        for chunk in chunks
    ]

    if enriched in (None, []):
        raise ValueError("No chunks were enriched!")

    return enriched


def ingest_pdf():
    chunks = read_pdf_chunks(pdf_path=get_file_path(), chunk_size=1000, chunk_overlap=150)

    documents = enrich_chunks_as_documents(chunks)

    store = PGVector(
        embeddings=get_embeddings(),
        collection_name=get_collection_name(),
        connection=get_connection_string(),
        use_jsonb=True
    )

    ids = [f"doc-{get_provider_name()}-{i}" for i in range(len(documents))]

    store.add_documents(documents, ids=ids)

    print("Dados ingeridos com sucesso!")


if __name__ == "__main__":
    select_provider()
    confirm_collection_cleanup()
    ingest_pdf()