# ================================================================
# Archivo: validators/validacion_dividendos.py
# Descripción:
#   Detecta dividendos duplicados en el mismo periodo.
#   Agrupa por: RUT + Número de Operación + Mes + Año.
#   Devuelve resultados compatibles con el informe de validaciones v5.1
#
# Autor: José López
# Institución: TRANSFORMACION DIGITAL
# Versión: v5.1 - Retorno estructurado con DataFrame
# Fecha: 10/11/2025
# ================================================================

import pandas as pd

def validar_dividendos_duplicados(archivo):
    """
    Revisa que no existan dividendos duplicados en el mismo periodo.
    Agrupa por: RUT + Nº de Operación + Mes + Año.

    Retorna un diccionario:
    {
        "nombre_validacion": "Validación de dividendos duplicados",
        "resultado": "OK" o "Con observaciones",
        "observaciones": str,
        "detalle": DataFrame con los duplicados (si existen)
    }
    """
    try:
        # Leer el archivo separado por ';'
        df = pd.read_csv(archivo, sep=';', header=None, dtype=str)
        if df.empty:
            return {
                "nombre_validacion": "Validación de dividendos duplicados",
                "resultado": "Error",
                "observaciones": "El archivo está vacío.",
                "detalle": None
            }

        # Verificar que tenga al menos las columnas esperadas
        if df.shape[1] < 8:
            return {
                "nombre_validacion": "Validación de dividendos duplicados",
                "resultado": "Error",
                "observaciones": f"Archivo con solo {df.shape[1]} columnas, se esperaban al menos 8.",
                "detalle": None
            }

        # Definir columnas de agrupación
        df["RUT"] = df.iloc[:, 1].str.strip()
        df["NUM_OP"] = df.iloc[:, 4].str.strip()
        df["MES"] = df.iloc[:, 6].str.strip()
        df["ANIO"] = df.iloc[:, 7].str.strip()
        df["CLAVE"] = df["RUT"] + "-" + df["NUM_OP"] + "-" + df["MES"] + "-" + df["ANIO"]

        # Detectar duplicados exactos
        df["Duplicado"] = df.duplicated(subset=["CLAVE"], keep=False)
        df_duplicados = df[df["Duplicado"] == True].copy()

        # Resultado según si hay duplicados o no
        if not df_duplicados.empty:
            resultado = "Con observaciones"
            obs = f"{len(df_duplicados)} registros duplicados detectados."
        else:
            resultado = "OK"
            obs = "No se encontraron dividendos duplicados."

        return {
            "nombre_validacion": "Validación de dividendos duplicados",
            "resultado": resultado,
            "observaciones": obs,
            "detalle": df_duplicados[["RUT", "NUM_OP", "MES", "ANIO"]] if not df_duplicados.empty else None
        }

    except Exception as e:
        return {
            "nombre_validacion": "Validación de dividendos duplicados",
            "resultado": "Error",
            "observaciones": f"Error al procesar: {e}",
            "detalle": None
        }
