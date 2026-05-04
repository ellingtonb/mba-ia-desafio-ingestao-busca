# Ingestão e Busca Semântica com LangChain e Postgres

Essa aplicação foi desenvolvida para o desafio **MBA Engenharia de Software com IA - Full Cycle** para realizar as seguintes tarefas:

1. **Ingestão**: Ler um arquivo PDF e salvar suas informações em um banco de dados PostgreSQL com extensão pgVector.
2. **Busca**: Permitir que o usuário faça perguntas via linha de comando (CLI) e receba respostas baseadas apenas no conteúdo do PDF.

# Requisitos

A aplicação atual foi desenvolvida e testada com as seguintes tecnologias:
* Python 3.12
* LangChain 0.3.27
* PostgreSQL + pgVector 17
* Docker & Docker Compose

Os provedores e modelos de IA utilizados são:
* Google:
  * Embedding: `models/gemini-embedding-2`
  * Response: `gemini-2.5-flash-lite`
* OpenAI
  * Embedding: `text-embedding-3-small`
  * Response: `gpt-5-nano`

# Estrutura de Dados

Os embeddings do PDF devem ser salvos separadamente para cada provedor porque cada modelo de embedding, como os da OpenAI ou do Google, transforma o texto em vetores dentro de um espaço semântico próprio, com dimensões, distribuições e critérios internos de similaridade diferentes. Mesmo quando dois modelos geram vetores com o mesmo número de dimensões, esses vetores não são diretamente comparáveis entre si, pois foram treinados de formas distintas e representam os significados segundo referências diferentes. Por isso, para garantir que a busca vetorial retorne resultados coerentes, os documentos devem ser indexados com o mesmo provedor/modelo que será usado posteriormente para gerar o embedding da pergunta do usuário. Misturar embeddings de provedores diferentes na mesma coleção pode comprometer a precisão da recuperação e gerar respostas incorretas ou pouco relevantes.

Todos os dados consumidos são armazenados no banco de dados PostgreSQL com PGVector na estrutura abaixo para cada provedor de IA:

**Tabela**: `langchain_pg_collection`

| Coluna    | Tipo    | Descrição                                | 
|-----------|---------|------------------------------------------|
| uuid      | uuid    | ID randômico único para cada coleção     |
| name      | varchar | Nome da coleção (sufixo + google/openai) |
| cmetadata | json    | Metadados da coleção em formato JSON     |

**Tabela**: `langchain_pg_embedding`

| Coluna | Tipo | Descrição                                    |
|--------|------|----------------------------------------------|
| id | varchar | ID randômico único para cada embedding       |
| collection_id | uuid | ID da coleção (langchain_pg_collection) à qual o embedding pertence |
| embedding | vector | Vetor de embedding                           |
| document | varchar | Documento associado ao embedding             |
| cmetadata | jsonb | Metadados do embedding em formato JSON       |

# Execução

Para executar a aplicação, siga os passos abaixo:

## 1. Execução do Banco de Dados

Para executar o banco de dados usando Docker local necessário para a execução do script, execute o comando abaixo:

```shell
docker-compose up -d
```

## 2. Configuração de Variáveis de Ambiente

Copie o arquivo `.env.example` para `.env` e preencha as variáveis de ambiente necessárias:
* `GOOGLE_API_KEY`
* `OPENAI_API_KEY`

Obs.: Caso seja utilizado apenas o provedor da OpenAI ou Google, preencha apenas a variável de ambiente correspondente.

## 3. Criação de Ambiente Virtual Python

Para executar a aplicação, primeiro execute os comandos abaixo para preparar o ambiente virtual:

```shell
python3 -m venv venv
source venv/bin/activate
```

Obs.: Para sair do ambiente virtual, execute o comando `deactivate`.

## 4. Instalação das Dependências

Dentro do ambiente virtual, instale as dependências necessárias para execução da aplicação:

```shell
python -m pip install -r requirements.txt
```

