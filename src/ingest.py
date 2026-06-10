import requests
import json
from pathlib import Path

def buscar_alimentos(categoria: str, pagina: int = 1, tamanho: int = 100) -> list:
    """ Busca alimentos da Open Food Facts por categoria.
    Retorna uma lista de dicionários com os nutrientes relevantes.
    """

    url = "https://world.openfoodfacts.org/cgi/search.pl"

    params = {
        "search_terms": categoria,
        "search_simple": 1,
        "action": "process",
        "json": 1,
        "page": pagina,
        "page_size": tamanho
    }

    headers = {
        "User-Agent": "Nutri_Insights/1.0 (caua.pereira345@gmail.com)"
    }

    response = requests.get(url, params=params, headers=headers, timeout=15)
    response.raise_for_status()

    produtos = response.json().get("products", [])

    return extrair_campos(produtos)

def extrair_campos(produtos: list) -> list:
    """
    Mapeia os campos da API para os nomes do Banco de Dados
    """
    resultado = []

    for produto in produtos:
        nutriments = produto.get("nutriments", {})

        alimento = {
            "nome_alimento": produto.get("product_name","").strip(),
            "categoria_alimento": produto.get("categories", "").split(","),
            "pais": produto.get("countries", "").split(","),
            "calorias_100g": nutriments.get("energy-kcal_100g"),
            "proteinas_100g":    nutriments.get("proteins_100g"),
            "gorduras_100g":     nutriments.get("fat_100g"),
            "gordura_sat_100g":  nutriments.get("saturated-fat_100g"),
            "carboidratos_100g": nutriments.get("carbohydrates_100g"),
            "acucar_100g":       nutriments.get("sugars_100g"),
            "sodio_100g":        nutriments.get("sodium_100g"),
            "fibras_100g":       nutriments.get("fiber_100g"),
        }
        if alimento["nome_alimento"] and any (v is not None for v in list(alimento.values())[3:0]):
            resultado.append(alimento)

    return resultado

def salvar_raw(dados: list, nome_arquivo: str) -> None:
    """
    Salva os Dados Brutos em JSON na pasta data/raw.
    """
    caminho = Path("data/raw") / nome_arquivo
    with open(caminho, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)
    print(f"{len(dados)}alimentos salvos em{caminho}")