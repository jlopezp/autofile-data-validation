# ================================================================
# Archivo: AutoFile.py
# Descripción:
#   Interfaz principal del sistema AutoFile (Automatización de Validaciones)
#   - “Validar TODO”: genera informe detallado con hojas por errores.
#   - “Generar Informe Final Pagos”: crea consolidado con montos y totales.
#   - “Generar Informe Final Clasificaciones”: genera informe de clasificaciones.
#
# Autor: José López
# Institución: TRANSFORMACION DIGITAL
# Versión: v6.4 - Limpieza final + códigos ordenados
# Fecha: 17/11/2025
# ================================================================

import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from sqlalchemy import create_engine, text
from datetime import datetime

# === Validaciones generales ===
from validators.validacion_estructura import validar_estructura
from validators.validacion_estados import validar_estados
from validators.validacion_dividendos import validar_dividendos_duplicados
from validators.validacion_montos import validar_montos
from validators.validacion_periodos import validar_periodos
from validators.validacion_rut import validar_rut_archivo

# === Clasificaciones ===
from validators.validacion_clasificaciones import validar_clasificaciones
from validators.validacion_montos_cuotas_clasificaciones import validar_montos_cuotas_clasificaciones
from validators.validacion_clasificados_rechazados import validar_clasificados_rechazados
from validators.validacion_rut_operacion_clasificaciones_archivo import validar_rut_operacion_clasificaciones_archivo
from validators.validacion_informe_final import validar_informe_final

# === Pagos/Rebaja ===
from validators.validacion_informe_final_pagos import generar_informe_final_pagos
from validators.informe_validacion_pagos import generar_informe_validaciones_pagos
from validators.validacion_pagos_leasing import validar_pagos_leasing


# ================================================================
# Conexión a BD
# ================================================================
def get_engine(server_option: str):
    driver = "ODBC Driver 17 for SQL Server"

    if server_option == "(Producción)":
        servidor = "instancia1"
        base_datos = "ORIGEN1"
        cadena = (
            f"mssql+pyodbc://@{servidor}/{base_datos}"
            f"?driver={driver.replace(' ', '+')}&Trusted_Connection=yes"
        )
    else:
        servidor = "DESARROLLO"
        base_datos = "ORIGEN2"
        usuario = "USER"
        contrasena = "123456"
        cadena = (
            f"mssql+pyodbc://{usuario}:{contrasena}@{servidor}/{base_datos}"
            f"?driver={driver.replace(' ', '+')}"
        )

    try:
        engine = create_engine(cadena)
        with engine.connect() as con:
            con.execute(text("SELECT 1"))
        messagebox.showinfo("Conexión", f"✅ Conectado a: {server_option}")
        return engine
    except Exception as e:
        messagebox.showerror("Error de conexión", f"No se pudo conectar: {e}")
        return None


# ================================================================
# Bloque VALIDACIONES
# ================================================================
VALIDACIONES = {
    "Negocio1 - Rebaja": [
        ("Revisión de estructura del archivo (formatos)",
         lambda archivo, engine=None: validar_estructura(archivo, "rules/negocio1_rebaja_estructura.json")),
        ("Revisar y contar los registros con todos los estados",
         lambda archivo, engine=None: validar_estados(archivo)),
        ("Revisar dividendos duplicados en el mismo periodo",
         lambda archivo, engine=None: validar_dividendos_duplicados(archivo)),
        ("Revisar montos donde superan las 20 UF",
         lambda archivo, engine=None: validar_montos(archivo, 8)),
        ("Revisar periodos en el archivo",
         lambda archivo, engine=None: validar_periodos(archivo)),
        ("Revisar existencia de RUT y número de operación",
         lambda archivo, engine: validar_rut_archivo(archivo, engine)),
        ("Detectar subsidios LEASING (PRG = 10)",
         lambda archivo, engine: validar_pagos_leasing(archivo, engine)),
    ],

    "Negocio2 - Clasificaciones": [
        ("Validar archivo de Rebaja Clasificaciones",
         lambda archivo, engine=None: validar_clasificaciones(archivo)),
        ("Revisión de coherencia de montos y cuotas (col 12–16)",
         lambda archivo, engine=None: validar_montos_cuotas_clasificaciones(archivo)),
        ("Revisión de clasificados y rechazados",
         lambda archivo, engine: validar_clasificados_rechazados(archivo, engine)),
        ("Revisión existencia en base de datos",
         lambda archivo, engine: validar_rut_operacion_clasificaciones_archivo(archivo, engine)),
    ]
}


