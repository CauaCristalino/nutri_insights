from clean import carregar_dados, limpar_dados, exportar_csv, atualizar_banco

df = carregar_dados()
df_limpo = limpar_dados(df)
exportar_csv(df_limpo, "alimentos_limpos.csv")
atualizar_banco(df_limpo)