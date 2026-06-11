import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

def conectar() -> mysql.connector.MySQLConnection:
    """
    Cria e retorna uma conexão com o banco MySQL
    usando as credenciais do arquivo .env
    """
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        port=int(os.getenv("DB_PORT")),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )


def inserir_alimentos(dados: list) -> None:
    """
    Insere uma lista de alimentos na tabela alimentos do MySQL.
    Ignora registros duplicados pelo nome.
    """
    sql = """
        INSERT IGNORE INTO alimentos (
            nome, categoria, pais,
            calorias_100g, proteinas_100g, gorduras_100g,
            gordura_sat_100g, carboidratos_100g, acucar_100g,
            sodio_100g, fibras_100g
        ) VALUES (
            %(nome)s, %(categoria)s, %(pais)s,
            %(calorias_100g)s, %(proteinas_100g)s, %(gorduras_100g)s,
            %(gordura_sat_100g)s, %(carboidratos_100g)s, %(acucar_100g)s,
            %(sodio_100g)s, %(fibras_100g)s
        )
    """

    conexao = conectar()
    cursor = conexao.cursor()

    cursor.executemany(sql, dados)
    conexao.commit()

    print(f"{cursor.rowcount} alimentos inseridos no banco.")

    cursor.close()
    conexao.close()