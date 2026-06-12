from clean import carregar_dados, limpar_dados, exportar_csv

df = carregar_dados()
df_limpo = limpar_dados(df)
exportar_csv(df_limpo, "alimentos_limpos.csv")