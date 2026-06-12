DROP TABLE alimentos;

CREATE TABLE alimentos (
    id               INT AUTO_INCREMENT PRIMARY KEY,
    nome             VARCHAR(255) UNIQUE,
    categoria        VARCHAR(255),
    pais             VARCHAR(100),
    calorias_100g    FLOAT,
    proteinas_100g   FLOAT,
    gorduras_100g    FLOAT,
    gordura_sat_100g FLOAT,
    carboidratos_100g FLOAT,
    acucar_100g      FLOAT,
    sodio_100g       FLOAT,
    fibras_100g      FLOAT,
    inserido_em      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);