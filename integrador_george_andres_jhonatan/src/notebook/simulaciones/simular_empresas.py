import random
import uuid

import pandas as pd
from faker import Faker

# Constantes
SECTORES = ["agricola", "minero", "alimenticio", "industrial"]

# Semillas fijas para que el archivo sea reproducible
random.seed(42)
Faker.seed(42)

fake = Faker("es_CO")


def obtener_muestra(df, porcentaje, semilla):
    """Devuelve los índices de una muestra reproducible.

    Cada columna usa una semilla distinta para que no se ensucien siempre las mismas filas.
    """
    return df.sample(frac=porcentaje, random_state=semilla).index


def crear_base(n):
    """Crea n filas limpias con las 8 columnas de la HU."""
    filas = []
    for _ in range(n):
        filas.append({
            "id": str(uuid.uuid4()),
            "nombre": fake.company(),
            "nit": fake.numerify("#########-#"),
            "sector": random.choice(SECTORES),
            "contacto": fake.name(),
            "correo": fake.company_email(),
            "telefono": fake.numerify("3#########"),
            "activa": random.choice([True, False]),
        })
    return pd.DataFrame(filas)


def duplicar_nits_entre_empresas(df, porcentaje=0.03):
    """Repite el NIT de otras empresas en el 3% de las filas."""
    df = df.copy()
    destino = obtener_muestra(df, porcentaje, 1)
    origen = df.drop(index=destino).sample(n=len(destino), random_state=2).index
    df.loc[destino, "nit"] = df.loc[origen, "nit"].values
    return df


def sector_sucio(texto):
    """Devuelve una variante del mismo sector: 'Logistica', 'LOGISTICA', ' logistica '."""
    return random.choice([texto.title(), texto.upper(), f" {texto} "])


def telefono_sucio(num):
    """Mezcla tres formatos: '3001234567', '300 123 4567', '+57 300-123-4567'."""
    return random.choice([
        num,
        f"{num[:3]} {num[3:6]} {num[6:]}",
        f"+57 {num[:3]}-{num[3:6]}-{num[6:]}",
    ])


def activa_como_texto(valor):
    """Convierte el booleano a texto sin cambiar su significado."""
    if valor:
        return random.choice(["SI", "1"])
    return random.choice(["No", "0"])


def ensuciar(df):
    """Aplica los errores de calidad que pide la HU."""
    df = df.copy()

    # NIT repetidos entre empresas distintas (3%)
    df = duplicar_nits_entre_empresas(df, 0.03)

    # nombre: 10% con espacios sobrantes y 15% en MAYUSCULAS
    idx = obtener_muestra(df, 0.10, 3)
    df.loc[idx, "nombre"] = " " + df.loc[idx, "nombre"] + " "
    idx = obtener_muestra(df, 0.15, 4)
    df.loc[idx, "nombre"] = df.loc[idx, "nombre"].str.upper()

    # nit: mitad con puntos y guion (900.123.456-7), mitad solo digitos (9001234567)
    digitos = df["nit"].str.replace("-", "", regex=False)
    con_formato = obtener_muestra(df, 0.5, 5)
    d = digitos.loc[con_formato]
    df.loc[con_formato, "nit"] = (
        d.str[0:3] + "." + d.str[3:6] + "." + d.str[6:9] + "-" + d.str[9]
    )
    sin_formato = df.index.difference(con_formato)
    df.loc[sin_formato, "nit"] = digitos.loc[sin_formato]

    # sector: variantes del mismo sector
    idx = obtener_muestra(df, 0.20, 6)
    df.loc[idx, "sector"] = df.loc[idx, "sector"].apply(sector_sucio)

    # contacto: 8% nulos
    idx = obtener_muestra(df, 0.08, 7)
    df.loc[idx, "contacto"] = None

    # correo: 6% sin arroba
    idx = obtener_muestra(df, 0.06, 8)
    df.loc[idx, "correo"] = df.loc[idx, "correo"].str.replace("@", "", regex=False)

    # telefono: tres formatos mezclados
    idx = obtener_muestra(df, 0.50, 9)
    df.loc[idx, "telefono"] = df.loc[idx, "telefono"].apply(telefono_sucio)

    # activa: a veces como texto
    df["activa"] = df["activa"].astype(object)
    idx = obtener_muestra(df, 0.15, 10)
    df.loc[idx, "activa"] = df.loc[idx, "activa"].apply(activa_como_texto)

    return df


def agregar_duplicados_exactos(df, cantidad):
    """Agrega copias idénticas de filas ya ensuciadas."""
    copias = df.sample(n=cantidad, random_state=11)
    return pd.concat([df, copias], ignore_index=True)


def generar_empresas(n=300):
    """Genera la tabla empresas sucia con n filas en total y la devuelve."""
    cantidad_duplicados = round(n * 0.05)
    df = crear_base(n - cantidad_duplicados)
    df = ensuciar(df)
    # Los duplicados se agregan al final para que queden idénticos y el total sea n
    df = agregar_duplicados_exactos(df, cantidad_duplicados)
    return df


if __name__ == "__main__":
    df = generar_empresas(300)
    print(df.shape)
    print(df.head())
    print(df.isna().sum())