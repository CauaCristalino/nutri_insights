import requests
import json
from pathlib import Path
import os
from dotenv import load_dotenv


import requests
import json
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("FDC_API_KEY")
BASE_URL = "https://api.nal.usda.gov/fdc/v1/foods/search"

def buscar_alimentos(query: str, pagina: int = 1, tamanho: int = 50) -> list:
    """
    Busca alimentos na USDA FoodData Central por termo de pesquisa.
    Retorna uma lista de dicionários com os nutrientes relevantes.
    """

    params = {
        "query": query,
        "pageNumber": pagina,
        "pageSize": tamanho,
        "api_key": API_KEY
    }

    headers = {
        "User-Agent": "NutriInsights/1.0 (caua.pereira345@gmail.com)"
    }

    response = requests.get(BASE_URL, params=params, headers=headers, timeout=15)
    response.raise_for_status()

    alimentos = response.json().get("foods", [])

    return extrair_campos(alimentos)


def extrair_campos(alimentos: list) -> list:
    """
    Mapeia os campos da API USDA para os nomes do nosso banco.
    Ignora alimentos sem nome ou sem dados nutricionais.
    """

    # mapeamento do nome do nutriente na API para o nome no banco
    mapa_nutrientes = {
        "Energy":              "calorias_100g",
        "Protein":             "proteinas_100g",
        "Total lipid (fat)":   "gorduras_100g",
        "Fatty acids, total saturated": "gordura_sat_100g",
        "Carbohydrate, by difference":  "carboidratos_100g",
        "Sugars, total including NLEA": "acucar_100g",
        "Sodium, Na":          "sodio_100g",
        "Fiber, total dietary": "fibras_100g",
    }

    resultado = []

    for alimento in alimentos:
        nutrientes_raw = alimento.get("foodNutrients", [])

        # transforma a lista de nutrientes em dicionário {nome: valor}
        nutrientes = {
            n.get("nutrientName"): n.get("value")
            for n in nutrientes_raw
        }

        registro = {
            "nome":      alimento.get("description", "").strip(),
            "categoria": alimento.get("foodCategory", ""),
            "pais":      "United States",
        }

        # aplica o mapeamento
        for nome_api, nome_banco in mapa_nutrientes.items():
            registro[nome_banco] = nutrientes.get(nome_api)

        # ignora alimentos sem nome ou sem nenhum nutriente
        if registro["nome"] and any(v is not None for v in list(registro.values())[3:]):
            resultado.append(registro)

    return resultado


def salvar_raw(dados: list, nome_arquivo: str) -> None:
    """
    Salva os dados brutos em JSON na pasta data/raw.
    """
    caminho = Path("../data/raw") / nome_arquivo
    caminho.parent.mkdir(parents=True, exist_ok=True)

    with open(caminho, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)

    print(f"{len(dados)} alimentos salvos em {caminho}")