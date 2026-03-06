# ================================================================
# Archivo: validators/validacion_estructura.py
# Descripción:
#   Valida la estructura de los archivos TXT de Rebaja / Pagos.
#   - Lee la estructura esperada desde un archivo JSON.
#   - Revisa largo, tipo de dato, formato de fecha, decimales, etc.
#   - Detecta errores de formato y RUT inválidos.
#   - Devuelve un DataFrame con el detalle de los errores detectados.
#
# Autor: José López
# Institución: TRANSFORMACION DIGITAL
# Versión: v5.2 - Retorno detallado de errores (DataFrame)
# Fecha: 07/11/2025
# ================================================================

import json
import os
import pandas as pd

# ================================================================
# FUNCIONES AUXILIARES DE RUT
# ================================================================
def calcular_dv(rut):
    """
    Calcula el dígito verificador (DV) para un RUT chileno.
    Ejemplo: 12345678 → 5
    """
    try:
        rut = int(rut)
    except ValueError:
        return None

    suma = 0
    multiplo = 2
    for digito in reversed(str(rut)):
        suma += int(digito) * multiplo
        multiplo = 2 if multiplo == 7 else multiplo + 1

    resto = 11 - (suma % 11)
    if resto == 11:
        return "0"
    if resto == 10:
        return "K"
    return str(resto)


def validar_rut(rut, dv):
    """
    Valida que el RUT y su dígito verificador correspondan correctamente.
    Retorna True si es válido, False si no lo es.
    """
    if not rut.isdigit():
        return False
    dv = dv.upper()
    return calcular_dv(rut) == dv


# ================================================================
# FUNCIÓN PRINCIPAL: VALIDAR ESTRUCTURA DEL ARCHIVO
# ================================================================
def validar_estructura(archivo, estructura_path):
    """
    Valida la estructura del archivo TXT según las reglas definidas
    en un archivo JSON de estructura (formato, tipo de datos, largo, etc.).

    Parámetros:
    -----------
    archivo : str
        Ruta del archivo TXT a validar.
    estructura_path : str
        Ruta del archivo JSON con las reglas de validación.

    Retorna:
    --------
    pd.DataFrame con las columnas:
        - Línea
        - Campo
        - Descripción del error

    Si no hay errores, devuelve None.
    """

    registros_error = []

    # ------------------------------------------------------------
    # 1. Verificar existencia del archivo de estructura JSON
    # ------------------------------------------------------------
    if not os.path.exists(estructura_path):
        return pd.DataFrame([{"Error": f"No se encontró el archivo de reglas: {estructura_path}"}])

    with open(estructura_path, "r", encoding="utf-8") as f:
        estructura = json.load(f)

    # ------------------------------------------------------------
    # 2. Leer el archivo TXT separado por ";"
    # ------------------------------------------------------------
    with open(archivo, "r", encoding="utf-8") as f:
        lineas = [line.strip() for line in f if line.strip()]

    if not lineas:
        return pd.DataFrame([{"Error": "El archivo está vacío."}])

    num_columnas_esperadas = len(estructura)

    # ------------------------------------------------------------
    # 3. Detectar posiciones de RUT y DV en la estructura
    # ------------------------------------------------------------
    nombres_campos = [campo["Campo"].lower() for campo in estructura]
    pos_rut = nombres_campos.index("rut") if "rut" in nombres_campos else None
    pos_dv = None
    if "dv" in nombres_campos:
        pos_dv = nombres_campos.index("dv")
    elif "dígito verificador" in nombres_campos:
        pos_dv = nombres_campos.index("dígito verificador")

    # ------------------------------------------------------------
    # 4. Validar cada línea del archivo TXT
    # ------------------------------------------------------------
    for idx, linea in enumerate(lineas, start=1):
        columnas = linea.split(";")

        # --- Validación de cantidad de columnas ---
        if len(columnas) != num_columnas_esperadas:
            registros_error.append({
                "Línea": idx,
                "Campo": "(estructura)",
                "Descripción": f"Se esperaban {num_columnas_esperadas} columnas, pero hay {len(columnas)}"
            })
            continue

        # --- Validar cada campo según el JSON ---
        for j, campo in enumerate(estructura):
            valor = columnas[j].strip()
            nombre = campo["Campo"]
            tipo = campo["Tipo de dato"].lower()
            largo = int(campo.get("Largo", 0) or 0)
            decimales = int(campo.get("Decimales", 0) or 0)

            # --- Validación de largo máximo ---
            if largo and len(valor) > largo:
                registros_error.append({
                    "Línea": idx,
                    "Campo": nombre,
                    "Descripción": f"Largo excedido ({len(valor)}/{largo})"
                })

            # --- Validación de tipo de dato ---
            if tipo == "numeric" and not valor.isdigit():
                registros_error.append({"Línea": idx, "Campo": nombre, "Descripción": f"'{valor}' no es numérico"})

            elif tipo == "char" and len(valor) != 1:
                registros_error.append({"Línea": idx, "Campo": nombre, "Descripción": "Debe tener un solo carácter"})

            elif tipo == "alfanumerico" and not valor.replace("-", "").isalnum():
                registros_error.append({"Línea": idx, "Campo": nombre, "Descripción": f"'{valor}' no es alfanumérico"})

            elif tipo == "decimal":
                try:
                    partes = valor.split(",")
                    if len(partes) == 2:
                        decs = len(partes[1])
                        if decs > decimales:
                            registros_error.append({
                                "Línea": idx,
                                "Campo": nombre,
                                "Descripción": f"Demasiados decimales ({decs}/{decimales})"
                            })
                except Exception:
                    registros_error.append({
                        "Línea": idx,
                        "Campo": nombre,
                        "Descripción": f"'{valor}' no es decimal válido"
                    })

            elif tipo.startswith("datetime"):
                if not valor.isdigit() or len(valor) != 8:
                    registros_error.append({
                        "Línea": idx,
                        "Campo": nombre,
                        "Descripción": f"'{valor}' no es fecha válida (ddmmaaaa)"
                    })

        # --- Validación especial de RUT/DV ---
        if pos_rut is not None and pos_dv is not None:
            rut_val = columnas[pos_rut].strip()
            dv_val = columnas[pos_dv].strip()
            if not validar_rut(rut_val, dv_val):
                registros_error.append({
                    "Línea": idx,
                    "Campo": "RUT",
                    "Descripción": f"RUT inválido {rut_val}-{dv_val}"
                })

    # ------------------------------------------------------------
    # 5. Retornar resultado final
    # ------------------------------------------------------------
    if registros_error:
        # Devuelve DataFrame con el detalle de errores encontrados
        return pd.DataFrame(registros_error)
    else:
        # Retorna None si no se detectaron errores
        return None
