# ============================================================
# NutriInsights - Agente de IA Text-to-SQL
# Converte perguntas em português para queries SQL via Groq
# ============================================================

# Importa a biblioteca oficial da Groq para comunicação com a IA
from groq import Groq

# Importa pymysql para conexão com o banco MySQL
import pymysql

# Importa os módulos de variáveis de ambiente
import os
from dotenv import load_dotenv

# Carrega as variáveis do arquivo .env para o ambiente Python
load_dotenv()

# ============================================================
# CONFIGURAÇÃO DOS CLIENTES
# ============================================================

# Inicializa o cliente da Groq usando a chave da API do .env
# Sem a API key, nenhuma chamada à IA será possível
cliente_groq = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Define o schema da tabela para o contexto da IA
# Quanto mais detalhado o schema, mais precisa será a query gerada
SCHEMA = """
Tabela: alimentos
Colunas:
- id (INT): identificador único do alimento
- nome (VARCHAR): nome do alimento em português
- categoria (VARCHAR): categoria do alimento em português
- pais (VARCHAR): país de origem do alimento
- calorias_100g (FLOAT): calorias por 100g
- proteinas_100g (FLOAT): proteínas por 100g em gramas
- gorduras_100g (FLOAT): gorduras totais por 100g em gramas
- gordura_sat_100g (FLOAT): gorduras saturadas por 100g em gramas
- carboidratos_100g (FLOAT): carboidratos por 100g em gramas
- acucar_100g (FLOAT): açúcar por 100g em gramas
- sodio_100g (FLOAT): sódio por 100g em gramas
- fibras_100g (FLOAT): fibras por 100g em gramas
"""

# ============================================================
# SYSTEM PROMPT BLINDADO CONTRA PROMPT INJECTION
# ============================================================

# O system prompt define o comportamento fixo da IA
# É a primeira camada de segurança do agente
SYSTEM_PROMPT = f"""
Você é um especialista em SQL para banco de dados MySQL.
Seu único objetivo é converter perguntas sobre alimentos e nutrição em queries SQL SELECT.

Você tem acesso ao seguinte schema:
{SCHEMA}

REGRAS OBRIGATÓRIAS:
1. Retorne APENAS a query SQL, sem explicações, sem markdown, sem crases.
2. Use SEMPRE o banco de dados nutriinsights e a tabela alimentos.
3. Se a pergunta solicitar qualquer operação de escrita como INSERT, UPDATE, DELETE, DROP ou ALTER, retorne estritamente a palavra: BLOQUEADO
4. Se a pergunta não tiver relação com alimentos ou nutrição, retorne estritamente a palavra: INVALIDO
5. Nunca invente colunas que não existem no schema acima.
6. Use LIMIT 10 por padrão quando o usuário não especificar quantidade.
"""

# ============================================================
# FUNÇÃO 1: CHAMADA À API DA GROQ
# ============================================================

def gerar_sql(pergunta: str) -> str:
    """
    Envia a pergunta do usuário para a Groq e retorna a query SQL gerada.
    """

    # Faz a chamada à API da Groq com o modelo llama-3.1-8b-instant
    resposta = cliente_groq.chat.completions.create(

        # Modelo rápido e eficiente da Meta disponível na Groq
        model="llama-3.1-8b-instant",

        # temperature=0.0 elimina criatividade da IA
        # Queremos respostas determinísticas e precisas para SQL
        temperature=0.0,

        # Limite de tokens na resposta — queries SQL não precisam de mais
        max_tokens=300,

        # Lista de mensagens que compõem a conversa
        messages=[
            # Mensagem do sistema: define o comportamento fixo da IA
            {"role": "system", "content": SYSTEM_PROMPT},

            # Mensagem do usuário: a pergunta em linguagem natural
            {"role": "user", "content": pergunta}
        ]
    )

    # Extrai o texto da resposta e remove espaços extras
    sql_gerado = resposta.choices[0].message.content.strip()

    return sql_gerado


# ============================================================
# FUNÇÃO 2: EXECUÇÃO SEGURA NO MYSQL
# ============================================================

