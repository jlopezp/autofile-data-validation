# ================================================================
# Archivo: validators/validacion_rut_operacion_clasificaciones_archivo.py
# Descripción:
#   Recorre el archivo TXT de Clasificaciones y valida RUT + N° de Operación
#   contra las tablas DS02, DS51 y DS12 (incluyendo reprogramaciones).
#   Genera un archivo Excel de salida con:
#     - Columnas separadas RUT y DV (compatibles con validación v4.3.8)
#     - Resultados detallados por decreto
#     - Hoja resumen con conteo de registros ENCONTRADOS / NO ENCONTRADOS
#
#   Este archivo es utilizado por la validación "Clasificados y Rechazados"
#   para identificar los registros ya procesados en PRODUCCION.
#
# Versión: v4.3.8 - Formato compatible con validación_clasificados_rechazados v4.3.8
# Autor: José López
# Fecha: 03/11/2025
# ================================================================

import pandas as pd
from .validacion_rut_operacion_clasificaciones import validar_rut_operacion_clasificaciones
from datetime import datetime

def validar_rut_operacion_clasificaciones_archivo(archivo, engine):
    """
    Recorre el archivo TXT de Clasificaciones y valida RUT + N° Operación
    contra las tablas DS02, DS51 y DS12 (incluyendo reprogramaciones).
    Genera un Excel ordenado por RUT con el estado detallado por cada decreto.
    Ahora exporta las columnas RUT y DV separadas (compatibles con validación v4.3.8).
    """
    registros = []

    try:
        df = pd.read_csv(archivo, sep=';', header=None, dtype=str, encoding='latin1').fillna('')

        for i, fila in df.iterrows():
            linea = i + 1
            rut = fila[0].strip()
            dv = fila[1].strip().upper()
            op = fila[9].strip()

            resultados = validar_rut_operacion_clasificaciones(rut, op, engine)
            encontrados = [f"{k}: ✅" for k, v in resultados.items() if "✅" in v]
            no_encontrados = [f"{k}: ❌" for k, v in resultados.items() if "❌" in v]

            registros.append({
                "Línea": linea,
                "RUT": rut,
                "DV": dv,
                "Operación": op,
                "Encontrado en": ", ".join(encontrados) if encontrados else "No encontrado en ninguna tabla",
                "No encontrado en": ", ".join(no_encontrados),
                "Estado General": "ENCONTRADO" if encontrados else "NO ENCONTRADO"
            })

        # --- Crear DataFrame de salida ---
        df_out = pd.DataFrame(registros)

        # Ordenar por RUT numéricamente
        df_out["RUT"] = df_out["RUT"].astype(str)
        df_out = df_out.sort_values(by="RUT", ascending=True)

        # Agregar columna con fecha de ejecución
        fecha = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        df_out.insert(0, "Fecha Ejecución", fecha)

        # Generar nombre de archivo de salida
        salida = archivo.replace(".txt", "_validacion_bd_clasificaciones.xlsx")

        # Exportar Excel
        with pd.ExcelWriter(salida, engine='openpyxl') as writer:
            df_out.to_excel(writer, index=False, sheet_name="Validación_BD_Clasificaciones")

            # --- Hoja resumen ---
            resumen = df_out.groupby("Estado General")["RUT"].count().reset_index()
            resumen.columns = ["Estado General", "Cantidad"]
            resumen.to_excel(writer, index=False, sheet_name="Resumen")

        total = len(df_out)
        encontrados = len(df_out[df_out["Estado General"] == "ENCONTRADO"])
        no_encontrados = total - encontrados

        print("\n=== VALIDACIÓN BD COMPLETADA ===")
        print(f"Total registros: {total}")
        print(f"   - Encontrados: {encontrados}")
        print(f"   - No encontrados: {no_encontrados}")
        print(f"Archivo generado: {salida}\n")

        return (
            f"Validación completada ✅\n\n"
            f"Total registros: {total}\n"
            f"Encontrados en BD: {encontrados}\n"
            f"No encontrados: {no_encontrados}\n\n"
            f"Archivo generado: {salida}"
        )

    except Exception as e:
        return f"❌ Error en validar_rut_operacion_clasificaciones_archivo: {str(e)}"
