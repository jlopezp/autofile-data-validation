# ================================================================
# Archivo: validators/validacion_periodos.py
# Descripción:
#   Valida la consistencia de los periodos (Mes/Año) dentro del archivo TXT.
#   - Detecta si hay más de un periodo distinto.
#   - Genera detalle de los registros por periodo.
#   Retorna resultado estructurado para informes detallados.
#
# Autor: José López
# Institución: TRANSFORMACION DIGITAL
# Versión: v5.1 - Retorno estructurado + detalle DataFrame
# Fecha: 10/11/2025
# ================================================================

import pandas as pd


def validar_periodos(archivo):
    """
    Valida los periodos en columnas 6 (mes) y 7 (año).

    Retorna un diccionario estructurado:
    {
        "nombre_validacion": "Validación de periodos",
        "resultado": "OK" / "Con observaciones" / "Error",
        "observaciones": texto resumen,
        "detalle": DataFrame (si hay observaciones)
    }
    """
    try:
        # Leer archivo separado por ";"
        df = pd.read_csv(archivo, sep=";", header=None, dtype=str)

        if df.empty:
            return {
                "nombre_validacion": "Validación de periodos",
                "resultado": "Error",
                "observaciones": "El archivo está vacío.",
                "detalle": None
            }

        # Verificar cantidad mínima de columnas
        if df.shape[1] <= 7:
            return {
                "nombre_validacion": "Validación de periodos",
                "resultado": "Error",
                "observaciones": f"El archivo tiene {df.shape[1]} columnas, se esperaban al menos 8.",
                "detalle": None
            }

        # Crear columna de periodo MM/YYYY
        df["MES"] = df.iloc[:, 6].astype(str).str.zfill(2)
        df["AÑO"] = df.iloc[:, 7].astype(str).str.strip()
        df["PERIODO"] = df["MES"] + "/" + df["AÑO"]

        # Conteo de registros por periodo
        conteo = df["PERIODO"].value_counts().reset_index()
        conteo.columns = ["Periodo", "Cantidad"]

        if len(conteo) == 1:
            periodo = conteo.iloc[0, 0]
            cantidad = conteo.iloc[0, 1]
            return {
                "nombre_validacion": "Validación de periodos",
                "resultado": "OK",
                "observaciones": f"✅ Un solo periodo detectado: {periodo} con {cantidad} registros.",
                "detalle": None
            }
        else:
            # Hay más de un periodo (observación)
            return {
                "nombre_validacion": "Validación de periodos",
                "resultado": "Con observaciones",
                "observaciones": (
                    f"❌ Se encontraron {len(conteo)} periodos distintos en el archivo."
                ),
                "detalle": conteo
            }

    except Exception as e:
        return {
            "nombre_validacion": "Validación de periodos",
            "resultado": "Error",
            "observaciones": f"Error al validar periodos: {e}",
            "detalle": None
        }
