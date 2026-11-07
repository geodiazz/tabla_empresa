"""Limpieza de la tabla empresas (HU L01 de Kaizen)."""
from pathlib import Path

import pandas as pd

# Rutas según la estructura del proyecto:
# <raiz>/src/notebook/limpiezas/limpiar_empresas.py
RAIZ_PROYECTO = Path(__file__).resolve().parents[3]
RUTA_ENTRADA = RAIZ_PROYECTO / "data" / "crudo" / "empresas_sucio.csv"
RUTA_SALIDA = RAIZ_PROYECTO / "data" / "limpio" / "empresas_limpio.csv"

# Columnas que no pueden quedar con nulos después de limpiar
COLUMNAS_OBLIGATORIAS = ["nombre", "nit", "sector", "activa"]


def diagnostico(df, titulo):
    """Imprime el diagnóstico: shape, info, nulos por columna y duplicados."""
    print(f"\n===== {titulo} =====")
    print("df.shape:", df.shape)
    print("\ndf.info():")
    df.info()
    print("\ndf.isna().sum():")
    print(df.isna().sum())
    print("\ndf.duplicated().sum():", df.duplicated().sum())


def limpiar(df):
    """Aplica las correcciones de la HU L01 y devuelve el DataFrame limpio."""
    # 1. Quitar duplicados exactos
    df = df.drop_duplicates()

    # 2. Quitar espacios sobrantes en el nombre
    df["nombre"] = df["nombre"].str.strip()

    # 3. Unificar el sector ('LOGISTICA' y ' logistica ' quedan iguales)
    df["sector"] = df["sector"].str.strip().str.title()

    # 4. NIT en un solo formato: sin puntos ni guiones
    df["nit"] = df["nit"].str.replace(r"[.\-]", "", regex=True)

    # 5. Teléfono solo con dígitos
    df["telefono"] = df["telefono"].str.replace(r"\D", "", regex=True)

    # 6. 'activa' llega como TEXTO desde el CSV: convertir a booleano real
    df["activa"] = (
        df["activa"].astype(str).str.strip().str.upper()
        .map({"TRUE": True, "SI": True, "1": True,
              "FALSE": False, "NO": False, "0": False})
    )

    # 7. Contactos vacíos -> "Sin contacto"
    df["contacto"] = df["contacto"].fillna("Sin contacto")

    # 8. Marcar correos inválidos en una columna nueva
    df["correo_valido"] = df["correo"].str.contains("@", na=False)

    return df


def garantizar_calidad(df):
    """Deja el resultado sin nulos en las columnas obligatorias y sin
    duplicados exactos (la limpieza puede crear duplicados nuevos al
    normalizar los textos)."""
    for col in COLUMNAS_OBLIGATORIAS:
        if df[col].dtype == object:
            df[col] = df[col].replace("", pd.NA)
    df = df.dropna(subset=COLUMNAS_OBLIGATORIAS)
    return df.drop_duplicates()


def limpiar_empresas(ruta_entrada=RUTA_ENTRADA, ruta_salida=RUTA_SALIDA):
    """Lee el CSV sucio, diagnostica, limpia, vuelve a diagnosticar y guarda."""
    ruta_entrada = Path(ruta_entrada)
    if not ruta_entrada.exists():
        raise FileNotFoundError(
            f"No se encontró {ruta_entrada}. Ejecuta primero la exportación."
        )

    # dtype=str conserva ceros a la izquierda en nit y telefono
    df = pd.read_csv(ruta_entrada, dtype=str)
    filas_antes = len(df)

    diagnostico(df, "DIAGNOSTICO ANTES DE LIMPIAR")

    df = limpiar(df)
    df = garantizar_calidad(df)

    diagnostico(df, "DIAGNOSTICO DESPUES DE LIMPIAR")

    print(f"\nFilas eliminadas: {filas_antes - len(df)} "
          f"({filas_antes} -> {len(df)})")
    print("Nulos en columnas obligatorias:",
          int(df[COLUMNAS_OBLIGATORIAS].isna().sum().sum()))
    print("Duplicados exactos:", int(df.duplicated().sum()))

    ruta_salida = Path(ruta_salida)
    ruta_salida.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(ruta_salida, index=False, encoding="utf-8")
    print(f"\nArchivo guardado en: {ruta_salida}")
    return df


if __name__ == "__main__":
    limpiar_empresas()