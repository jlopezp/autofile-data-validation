# ================================================================
# Archivo: validators/validacion_clasificados_rechazados.py
# Descripción:
#   Procesa el archivo TXT de Clasificaciones DS02/DS116/DS19/DS120.
#   - Lee el archivo maestro desde red 
#     
#   - Compara solo por RUT (sin DV)
#   - Genera informe detallado en TXT_GENERADOS
#
# Versión: v4.5.2 - Comparación solo por RUT
# Autor: José López
# Fecha: 06/11/2025
# ================================================================

import os
import pandas as pd
from datetime import datetime


def validar_clasificados_rechazados(archivo_txt, engine=None):
    print("\n=== Iniciando validación de clasificados y rechazados (v4.5.2) ===")

    # --- Definir estructuras ---
    columnas_17 = [
        "RUT", "DV", "NOMBRE", "AP_PATERNO", "AP_MATERNO",
        "REGION", "COMUNA", "ENTIDAD_FIN", "COD_MONEDA",
        "NUM_OPERACION", "FECHA_CREDITO", "MONTO_CREDITO",
        "SALDO_DEUDOR", "N_CUOTAS_TOTAL", "SALDO_EN_CUOTAS",
        "MONTO_ORIGINAL", "MONTO_DIVIDENDO"
    ]
    columnas_18 = columnas_17 + ["% BENEFICIO"]

    # --- Leer TXT ---
    df = pd.read_csv(archivo_txt, sep=";", header=None, dtype=str, encoding="latin-1", on_bad_lines="skip")
    n_cols = df.shape[1]
    if n_cols == 17:
        df.columns = columnas_17
        df["% BENEFICIO"] = ""
    elif n_cols >= 18:
        df = df.iloc[:, :18]
        df.columns = columnas_18
    else:
        raise Exception(f"Estructura inesperada: {n_cols} columnas detectadas")

    # --- Normalizar RUT ---
    def normalizar_rut(r):
        return str(r).strip().replace(".", "").replace("-", "").zfill(8)

    df["RUT_NORM"] = df["RUT"].apply(normalizar_rut)

    # --- Leer Excel maestro en red ---
    excel_maestro = r"\\share\\Clasificados & Rechazados.xlsx"
    if not os.path.exists(excel_maestro):
        print(f"⚠️ No se encontró el Excel maestro en:\n{excel_maestro}")
        return "No se encontró el archivo maestro en red."

    try:
        with open(excel_maestro, "rb") as f:
            f.read(1)
    except PermissionError:
        print(f"⚠️ El archivo '{excel_maestro}' está abierto. Cierra el Excel y vuelve a ejecutar.")
        return "Archivo maestro bloqueado por otro usuario."

    # --- Leer Excel maestro ---
    df_maestro = pd.read_excel(excel_maestro, dtype=str)
    df_maestro.columns = [c.strip().upper() for c in df_maestro.columns]

    # --- Normalizar RUT maestro ---
    if "RUT" not in df_maestro.columns:
        raise Exception("El Excel maestro no contiene la columna 'RUT'.")
    df_maestro["RUT_NORM"] = df_maestro["RUT"].apply(normalizar_rut)

    # --- Determinar columnas opcionales ---
    col_region = "REGION" if "REGION" in df_maestro.columns else None
    col_programa = "PROGRAMA" if "PROGRAMA" in df_maestro.columns else None
    col_beneficio = "BENEFICIO" if "BENEFICIO" in df_maestro.columns else None
    col_motivo = "MOTIVO_RECHAZO" if "MOTIVO_RECHAZO" in df_maestro.columns else None

    # --- Combinar por RUT_NORM ---
    df_merge = df.merge(df_maestro, on="RUT_NORM", how="left", suffixes=("", "_MAESTRO"))

    # --- Marcar encontrados / no encontrados ---
    df_merge["Estado"] = df_merge.apply(lambda x: "ENCONTRADO" if pd.notna(x.get("REGION_MAESTRO", None)) else "NO ENCONTRADO", axis=1)

    # --- Crear DataFrames separados ---
    cols_salida = ["RUT", "DV"]
    if col_region: cols_salida.append("REGION_MAESTRO")
    if col_programa: cols_salida.append("PROGRAMA")
    cols_salida += ["MONTO_CREDITO", "Estado"]
    if col_beneficio: cols_salida.append("BENEFICIO")
    if col_motivo: cols_salida.append("MOTIVO_RECHAZO")

    df_encontrados = df_merge[df_merge["Estado"] == "ENCONTRADO"][cols_salida].copy()
    df_no_encontrados = df_merge[df_merge["Estado"] == "NO ENCONTRADO"][cols_salida].copy()

    # --- Carpeta de salida ---
    base_path = os.path.dirname(archivo_txt)
    carpeta_salida = os.path.join(base_path, "TXT_GENERADOS")
    os.makedirs(carpeta_salida, exist_ok=True)
    nombre_archivo = os.path.splitext(os.path.basename(archivo_txt))[0]
    salida_informe = os.path.join(carpeta_salida, f"{nombre_archivo}_informe_clasificados.xlsx")

    # --- Guardar informe Excel ---
    with pd.ExcelWriter(salida_informe, engine="xlsxwriter") as writer:
        df_encontrados.to_excel(writer, index=False, sheet_name="Encontrados")
        df_no_encontrados.to_excel(writer, index=False, sheet_name="No Encontrados")

        resumen = pd.DataFrame({
            "Detalle": ["Encontrados", "No Encontrados", "Total"],
            "Cantidad": [len(df_encontrados), len(df_no_encontrados), len(df)]
        })
        resumen.to_excel(writer, index=False, sheet_name="Resumen General")

    print(f"📘 Informe generado correctamente: {salida_informe}")
    print(f"✅ Total encontrados: {len(df_encontrados)} | No encontrados: {len(df_no_encontrados)}")

    return f"Informe de clasificados y rechazados generado: {salida_informe}"