# ================================================================
# UI Principal
# ================================================================
class AutoFileApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("AutoFile - Validaciones Automáticas")
        self.root.geometry("1040x740")
        self.archivo = None
        self.engine = None

        self._build_header()
        self._build_tabs()

    # -------------------------
    # Header
    # -------------------------
    def _build_header(self):
        bar = tk.Frame(self.root)
        bar.pack(fill="x", padx=12, pady=8)

        tk.Label(bar, text="🌐 Servidor:", font=("Segoe UI", 10, "bold")).pack(side=tk.LEFT, padx=(4, 6))

        self.combo_server = ttk.Combobox(
            bar,
            values=["(Producción)", "Servidor Desarrollo"],
            state="readonly",
            width=35
        )
        self.combo_server.current(0)
        self.combo_server.pack(side=tk.LEFT)

        tk.Button(bar, text="🔗 Conectar", command=self.conectar_servidor).pack(side=tk.LEFT, padx=8)

    def conectar_servidor(self):
        opcion = self.combo_server.get()
        self.engine = get_engine(opcion)

    # -------------------------
    # Tabs
    # -------------------------
    def _build_tabs(self):
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)

        # Rebaja/Pagos
        tab_rebaja = ttk.Frame(self.notebook)
        self.notebook.add(tab_rebaja, text="💰 Negocio1 - Rebaja / Pagos")
        self._build_tab_content(tab_rebaja, "Negocio1 - Rebaja", tipo="pagos")

        # Clasificaciones
        tab_clasif = ttk.Frame(self.notebook)
        self.notebook.add(tab_clasif, text="📑 Negocio2 - Clasificaciones")
        self._build_tab_content(tab_clasif, "Negocio2 - Clasificaciones", tipo="clasificaciones")

    # -------------------------
    # Contenido de pestaña
    # -------------------------
    def _build_tab_content(self, container, negocio_key: str, tipo: str):
        frame = tk.Frame(container)
        frame.pack(fill="both", expand=True, padx=15, pady=15)

        tk.Label(frame, text=f"Validaciones – {negocio_key}", font=("Segoe UI", 11, "bold")).pack(pady=6)
        tk.Button(frame, text="📂 Cargar archivo TXT", command=self._cargar_archivo).pack(pady=6)

        box = tk.LabelFrame(frame, text="Lista de validaciones", padx=8, pady=6)
        box.pack(fill="both", expand=False, padx=2, pady=6)

        lista = tk.Listbox(box, height=min(14, len(VALIDACIONES[negocio_key])), activestyle="none")
        for titulo, _ in VALIDACIONES[negocio_key]:
            lista.insert(tk.END, f"• {titulo}")
        lista.config(state="disabled")
        lista.pack(fill="both", expand=True)

        # Botones principales
        buttons = tk.Frame(frame)
        buttons.pack(fill="x", pady=10)

        tk.Button(
            buttons, text="✅ Validar TODO",
            command=lambda: self._validar_todo(negocio_key)
        ).pack(side=tk.LEFT, padx=4)

        if tipo == "pagos":
            tk.Button(
                buttons, text="📊 Generar Informe Final Pagos",
                command=self._generar_informe_final_pagos
            ).pack(side=tk.LEFT, padx=4)
        else:
            tk.Button(
                buttons, text="📊 Generar Informe Final Clasificaciones",
                command=self._generar_informe_final_clasificaciones
            ).pack(side=tk.LEFT, padx=4)

    # ============================================================
    # Funciones auxiliares
    # ============================================================
    def _cargar_archivo(self):
        ruta = filedialog.askopenfilename(title="Selecciona archivo TXT",
                                          filetypes=[("Archivos TXT", "*.txt")])
        if ruta:
            self.archivo = ruta
            messagebox.showinfo("Archivo seleccionado", os.path.basename(ruta))

    # ============================================================
    # 🔍 VALIDAR TODO
    # ============================================================
    def _validar_todo(self, negocio_key: str):
        import pandas as pd

        if not self.archivo:
            messagebox.showwarning("Archivo faltante", "Primero debes cargar un archivo TXT.")
            return

        # Requiere conexión a BD
        if any("RUT" in t for (t, _) in VALIDACIONES[negocio_key]):
            if not self.engine:
                messagebox.showerror("Sin conexión", "Debes conectarte a un servidor antes de continuar.")
                return

        resultados_validaciones = []
        errores = 0

        for titulo, funcion in VALIDACIONES[negocio_key]:
            try:
                resultado = funcion(self.archivo, self.engine)

                if isinstance(resultado, dict):
                    nombre = resultado.get("nombre_validacion", titulo)
                    res = resultado.get("resultado", "OK")
                    detalle = resultado.get("detalle", None)

                    if isinstance(detalle, list):
                        detalle = pd.DataFrame(detalle, columns=["Observacion"])

                    resultados_validaciones.append((nombre, res, detalle))

                    if res != "OK":
                        errores += 1

                else:
                    resultados_validaciones.append((titulo, "OK", None))

            except Exception as e:
                errores += 1
                resultados_validaciones.append((titulo, f"Error: {e}", None))

        # Guardar informe
        generar_informe_validaciones_pagos(resultados_validaciones, self.archivo)

        messagebox.showinfo(
            "Validaciones completadas",
            f"Proceso completado.\nValidaciones con observaciones o errores: {errores}."
        )

        # ============================================================
    # 📊 INFORME FINAL PAGOS – V7.0 (Procesa siempre CARPETA)
    # ============================================================
    def _generar_informe_final_pagos(self):
        try:
            # Siempre elegir carpeta (los archivos vienen del resultado PRODUCCION)
            carpeta = filedialog.askdirectory(
                title="Selecciona la carpeta que contiene los archivos TXT de pagos generados por PRODUCCION"
            )

            if not carpeta:
                messagebox.showwarning("Sin carpeta", "Debes seleccionar una carpeta.")
                return

            # Llama al generador pasándole la carpeta (versión con argumento)
            generar_informe_final_pagos(carpeta)

            messagebox.showinfo(
                "Informe generado",
                "✅ Informe final de pagos generado correctamente con los archivos de PRODUCCION."
            )

        except Exception as e:
            messagebox.showerror(
                "Error",
                f"No se pudo generar el informe final de pagos:\n{e}"
            )


    # ============================================================
    # 📊 INFORME FINAL CLASIFICACIONES
    # ============================================================
    def _generar_informe_final_clasificaciones(self):
        try:
            if not self.archivo:
                messagebox.showwarning("Archivo faltante", "Primero debes cargar un archivo TXT.")
                return

            validar_informe_final(self.archivo)
            messagebox.showinfo("Informe generado", "Informe final de clasificaciones generado correctamente.")

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo generar el informe final de clasificaciones:\n{e}")


# ================================================================
# Main
# ================================================================
if __name__ == "__main__":
    root = tk.Tk()
    app = AutoFileApp(root)
    root.mainloop()
