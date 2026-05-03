from commons import select_provider
from search import search_prompt


def main():
    select_provider()

    question = input("Digite sua pergunta: ")

    chain = search_prompt()

    if not chain:
        print("Não foi possível iniciar o chat. Verifique os erros de inicialização.")
        return

    result = chain.invoke({"pergunta": question})

    print(f"\nRESPOSTA: {result.content}\n")

    pass

if __name__ == "__main__":
    main()