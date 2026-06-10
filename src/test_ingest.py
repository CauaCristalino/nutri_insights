from ingest import buscar_alimentos, salvar_raw

dados = buscar_alimentos("fruit", pagina=1, tamanho=20)

print(f"Total de alimentos encontrados:{len(dados)}")

print("\nPrimeiro alimento:")
for chave, valor in dados[0].items():
    print(f"  {chave}: {valor}")

salvar_raw(dados, "fruit_raw.json")