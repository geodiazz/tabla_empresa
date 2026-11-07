"""Consultas de la tabla empresas (HU Q01 de Kaizen)."""
from pathlib import Path

import pandas as pd

# Rutas según la estructura del proyecto:
# <raiz>/src/notebook/consultas/consultas_empresas.py
RAIZ_PROYECTO = Path(__file__).resolve().parents[3]
CARPETA_LIMPIO = RAIZ_PROYECTO / "data" / "limpio"
RUTA_ENTRADA = CARPETA_LIMPIO / "empresas_limpio.csv"

# Sector que se filtra en la consulta 2 (debe existir en los datos)
SECTOR_CONSULTA = "Industrial"


def cargar_datos(ruta=RUTA_ENTRADA):
    """Lee el CSV limpio y se asegura de que 'activa' sea booleana real
    (si llega como texto 'True'/'False' la convierte)."""
    ruta = Path(ruta)
    if not ruta.exists():
        raise FileNotFoundError(
            f"No se encontró {ruta}. Ejecuta primero la limpieza."
        )
    df = pd.read_csv(ruta)
    if df["activa"].dtype != bool:
        df["activa"] = (
            df["activa"].astype(str).str.strip().str.upper()
            .map({"TRUE": True, "FALSE": False})
        )
    return df


def guardar(resultado, numero, con_indice):
    """Guarda el resultado en data/limpio/empresas_consulta_N.csv
    y avisa por consola dónde quedó."""
    CARPETA_LIMPIO.mkdir(parents=True, exist_ok=True)
    ruta = CARPETA_LIMPIO / f"empresas_consulta_{numero}.csv"
    resultado.to_csv(ruta, index=con_indice, encoding="utf-8")
    print(f"(guardado en {ruta})")


def consulta_1(df):
    """Consulta 1: ¿Cuáles son las empresas activas?"""
    print("\n=== Consulta 1: ¿Cuáles son las empresas activas? ===")
    activas = df[df["activa"] == True]  # noqa: E712
    print(activas.to_string(index=False) if len(activas) else "Sin resultados.")
    guardar(activas, 1, con_indice=False)
    return activas


def consulta_2(df):
    """Consulta 2: ¿Qué empresas son de un sector, ordenadas por nombre?"""
    print(f"\n=== Consulta 2: ¿Qué empresas son del sector {SECTOR_CONSULTA}, "
          "ordenadas por nombre? ===")
    del_sector = df[df["sector"] == SECTOR_CONSULTA].sort_values("nombre")
    print(del_sector.to_string(index=False) if len(del_sector) else "Sin resultados.")
    guardar(del_sector, 2, con_indice=False)
    return del_sector


def consulta_3(df):
    """Consulta 3: ¿Cuántas empresas hay por sector? (value_counts)"""
    print("\n=== Consulta 3: ¿Cuántas empresas hay por sector? (value_counts) ===")
    conteo = df["sector"].value_counts()
    print(conteo.to_string())
    guardar(conteo, 3, con_indice=True)
    return conteo


def consulta_4(df):
    """Consulta 4 (GROUPBY): ¿Cuántas empresas hay por sector, de mayor a menor?"""
    print("\n=== Consulta 4 (groupby): ¿Cuántas empresas hay por sector, "
          "de mayor a menor? ===")
    por_sector = df.groupby("sector")["id"].count().sort_values(ascending=False)
    print(por_sector.to_string())
    guardar(por_sector, 4, con_indice=True)
    return por_sector


def consulta_5(df):
    """Consulta 5 (GROUPBY doble): ¿Cuántas empresas activas e inactivas hay por sector?"""
    print("\n=== Consulta 5 (groupby doble): ¿Cuántas empresas activas e "
          "inactivas hay por sector? ===")
    tabla = df.groupby(["sector", "activa"])["id"].count().unstack(fill_value=0)
    print(tabla.to_string())
    guardar(tabla, 5, con_indice=True)
    return tabla


def consultar_empresas(ruta_entrada=RUTA_ENTRADA):
    """Lee el CSV limpio y ejecuta las cinco consultas en orden."""
    df = cargar_datos(ruta_entrada)
    print(f"Archivo cargado: {len(df)} empresas, columnas: {list(df.columns)}")

    consulta_1(df)
    consulta_2(df)
    consulta_3(df)
    consulta_4(df)
    consulta_5(df)


if __name__ == "__main__":
    consultar_empresas()