## 5. Ingestão dos Dados

Para realizar a ingestão dos dados do arquivo `document.pdf`, execute o comando abaixo, onde será questionado qual provedor utilizar (openai ou google):

Apenas pressione ENTER para usar o provedor da OpenAI (padrão).

```shell
python src/ingest.py
```

Caso já tenha sido ingerido dados para um provedor de IA anteriormente, será solicitado autorização para excluir os dados existentes.

Para alterar informar outro arquivo, basta incluir o path + nome na variável de ambiente `PDF_PATH`.

Obs.: Deve ser realizado a ingestão dos dados para cada provedor (Google e OpenAI).

## 6. Execução do Chat

Execute o comando abaixo para iniciar o chat e inserir o prompt desejado, onde será questionado qual provedor utilizar:

```shell
python src/chat.py
```

Obs.: Deve ser realizado a ingestão prévia dos dados para cada provedor (Google e OpenAI).

# Exemplos

Alguns exemplos de ingestão e execução do chat com os provedores Google e OpenAI.

## OpenAI

Exemplos de ingestão e execução do chat com o provedor da OpenAI.

### Exemplo de Ingestão

```shell
python src/ingest.py

# Selecione o provider [google/openai] (default: openai): 
# Dados ingeridos com sucesso!
```

### Exemplo de Chat com Sucesso 1

```shell
python src/chat.py

# Selecione o provider [google/openai] (default: openai): 
# Digite sua pergunta: Qual o faturamento da Empresa SuperTechIABrazil?

# RESPOSTA: R$ 10.000.000,00
```

### Exemplo de Chat com Sucesso 2

```shell
python src/chat.py

# Selecione o provider [google/openai] (default: openai):
# Digite sua pergunta: Qual foi o ano de fundação e faturamento da empresa Aurora Educação EPP?

# RESPOSTA: Ano de fundação: 1958. Faturamento: R$ 4.321.211.894,95.
```

### Exemplo de Chat com Erro 1

```shell
python src/chat.py

# Selecione o provider [google/openai] (default: openai):
# Digite sua pergunta: Quantos clientes temos em 2024?

# RESPOSTA: Não tenho informações necessárias para responder sua pergunta.
```

### Exemplo de Chat com Erro 2

```shell
python src/chat.py

# Selecione o provider [google/openai] (default: openai): 
# Digite sua pergunta: Qual é o tamanho da base de dados?

# RESPOSTA: Não tenho informações necessárias para responder sua pergunta.
```

## Google

Exemplos de ingestão e execução do chat com o provedor do Google.

### Exemplo de Ingestão

```shell
python src/ingest.py

# Selecione o provider [google/openai] (default: openai): google
# Dados ingeridos com sucesso!
```

### Exemplo de Chat com Sucesso 1

```shell
python src/chat.py

# Selecione o provider [google/openai] (default: openai): google
# Digite sua pergunta: Qual o faturamento da Empresa SuperTechIABrazil?

# RESPOSTA: SuperTechIABrazil R$ 10.000.000,00
```

### Exemplo de Chat com Sucesso 2

```shell
python src/chat.py

# Selecione o provider [google/openai] (default: openai): google
# Digite sua pergunta: Qual foi o ano de fundação e faturamento da empresa Aurora Educação EPP?

# RESPOSTA: Aurora Educação EPP R$ 4.321.211.894,95 1958
```

### Exemplo de Chat com Erro 1

```shell
python src/chat.py

# Selecione o provider [google/openai] (default: openai): google
# Digite sua pergunta: Quantos clientes temos em 2024?

# RESPOSTA: Não tenho informações necessárias para responder sua pergunta.
```

### Exemplo de Chat com Erro 2

```shell
python src/chat.py

# Selecione o provider [google/openai] (default: openai): google
# Digite sua pergunta: Qual é o tamanho da base de dados?

# RESPOSTA: Não tenho informações necessárias para responder sua pergunta.
```
