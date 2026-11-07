import sys
from importlib import import_module
from pathlib import Path

# Rutas según la estructura del proyecto:
# <raiz>/src/notebook/exportaciones/exportar_empresas.py
CARPETA_ACTUAL = Path(__file__).resolve().parent
CARPETA_SIMULACIONES = CARPETA_ACTUAL.parent / "simulaciones"
RAIZ_PROYECTO = CARPETA_ACTUAL.parents[2]
CARPETA_SALIDA = RAIZ_PROYECTO / "data" / "crudo"

# Permite importar simular_empresas.py desde la carpeta simulaciones
if str(CARPETA_SIMULACIONES) not in sys.path:
    sys.path.insert(0, str(CARPETA_SIMULACIONES))

# Reutiliza la función de simulación (no se copia el código de generación)
generar_empresas = import_module("simular_empresas").generar_empresas


def exportar(df=None):
    """Guarda la tabla sucia en CSV, XLSX y JSON dentro de data/crudo."""
    if df is None:
        df = generar_empresas(300)

    CARPETA_SALIDA.mkdir(parents=True, exist_ok=True)

    ruta_csv = CARPETA_SALIDA / "empresas_sucio.csv"
    ruta_xlsx = CARPETA_SALIDA / "empresas_sucio.xlsx"
    ruta_json = CARPETA_SALIDA / "empresas_sucio.json"

    df.to_csv(ruta_csv, index=False, encoding="utf-8")
    df.to_excel(ruta_xlsx, index=False, sheet_name="empresas")
    df.to_json(ruta_json, orient="records", force_ascii=False, indent=2)

    for ruta in (ruta_csv, ruta_xlsx, ruta_json):
        print(f"{ruta} -> {df.shape}")


if __name__ == "__main__":
    exportar()