# ================================================================
# Archivo: validators/validacion_montos_cuotas_clasificaciones.py
# Descripción:
#   Valida coherencia entre montos, cuotas y formato de fecha
#   en el archivo de Rebaja Clasificaciones.
#
#   • L, M y P deben ser idénticos
#   • N y O deben ser idénticos
#   • Detecta fechas mal estructuradas
#   • NO modifica el archivo original
#   • Exporta errores a Excel
#   • Retorna dict compatible con AutoFile
#
# Autor: José López
# Institución: TRANSFORMACION DIGITAL
# Versión: v3.0 (FIX DEFINITIVO)
# ================================================================

import pandas as pd


def validar_montos_cuotas_clasificaciones(archivo):
    errores = []

    try:
        df = pd.read_csv(
            archivo,
            sep=";",
            header=None,
            dtype=str,
            encoding="latin1"
        ).fillna("")

        for i, fila in df.iterrows():
            linea = i + 1

            # ====================================================
            # FECHA (col 11 → índice 10)
            # ====================================================
            fecha = fila[10].strip()

            if fecha:
                if len(fecha) != 8 or not fecha.isdigit():
                    errores.append({
                        "Línea": linea,
                        "Tipo": "Formato fecha",
                        "Descripción": "Fecha no tiene 8 dígitos numéricos",
                        "Valores": fecha
                    })
                else:
                    dia = int(fecha[:2])
                    mes = int(fecha[2:4])
                    anio = int(fecha[4:])

                    if anio < 1900 or anio > 2100:
                        errores.append({
                            "Línea": linea,
                            "Tipo": "Formato fecha",
                            "Descripción": "Año fuera de rango válido",
                            "Valores": fecha
                        })

                    if dia < 1 or dia > 31 or mes < 1 or mes > 12:
                        errores.append({
                            "Línea": linea,
                            "Tipo": "Fecha inconsistente",
                            "Descripción": "Día o mes fuera de rango",
                            "Valores": fecha
                        })

            # ====================================================
            # MONTOS → L (11), M (12), P (15)
            # ====================================================
            try:
                monto_L = float(fila[11].replace(",", "."))
                monto_M = float(fila[12].replace(",", "."))
                monto_P = float(fila[15].replace(",", "."))
            except ValueError:
                errores.append({
                    "Línea": linea,
                    "Tipo": "Formato montos",
                    "Descripción": "Error de formato decimal en montos",
                    "Valores": f"L={fila[11]} | M={fila[12]} | P={fila[15]}"
                })
                continue

            if not (monto_L == monto_M == monto_P):
                errores.append({
                    "Línea": linea,
                    "Tipo": "Error montos",
                    "Descripción": "L, M y P deben ser idénticos",
                    "Valores": f"L={monto_L} | M={monto_M} | P={monto_P}"
                })

            # ====================================================
            # CUOTAS → N (13), O (14)
            # ====================================================
            try:
                cuotas_N = int(fila[13])
                cuotas_O = int(fila[14])
            except ValueError:
                errores.append({
                    "Línea": linea,
                    "Tipo": "Formato cuotas",
                    "Descripción": "Error de formato en cuotas",
                    "Valores": f"N={fila[13]} | O={fila[14]}"
                })
                continue

            if cuotas_N != cuotas_O:
                errores.append({
                    "Línea": linea,
                    "Tipo": "Error cuotas",
                    "Descripción": "N y O deben ser idénticos",
                    "Valores": f"N={cuotas_N} | O={cuotas_O}"
                })

        # ====================================================
        # RETORNO COMPATIBLE CON AutoFile
        # ====================================================
        if errores:
            _exportar_errores(archivo, errores)

            return {
                "nombre_validacion": "Coherencia de montos y cuotas (Clasificaciones)",
                "resultado": "OBSERVACIONES",
                "detalle": [
                    f"Línea {e['Línea']} - {e['Tipo']}: {e['Descripción']} ({e['Valores']})"
                    for e in errores
                ]
            }

        return {
            "nombre_validacion": "Coherencia de montos y cuotas (Clasificaciones)",
            "resultado": "OK",
            "detalle": None
        }

    except Exception as e:
        return {
            "nombre_validacion": "Coherencia de montos y cuotas (Clasificaciones)",
            "resultado": "ERROR",
            "detalle": [str(e)]
        }


# ================================================================
# EXPORTAR ERRORES
# ================================================================
def _exportar_errores(archivo, errores):
    df = pd.DataFrame(errores)
    salida = archivo.replace(".txt", "_errores_montos_cuotas.xlsx")
    df.to_excel(salida, index=False)
