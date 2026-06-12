import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv
from pathlib import Path
import os
from deep_translator import GoogleTranslator

load_dotenv()

def carregar_dados() -> pd.DataFrame:
    """
    Lê a tabela alimentos do MySQL e retorna um DataFrame.
    """
    usuario = os.getenv("DB_USER")
    senha = os.getenv("DB_PASSWORD")
    host = os.getenv("DB_HOST")
    porta = os.getenv("DB_PORT")
    banco = os.getenv("DB_NAME")

    engine = create_engine(f"mysql+mysqlconnector://{usuario}:{senha}@{host}:{porta}/{banco}")

    df = pd.read_sql("SELECT * FROM alimentos", engine)
    print(f"Dados carregados: {df.shape[0]} linhas e {df.shape[1]} colunas")
    return df


def traduzir_texto(texto: str) -> str:
    """
    Traduz um texto do inglês para o português.
    Retorna o texto original em caso de erro.
    """
    try:
        if pd.isna(texto) or texto.strip() == "":
            return texto
        return GoogleTranslator(source="en", target="pt").translate(texto)
    except:
        return texto


def limpar_dados(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aplica as etapas de limpeza no DataFrame.
    """

    # remove linhas onde nome está vazio
    df = df[df["nome"].str.strip() != ""]

    # remove linhas onde todos os nutrientes são nulos
    nutrientes = ["calorias_100g", "proteinas_100g", "gorduras_100g",
                  "gordura_sat_100g", "carboidratos_100g", "acucar_100g",
                  "sodio_100g", "fibras_100g"]
    df = df.dropna(subset=nutrientes, how="all")

    # preenche valores nulos com a mediana da coluna
    for col in nutrientes:
        mediana = df[col].median()
        df[col] = df[col].fillna(mediana)

    # remove outliers extremos de calorias (acima de 1000 kcal/100g)
    df = df[df["calorias_100g"] <= 1000]

    # padroniza o texto de categoria e pais antes de traduzir
    df["categoria"] = df["categoria"].str.strip().str.title()
    df["pais"]      = df["pais"].str.strip().str.title()

    # traduz nome e categoria para português
    print("Traduzindo nomes...")
    df["nome"] = df["nome"].apply(traduzir_texto)

    print("Traduzindo categorias...")
    # traduz categorias únicas para evitar chamadas repetidas
    categorias_unicas = df["categoria"].unique()
    mapa_categorias = {cat: traduzir_texto(cat) for cat in categorias_unicas}
    df["categoria"] = df["categoria"].map(mapa_categorias)

    # remove a coluna inserido_em (não é útil pro Power BI)
    df = df.drop(columns=["inserido_em"], errors="ignore")

    print(f"Dados após limpeza: {df.shape[0]} linhas e {df.shape[1]} colunas")
    return df


def exportar_csv(df: pd.DataFrame, nome_arquivo: str) -> None:
    """
    Exporta o DataFrame limpo como CSV na pasta data/processed.
    """
    caminho = Path("../data/processed") / nome_arquivo
    caminho.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(caminho, index=False, encoding="utf-8-sig")
    print(f"CSV exportado em: {caminho}")

def atualizar_banco(df: pd.DataFrame) -> None:
    """
    Substitui os dados da tabela alimentos no MySQL
    pelos dados já traduzidos e limpos do DataFrame.
    """
    usuario  = os.getenv("DB_USER")
    senha    = os.getenv("DB_PASSWORD")
    host     = os.getenv("DB_HOST")
    porta    = os.getenv("DB_PORT")
    banco    = os.getenv("DB_NAME")

    engine = create_engine(f"mysql+mysqlconnector://{usuario}:{senha}@{host}:{porta}/{banco}")

    # substitui a tabela inteira pelos dados limpos e traduzidos
    # if_exists="replace" recria a tabela com os novos dados
    df.to_sql(
        name="alimentos",
        con=engine,
        if_exists="replace",
        index=False
    )

    print(f"Banco atualizado com {len(df)} registros traduzidos.")