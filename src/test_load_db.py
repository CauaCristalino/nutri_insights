from ingest import buscar_alimentos
from load_db import inserir_alimentos

dados = buscar_alimentos("vegetable", pagina=1, tamanho=50)
print(f"Alimentos coletados: {len(dados)}")

inserir_alimentos(dados)