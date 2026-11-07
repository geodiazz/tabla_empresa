import sys
from pathlib import Path

# Hace visibles las carpetas de módulos, sin importar desde dónde se ejecute
BASE = Path(__file__).resolve().parent
for carpeta in ("simulaciones", "exportaciones", "limpiezas", "consultas", "graficas"):
    ruta = str(BASE / carpeta)
    if ruta not in sys.path:
        sys.path.insert(0, ruta)

from simular_empresas import generar_empresas
from exportar_empresas import exportar
from limpiar_empresas import limpiar_empresas
from consultas_empresas import consultar_empresas
from reporte_empresas import graficar_empresas


def main():
    print("=== 1. Simulación (HU F01) ===")
    df = generar_empresas(300)
    print(df.shape)
    print(df.head())
    print(df.isna().sum())

    print("\n=== 2. Exportación (HU X01) ===")
    exportar(df)

    print("\n=== 3. Limpieza (HU L01) ===")
    limpiar_empresas()

    print("\n=== 4. Consultas (HU Q01) ===")
    consultar_empresas()

    print("\n=== 5. Gráficas (HU G01) ===")
    graficar_empresas()


if __name__ == "__main__":
    main()