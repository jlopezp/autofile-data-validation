import os
import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox

# --- Función para procesar y separar bloques ---
def procesar_archivo(ruta_archivo):
    # Crear carpeta de salida
    carpeta_salida = "salida_bloques"
    os.makedirs(carpeta_salida, exist_ok=True)

    # Definir columnas esperadas
    COLUMNAS = [
        "EntidadFinanciera", "RUT", "DV", "Moneda", "Operacion",
        "Correlativo", "Mes", "Ano", "Monto"
    ]

    # Leer archivo
    df = pd.read_csv(ruta_archivo, sep=";", header=None, names=COLUMNAS, dtype=str)

    # Convertir tipos
    df["Mes"] = df["Mes"].astype(int)
    df["Ano"] = df["Ano"].astype(int)
    df["Correlativo"] = df["Correlativo"].astype(int)

    # Ordenar
    df = df.sort_values(by=["EntidadFinanciera", "RUT", "Operacion", "Ano", "Mes", "Correlativo"])

    # Función para dividir en bloques de hasta 6 meses
    def separar_bloques(grupo):
        bloques = []
        bloque_actual = [grupo.iloc[0]]

        for i in range(1, len(grupo)):
            fila_ant = grupo.iloc[i-1]
            fila_act = grupo.iloc[i]

            mes_consecutivo = (fila_act["Mes"] == fila_ant["Mes"] + 1) and (fila_act["Ano"] == fila_ant["Ano"])
            corr_consecutivo = (fila_act["Correlativo"] == fila_ant["Correlativo"] + 1)

            if mes_consecutivo and corr_consecutivo and len(bloque_actual) < 6:
                bloque_actual.append(fila_act)
            else:
                bloques.append(pd.DataFrame(bloque_actual))
                bloque_actual = [fila_act]

        if bloque_actual:
            bloques.append(pd.DataFrame(bloque_actual))

        return bloques

    # Procesar por grupo
    contador = 0
    for (entidad, rut, operacion), grupo in df.groupby(["EntidadFinanciera", "RUT", "Operacion"]):
        bloques = separar_bloques(grupo.reset_index(drop=True))

        for idx, bloque in enumerate(bloques, start=1):
            nombre_archivo = f"{carpeta_salida}/{entidad}_{rut}_{operacion}_bloque{idx}.txt"
            bloque.to_csv(nombre_archivo, sep=";", header=False, index=False)
            contador += 1

    return contador, carpeta_salida

# --- Interfaz con Tkinter ---
def seleccionar_y_procesar():
    archivo = filedialog.askopenfilename(
        title="Seleccione archivo TXT",
        filetypes=[("Archivos TXT", "*.txt"), ("Todos los archivos", "*.*")]
    )
    if archivo:
        try:
            cantidad, carpeta = procesar_archivo(archivo)
            messagebox.showinfo("Proceso completado", f"✅ Se generaron {cantidad} archivos en la carpeta:\n{carpeta}")
        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error: {e}")

# Ventana principal
root = tk.Tk()
root.title("Separador de Bloques - Archivos TXT")
root.geometry("400x200")

tk.Label(root, text="Separar archivo TXT en bloques de hasta 6 meses", wraplength=350, pady=20).pack()
tk.Button(root, text="Seleccionar archivo y procesar", command=seleccionar_y_procesar, width=30, height=2).pack(pady=20)

root.mainloop()
