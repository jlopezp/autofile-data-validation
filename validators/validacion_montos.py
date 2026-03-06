# ================================================================
# Archivo: validators/validacion_montos.py
# Descripción:
#   Valida que los montos en UF no superen los límites establecidos
#   o sean negativos.
#   - Error si monto > 20 UF
#   - Advertencia si monto > 19 UF
#   - Error si monto < 0
#   Retorna resultado estructurado compatible con informes detallados.
#
# Autor: José López
# Institución: TRANSFORMACION DIGITAL
# Versión: v5.2 - Incluye detección de montos negativos y detalle completo
# Fecha: 11/11/2025
# ================================================================

import requests
import pandas as pd

# ---------------------------------------------------------------
# Obtener valor UF actual
# ---------------------------------------------------------------
def get_uf_actual():
    """Obtiene el valor actual de la UF desde mindicador.cl"""
    try:
        resp = requests.get("https://mindicador.cl/api/uf", timeout=6)
        resp.raise_for_status()
        data = resp.json()
        return float(data.get("serie", [{}])[0].get("valor", 0))
    except Exception as e:
        print(f"[ADVERTENCIA] No se pudo obtener UF: {e}")
        return 39000.0  # Valor de respaldo en CLP


# ---------------------------------------------------------------
# Validación principal
# ---------------------------------------------------------------
def validar_montos(archivo, indice_monto=8):
    """
    Valida montos en UF:
      - Error si monto > 20 UF
      - Advertencia si monto > 19 UF
      - Error si monto < 0 (negativo)
    """
    try:
        # Leer archivo separado por ";"
        df = pd.read_csv(archivo, sep=";", header=None, dtype=str)
        if df.empty:
            return {
                "nombre_validacion": "Validación de montos en UF",
                "resultado": "Error",
                "observaciones": "El archivo está vacío.",
                "detalle": None
            }

        # Verificar columna de monto
        if df.shape[1] <= indice_monto:
            return {
                "nombre_validacion": "Validación de montos en UF",
                "resultado": "Error",
                "observaciones": f"Archivo con solo {df.shape[1]} columnas, se esperaba la {indice_monto+1}.",
                "detalle": None
            }

        uf = get_uf_actual()

        # Limpieza y conversión de montos
        df["MONTO_UF"] = (
            df.iloc[:, indice_monto]
            .astype(str)
            .str.replace(",", ".", regex=False)
            .str.strip()
        )

        df["MONTO_UF_NUM"] = pd.to_numeric(df["MONTO_UF"], errors="coerce")
        df["MONTO_CLP"] = df["MONTO_UF_NUM"] * uf

        # Filtrar casos
        df_negativos = df[df["MONTO_UF_NUM"] < 0]
        df_errores = df[df["MONTO_UF_NUM"] > 20]
        df_advertencias = df[(df["MONTO_UF_NUM"] > 19) & (df["MONTO_UF_NUM"] <= 20)]

        # Concatenar todas las filas observadas
        df_detalle = pd.concat([df_negativos, df_errores, df_advertencias])

        # Resultado general
        if not df_detalle.empty:
            resultado = "Con observaciones"
            obs = (
                f"Se detectaron {len(df_negativos)} montos negativos, "
                f"{len(df_errores)} mayores a 20 UF, "
                f"y {len(df_advertencias)} cercanos al límite (>19 UF)."
            )
        else:
            resultado = "OK"
            obs = "No se encontraron montos fuera de rango (negativos o sobre 19 UF)."

        # Reordenar columnas para claridad
        if not df_detalle.empty:
            cols = list(df.columns)
            # Mover las columnas de cálculo al final
            for col in ["MONTO_UF", "MONTO_UF_NUM", "MONTO_CLP"]:
                if col in cols:
                    cols.remove(col)
                    cols.append(col)
            df_detalle = df_detalle[cols]

        return {
            "nombre_validacion": "Validación de montos en UF",
            "resultado": resultado,
            "observaciones": obs,
            "detalle": df_detalle if not df_detalle.empty else None
        }

    except Exception as e:
        return {
            "nombre_validacion": "Validación de montos en UF",
            "resultado": "Error",
            "observaciones": f"Error al procesar archivo: {e}",
            "detalle": None
        }
