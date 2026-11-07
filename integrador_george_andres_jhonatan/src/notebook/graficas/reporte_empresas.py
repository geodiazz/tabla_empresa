"""Reporte gráfico de la tabla empresas (HU G01 de Kaizen)."""
import os
from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # sin ventana: el script nunca se queda esperando
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402

# Rutas según la estructura del proyecto:
# <raiz>/src/notebook/graficas/reporte_empresas.py
RAIZ_PROYECTO = Path(__file__).resolve().parents[3]
RUTA_ENTRADA = RAIZ_PROYECTO / "data" / "limpio" / "empresas_limpio.csv"
CARPETA_REPORTES = RAIZ_PROYECTO / "reportes"


def a_booleano(serie):
    """Convierte una columna a booleano real (si llega como texto
    'True'/'False' la mapea; lo que no reconoce queda como nulo)."""
    if serie.dtype == bool:
        return serie
    return (serie.astype(str).str.strip().str.upper()
            .map({"TRUE": True, "FALSE": False}))


def cargar_datos(ruta=RUTA_ENTRADA):
    """Lee el CSV limpio, deja 'activa' como booleana y garantiza que exista
    la columna 'correo_valido' (si falta, la calcula desde 'correo')."""
    ruta = Path(ruta)
    if not ruta.exists():
        raise FileNotFoundError(
            f"No se encontró {ruta}. Ejecuta primero la limpieza."
        )
    df = pd.read_csv(ruta)
    df["activa"] = a_booleano(df["activa"])
    if "correo_valido" in df.columns:
        df["correo_valido"] = a_booleano(df["correo_valido"]).fillna(False)
    else:
        df["correo_valido"] = df["correo"].str.contains("@", na=False)
    return df


def guardar_grafica(numero):
    """Ajusta el espacio con tight_layout, guarda la figura actual en
    reportes/empresas_grafica_N.png con dpi=120, la cierra y devuelve la ruta."""
    os.makedirs(CARPETA_REPORTES, exist_ok=True)
    ruta = CARPETA_REPORTES / f"empresas_grafica_{numero}.png"
    plt.tight_layout()
    plt.savefig(ruta, dpi=120)
    plt.close()
    return ruta


def grafica_1(df):
    """Gráfica 1 (barras): cantidad de empresas por sector."""
    por_sector = df.groupby("sector")["id"].count().sort_values(ascending=False)
    plt.figure(figsize=(8, 5))
    por_sector.plot(kind="bar", color="#4C78A8")
    plt.title("Cantidad de empresas por sector")
    plt.xlabel("Sector")
    plt.ylabel("Número de empresas")
    plt.xticks(rotation=45, ha="right")
    return guardar_grafica(1), por_sector


def grafica_2(df):
    """Gráfica 2 (torta): empresas activas vs inactivas."""
    estado = df["activa"].value_counts()
    # Orden fijo para que cada color siempre corresponda al mismo estado
    estado = estado.reindex([True, False], fill_value=0)
    estado = estado.rename({True: "Activas", False: "Inactivas"})
    plt.figure(figsize=(6, 6))
    estado.plot(kind="pie", autopct="%1.1f%%", colors=["#54A24B", "#E45756"])
    plt.title("Empresas activas vs inactivas")
    plt.xlabel("Proporción de empresas")
    plt.ylabel("Estado")
    return guardar_grafica(2)


def grafica_3(df):
    """Gráfica 3 (barras apiladas): activas e inactivas por sector."""
    tabla = df.groupby(["sector", "activa"])["id"].count().unstack(fill_value=0)
    # Orden fijo de columnas (aunque falte alguna) para colores consistentes
    tabla = tabla.reindex(columns=[False, True], fill_value=0)
    tabla = tabla.rename(columns={True: "Activas", False: "Inactivas"})
    plt.figure(figsize=(8, 5))
    tabla.plot(kind="bar", stacked=True, color=["#E45756", "#54A24B"])
    plt.title("Empresas activas e inactivas por sector")
    plt.xlabel("Sector")
    plt.ylabel("Número de empresas")
    plt.xticks(rotation=45, ha="right")
    plt.legend(title="Estado")
    return guardar_grafica(3)


def imprimir_conclusiones(df, por_sector):
    """Calcula e imprime las conclusiones: sector con más empresas,
    porcentaje de inactivas y correos inválidos."""
    maximo = por_sector.max()
    lideres = por_sector[por_sector == maximo].index.tolist()
    con_estado = df["activa"].dropna()
    inactivas = int((con_estado == False).sum())  # noqa: E712
    pct_inactivas = 100 * inactivas / len(con_estado) if len(con_estado) else 0.0
    invalidos = int((~df["correo_valido"]).sum())

    print("\n===== CONCLUSIONES =====")
    print(f"1. Sector con más empresas: {' y '.join(lideres)} "
          f"({maximo} de {len(df)} empresas registradas).")
    print(f"2. Empresas inactivas: {inactivas} de {len(con_estado)} "
          f"({pct_inactivas:.1f}%). Es la parte de la base que no está operando "
          "en la plataforma: conviene contactarlas para reactivarlas o depurarlas, "
          "porque inflan los indicadores de uso.")
    print(f"3. Correos inválidos: {invalidos} de {len(df)}. Hay que validarlos "
          "en el back porque el front se puede saltar (API, importaciones, "
          "scripts); un correo malo rompe notificaciones y recuperación de "
          "cuenta, y la base debe garantizar su calidad sin depender del cliente.")


def graficar_empresas(ruta_entrada=RUTA_ENTRADA):
    """Lee el CSV limpio, crea las tres gráficas, imprime sus rutas y las
    conclusiones."""
    df = cargar_datos(ruta_entrada)
    print(f"Archivo cargado: {len(df)} empresas.")

    ruta1, por_sector = grafica_1(df)
    ruta2 = grafica_2(df)
    ruta3 = grafica_3(df)

    print("\nGráficas guardadas:")
    for ruta in (ruta1, ruta2, ruta3):
        print(f"  - {ruta}")

    imprimir_conclusiones(df, por_sector)


if __name__ == "__main__":
    graficar_empresas()