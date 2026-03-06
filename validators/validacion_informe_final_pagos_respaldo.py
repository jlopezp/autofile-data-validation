# ================================================================
# Archivo: validators/validacion_informe_final_pagos.py
# Descripción:
#   Genera los informes de validaciones y el informe final para Rebaja/Pagos.
#   - Informe de validaciones: resumen + detalle de filas con errores.
#   - Informe final: Excel formateado con nóminas y totales.
#
# Autor: José López
# Institución: TRANSFORMACION DIGITAL
# Versión: v5.2 (ajustada) - Compatible con validaciones detalladas
# Fecha: 10/11/2025
# ================================================================

import os
import pandas as pd
from datetime import datetime
from tkinter import messagebox, filedialog


# ================================================================
# GENERAR INFORME DE VALIDACIONES DETALLADO
# ================================================================
def generar_informe_validaciones_pagos(resultados_validaciones, archivo_txt):
    """
    Crea un archivo Excel con:
      - Hoja 1: Resumen general de validaciones (nombre, resultado, observaciones)
      - Hojas siguientes: Detalle de filas con errores por cada validación con observaciones

    Parámetros:
        resultados_validaciones: lista de tuplas (nombre_validacion, resultado, df_errores)
        archivo_txt: ruta completa del archivo TXT validado
    """
    try:
        carpeta_base = os.path.dirname(archivo_txt)
        carpeta_validaciones = os.path.join(carpeta_base, "Validaciones")
        os.makedirs(carpeta_validaciones, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        nombre_salida = os.path.join(carpeta_validaciones, f"Validaciones_Pagos_{timestamp}.xlsx")

        resumen = []
        escritor = pd.ExcelWriter(nombre_salida, engine="openpyxl")

        # Procesar cada validación
        for nombre, resultado, df_errores in resultados_validaciones:
            # --- Asegurar compatibilidad ---
            if isinstance(df_errores, list) and df_errores:
                # Convertir lista de strings a DataFrame de una columna
                df_errores = pd.DataFrame(df_errores, columns=["Observaciones"])
            elif not isinstance(df_errores, pd.DataFrame):
                df_errores = pd.DataFrame()

            # --- Guardar resultados ---
            if df_errores is not None and not df_errores.empty:
                resumen.append([nombre, "Con observaciones", f"{len(df_errores)} filas afectadas"])
                hoja = nombre[:28].replace("/", "-")
                df_errores.to_excel(escritor, index=False, sheet_name=hoja)
            else:
                resumen.append([nombre, "OK", ""])

        # Hoja resumen
        df_resumen = pd.DataFrame(resumen, columns=["Validación", "Resultado", "Observaciones"])
        df_resumen.to_excel(escritor, index=False, sheet_name="Resumen Validaciones")

        escritor.close()

        messagebox.showinfo(
            "Informe de validaciones generado",
            f"✅ Archivo creado en:\n{nombre_salida}\n\n"
            "Incluye hojas con detalle de errores detectados."
        )

    except Exception as e:
        messagebox.showerror("Error", f"Ocurrió un error al generar el informe de validaciones:\n{e}")


# ================================================================
# GENERAR INFORME FINAL DE PAGOS
# ================================================================
def generar_informe_final_pagos(engine=None):
    """
    Genera un informe consolidado con todos los archivos TXT de pagos (DS02, DS12, DS51, etc.)
    - Respeta la estructura original de los archivos.
    - Obtiene el MES y AÑO desde las columnas 6 y 7 del TXT.
    - Incluye una hoja con detalle y otra con resumen de totales por decreto y periodo.
    """
    import pandas as pd
    import os
    from datetime import datetime
    from tkinter import filedialog, messagebox

    try:
        # === Selección de carpeta ===
        carpeta = filedialog.askdirectory(title="Selecciona la carpeta con archivos TXT de pagos")
        if not carpeta:
            messagebox.showwarning("Carpeta faltante", "No se seleccionó ninguna carpeta.")
            return

        archivos_txt = [f for f in os.listdir(carpeta) if f.lower().endswith(".txt")]
        if not archivos_txt:
            messagebox.showwarning("Sin archivos", "No se encontraron archivos TXT en la carpeta seleccionada.")
            return

        registros = []
        columnas_referencia = None  # se detectará del primer archivo

        # === Leer todos los archivos TXT ===
        for archivo in archivos_txt:
            ruta = os.path.join(carpeta, archivo)
            try:
                df = pd.read_csv(ruta, sep=";", header=None, dtype=str, encoding="latin-1", na_filter=False)
                if df.empty:
                    print(f"[AVISO] El archivo {archivo} está vacío.")
                    continue

                # Definir columnas de referencia (mantiene estructura del primer TXT)
                if columnas_referencia is None:
                    columnas_referencia = [f"COL_{i+1}" for i in range(df.shape[1])]
                
                df.columns = columnas_referencia[:df.shape[1]]

                # Extraer MES y AÑO desde columnas 7 y 8 (índices 6 y 7)
                if df.shape[1] >= 8:
                    df["MES"] = df.iloc[:, 6].astype(str).str.zfill(2)
                    df["AÑO"] = df.iloc[:, 7].astype(str)
                    df["PERIODO"] = df["MES"] + "/" + df["AÑO"]
                else:
                    df["PERIODO"] = "No definido"

                # Agregar nombre del archivo como referencia (ej. DS02, DS51, etc.)
                df["ARCHIVO_ORIGEN"] = os.path.splitext(archivo)[0]

                registros.append(df)

            except Exception as e:
                print(f"[Error al leer {archivo}]: {e}")

        if not registros:
            messagebox.showerror("Error", "No se pudo leer ningún archivo TXT válido.")
            return

        # === Consolidar todos los archivos ===
        df_consolidado = pd.concat(registros, ignore_index=True)

        # === Crear resumen total UF por decreto y periodo ===
        # Si la columna de monto existe (posición 9)
        if df_consolidado.shape[1] >= 9:
            df_consolidado["MONTO_UF"] = (
                df_consolidado.iloc[:, 8]
                .astype(str)
                .str.replace(",", ".", regex=False)
                .str.strip()
            )
            df_consolidado["MONTO_UF_NUM"] = pd.to_numeric(df_consolidado["MONTO_UF"], errors="coerce")

            resumen = (
                df_consolidado.groupby(["ARCHIVO_ORIGEN", "PERIODO"])["MONTO_UF_NUM"]
                .sum()
                .reset_index()
                .rename(columns={"MONTO_UF_NUM": "TOTAL_UF"})
            )
        else:
            resumen = pd.DataFrame(columns=["ARCHIVO_ORIGEN", "PERIODO", "TOTAL_UF"])

        # === Guardar Excel consolidado ===
        fecha = datetime.now().strftime("%Y%m%d_%H%M")
        salida = os.path.join(carpeta, f"Informe_Final_Pagos_{fecha}.xlsx")

        with pd.ExcelWriter(salida, engine="openpyxl") as writer:
            df_consolidado.to_excel(writer, index=False, sheet_name="Detalle_Pagos")
            resumen.to_excel(writer, index=False, sheet_name="Resumen_Totales")

        messagebox.showinfo(
            "Informe Final Generado",
            f"✅ Informe consolidado creado correctamente.\n\nUbicación:\n{salida}\n\n"
            f"Archivos procesados: {len(archivos_txt)}"
        )

    except Exception as e:
        messagebox.showerror("Error", f"Ocurrió un error al generar el informe final:\n{e}")



# ================================================================
# EXPORTAR PDF DESDE EXCEL
# ================================================================
def exportar_pdf_desde_excel():
    """
    Exporta un archivo Excel a PDF usando Microsoft Excel (requiere pywin32).
    """
    try:
        import win32com.client
        ruta_excel = filedialog.askopenfilename(title="Selecciona el archivo Excel a exportar")
        if not ruta_excel:
            return

        excel = win32com.client.Dispatch("Excel.Application")
        wb = excel.Workbooks.Open(ruta_excel)
        pdf_path = ruta_excel.replace(".xlsx", ".pdf")
        wb.ExportAsFixedFormat(0, pdf_path)
        wb.Close(False)
        excel.Quit()

        messagebox.showinfo("Exportación PDF", f"✅ Archivo PDF exportado:\n{pdf_path}")

    except Exception as e:
        messagebox.showerror("Error PDF", f"No se pudo exportar a PDF:\n{e}")
