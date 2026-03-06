# ================================================================
# Archivo: validators/validacion_estados.py
# Descripción:
#   Valida los estados de las cuotas en el archivo de pagos.
#   Hoja de detalle SIEMPRE generada.
#   Si hay estados = 2 → Con observaciones.
#
# Autor: José López
# Institución: TRANSFORMACION DIGITAL
# Versión: v5.6 - Detalle siempre + observación por estado 2
# Fecha: 18/11/2025
# ================================================================

import pandas as pd

def validar_estados(archivo):
    try:
        df = pd.read_csv(archivo, sep=';', header=None, dtype=str)

        # Validar nº columnas (si falla, marcar error pero entregar detalle)
        if df.shape[1] != 10:
            return {
                "nombre_validacion": "Validación de estados de cuota",
                "resultado": "Error",
                "observaciones": f"Archivo inválido: se esperaban 10 columnas y tiene {df.shape[1]}.",
                "detalle": df.head()
            }

        # Columna del estado (índice 9)
        col_estado = 9

        total = len(df)
        conteo = df[col_estado].value_counts(dropna=False).to_dict()

        est1 = conteo.get("1", 0)
        est2 = conteo.get("2", 0)
        otros = total - est1 - est2

        # -------------------------------------------
        # 🟦 CREA DETALLE SIEMPRE
        # -------------------------------------------
        detalle = pd.DataFrame([
            ["Total registros", total],
            ["Estado 1", est1],
            ["Estado 2", est2],
            ["Otros estados", otros]
        ], columns=["Descripción", "Cantidad"])

        # -------------------------------------------
        # 🔥 DEFINIR RESULTADO SEGÚN LÓGICA PEDIDA
        # -------------------------------------------

        if otros > 0:
            resultado = "Con observaciones"
            obs = f"{otros} registros con estados no válidos."
        elif est2 > 0:
            resultado = "Con observaciones"
            obs = f"{est2} registros con estado 2."
        else:
            resultado = "OK"
            obs = "Solo existen estados 1."

        resumen = (
            f"Total: {total} | Estado 1: {est1} | "
            f"Estado 2: {est2} | Otros: {otros}"
        )

        return {
            "nombre_validacion": "Validación de estados de cuota",
            "resultado": resultado,
            "observaciones": resumen + " → " + obs,
            "detalle": detalle
        }

    except Exception as e:
        return {
            "nombre_validacion": "Validación de estados de cuota",
            "resultado": "Error",
            "observaciones": f"Error al procesar: {e}",
            "detalle": None
        }