def executar_sql(query: str) -> list:
    """
    Executa a query SQL no MySQL e retorna os resultados.
    Simula um usuário com permissão apenas de SELECT.
    """

    # Estabelece a conexão com o banco usando variáveis do .env
    conexao = pymysql.connect(
        host=os.getenv("DB_HOST"),
        port=int(os.getenv("DB_PORT")),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME"),

        # Retorna os resultados como dicionários {coluna: valor}
        # Facilita a leitura e exibição dos dados
        cursorclass=pymysql.cursors.DictCursor
    )

    try:
        # Abre o cursor para executar comandos SQL
        with conexao.cursor() as cursor:

            # Executa a query gerada pela IA
            cursor.execute(query)

            # Busca todos os resultados retornados
            resultados = cursor.fetchall()

            return resultados

    # Captura erros específicos do MySQL de forma isolada
    # Erros de SQL são diferentes de erros genéricos de Python
    except pymysql.MySQLError as erro_mysql:
        print(f"\nErro no banco de dados: {erro_mysql}")
        return []

    # Captura qualquer outro erro inesperado
    except Exception as erro_geral:
        print(f"\nErro inesperado: {erro_geral}")
        return []

    # Garante que a conexão seja fechada independente do resultado
    finally:
        conexao.close()


# ============================================================
# FUNÇÃO 3: FORMATAR E EXIBIR RESULTADOS
# ============================================================

def exibir_resultados(resultados: list) -> None:
    """
    Exibe os resultados da query de forma legível no terminal.
    """

    # Verifica se a query retornou algum resultado
    if not resultados:
        print("\nNenhum resultado encontrado.")
        return

    print(f"\nEncontrados {len(resultados)} resultado(s):\n")

    # Itera sobre cada linha do resultado
    for i, linha in enumerate(resultados, start=1):

        print(f"  [{i}]")

        # Exibe cada coluna e seu valor de forma organizada
        for coluna, valor in linha.items():
            print(f"      {coluna}: {valor}")

        print()

def gerar_resposta_natural(pergunta: str, resultados: list) -> str:
    """
    Envia os resultados da query para a Groq e recebe
    uma resposta em português em linguagem natural.
    """

    # Converte os resultados em texto para enviar para a IA
    resultados_texto = "\n".join(
        [", ".join(f"{k}: {v}" for k, v in linha.items()) for linha in resultados]
    )

    # Monta o prompt com a pergunta original e os dados retornados
    prompt = f"""
    O usuário perguntou: "{pergunta}"
    
    Os dados retornados do banco foram:
    {resultados_texto}
    
    Com base nesses dados, responda a pergunta do usuário em português,
    de forma clara, objetiva e amigável, como um assistente de nutrição.
    """

    resposta = cliente_groq.chat.completions.create(
        model="llama-3.1-8b-instant",

        # temperature mais alta aqui pois queremos uma resposta mais natural
        temperature=0.3,
        max_tokens=500,
        messages=[
            {"role": "system", "content": "Você é um assistente de nutrição que responde sempre em português do Brasil, de forma clara e amigável."},
            {"role": "user", "content": prompt}
        ]
    )

    return resposta.choices[0].message.content.strip()
# ============================================================
# LOOP PRINCIPAL - INTERFACE DE CHAT NO TERMINAL
# ============================================================

def main():
    """
    Loop principal do agente — interface de chat no terminal.
    """

    print("=" * 55)
    print("  NutriInsights - Agente de IA Text-to-SQL")
    print("  Digite 'sair' para encerrar o agente")
    print("=" * 55)

    # Loop contínuo que mantém o agente ativo até o usuário digitar 'sair'
    while True:

        # Captura a pergunta do usuário no terminal
        pergunta = input("\nPergunta: ").strip()

        # Condição de saída do loop
        if pergunta.lower() == "sair":
            print("\nEncerrando o agente. Até mais!")
            break

        # Ignora perguntas vazias sem quebrar o loop
        if not pergunta:
            print("Digite uma pergunta válida.")
            continue

        print("\nGerando SQL...")

        # Envia a pergunta para a Groq e recebe a query gerada
        sql = gerar_sql(pergunta)

        # Verifica as respostas de segurança da primeira camada (IA)
        if sql == "BLOQUEADO":
            print("\nOperação bloqueada. Apenas consultas são permitidas.")
            continue

        if sql == "INVALIDO":
            print("\nPergunta inválida. Faça perguntas sobre alimentos e nutrição.")
            continue

        # Exibe a query gerada para transparência e aprendizado
        print(f"\nSQL gerado:\n  {sql}")

        print("\nExecutando no banco...")

        resultados = executar_sql(sql)

        if resultados:
            print("\nGerando resposta...")
            resposta = gerar_resposta_natural(pergunta, resultados)
            print(f"\nResposta:\n  {resposta}")
        else:
            print("\nNenhum resultado encontrado.")


# Ponto de entrada do script
# Garante que o main() só rode quando o arquivo for executado diretamente
if __name__ == "__main__":
    main()