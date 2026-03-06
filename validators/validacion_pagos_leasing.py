# ================================================================
# Archivo: validators/validacion_pagos_leasing.py
# Descripción:
#   Detecta subsidios LEASING en archivos TXT de pagos,
#   según definición PRODUCCION (PRG = 10).
#
#   • Identifica registros LEASING
#   • Permite excluirlos del proceso MUTUOS
#   • Genera informe Excel para notificación
#
# Autor: José López
# Institución: TRANSFORMACION DIGITAL
# Versión: v1.0
# ================================================================

import pandas as pd
from sqlalchemy import text


def validar_pagos_leasing(archivo, engine):
    leasing_detectados = []

    # ==========================
    # Leer archivo TXT de pagos
    # ==========================
    df = pd.read_csv(
        archivo,
        sep=";",
        header=None,
        dtype=str,
        encoding="latin1"
    ).fillna("")

    for i, fila in df.iterrows():
        linea = i + 1

        rut = fila[1].strip()      # AJUSTAR si el RUT está en otra columna
        entidad = fila[0].strip()  # AJUSTAR si cambia el layout

        if not rut:
            continue

        # ==========================
        # Consulta BD – Leasing
        # ==========================
        sql = text("""
            SELECT TIT_CRE_DS02_RUT, ENT_FIA_ID, TIT_CRE_DS02_PRG
            FROM PRODUCCION_MIGRA_TITULAR_CREDITO_DS02
            WHERE tit_cre_ds02_est_vig = 1
              AND TIT_CRE_DS02_PRG = 10
              AND TIT_CRE_DS02_RUT = :rut
        """)

        with engine.connect() as con:
            resultado = con.execute(sql, {"rut": rut}).fetchone()

        if resultado:
            leasing_detectados.append({
                "Línea TXT": linea,
                "RUT": rut,
                "Entidad Financiera": entidad,
                "Tipo Subsidio": "LEASING",
                "Programa": resultado.TIT_CRE_DS02_PRG
            })

    # ==========================
    # Resultado validación
    # ==========================
    if leasing_detectados:
        salida = archivo.replace(".txt", "_pagos_leasing_detectados.xlsx")
        pd.DataFrame(leasing_detectados).to_excel(salida, index=False)

        return {
            "nombre_validacion": "Detección de subsidios LEASING en pagos",
            "resultado": "OBSERVACIONES",
            "detalle": [
                f"Línea {r['Línea TXT']} - RUT {r['RUT']} corresponde a LEASING"
                for r in leasing_detectados
            ]
        }

    return {
        "nombre_validacion": "Detección de subsidios LEASING en pagos",
        "resultado": "OK",
        "detalle": None
    }
