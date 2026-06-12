from ingest import buscar_alimentos, salvar_raw
from load_db import inserir_alimentos

categorias = [
    "fruit",
    "vegetable",
    "protein",
    "dairy",
    "grain",
    "nut",
    "fish",
    "legume",
    "breakfast cereal",
    "snack",
    "beverage",
    "meat",
    "egg",
    "herb",
    "spice",
    "seafood",
    "bread",
    "soup"
]
for categoria in categorias:
    print(f"\nColetanto{categoria}...")
    dados = buscar_alimentos(categoria, pagina=1, tamanho=50)
    salvar_raw(dados, f"{categoria}_raw.json")
    inserir_alimentos(dados)

print(f"\nPopulação do Banco concluída!")