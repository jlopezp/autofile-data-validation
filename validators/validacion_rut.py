# ================================================================
# Archivo: validators/validacion_rut.py
# Descripción:
#   Valida que los RUT y número de operación del archivo existan en
#   las tablas de los decretos DS02, DS12, DS51 (y reprogramaciones).
#   - Devuelve resultados estructurados para informes detallados.
#   - Incluye DataFrame con todas las columnas del archivo original.
#
# Autor: José López
# Institución: TRANSFORMACION DIGITAL
# Versión: v5.3 - Parámetros unificados y soporte dinámico reprogramaciones
# Fecha: 11/11/2025
# ================================================================

import pandas as pd
from sqlalchemy import text


def validar_rut_archivo(archivo, engine):
    """
    Valida existencia de RUT y número de operación en DS02, DS12 y DS51.
    Soporta reprogramaciones.

    Retorna:
    {
        "nombre_validacion": "Validación RUT y Operación",
        "resultado": "OK" / "Con observaciones" / "Error",
        "observaciones": str,
        "detalle": DataFrame (si hay no encontrados)
    }
    """
    try:
        # === 1. Leer archivo TXT ===
        df = pd.read_csv(archivo, sep=';', header=None, dtype=str, encoding='latin-1', na_filter=False)

        if df.shape[1] <= 4:
            return {
                "nombre_validacion": "Validación RUT y Operación",
                "resultado": "Error",
                "observaciones": f"El archivo tiene solo {df.shape[1]} columnas (se esperaban al menos 5).",
                "detalle": None
            }

        df["RUT"] = df.iloc[:, 1].str.strip()
        df["NUM_OP"] = df.iloc[:, 4].str.strip()
        df = df[(df["RUT"] != "") & (df["NUM_OP"] != "")]

        if df.empty:
            return {
                "nombre_validacion": "Validación RUT y Operación",
                "resultado": "Error",
                "observaciones": "No se encontraron registros válidos con RUT y número de operación.",
                "detalle": None
            }

        # === 2. Consultas SQL por decreto ===
        queries = [
            ("DS02", "Principal", """
                SELECT COUNT(*) AS existe
                FROM PRODUCCION_MIGRA_TITULAR_CREDITO_DS02
                WHERE TIT_CRE_DS02_EST_VIG = 1
                  AND TIT_CRE_DS02_MAS_EST = 1
                  AND TIT_CRE_DS02_RUT = :rut
                  AND TIT_CRE_DS02_NUM_OPR_CRE_ORIG = :num_op
            """),
            ("DS02", "Reprogramación", """
                SELECT COUNT(*) AS existe
                FROM PRODUCCION_MIGRA_TITULAR_CREDITO_REPROGRAMACION_DS02 a
                JOIN PRODUCCION_MIGRA_TITULAR_CREDITO_DS02 b ON a.TIT_CRE_DS02_ID = b.TIT_CRE_DS02_ID
                WHERE b.TIT_CRE_DS02_EST_VIG = 1
                  AND b.TIT_CRE_DS02_RUT = :rut
                  AND a.REP_CRE_DS02_NUM_OPR = :num_op
            """),
            ("DS12", "Principal", """
                SELECT COUNT(*) AS existe
                FROM PRODUCCION_MIGRA_TITULAR_CREDITO_DS12
                WHERE TIT_CRE_DS12_MAS_EST = 1
                  AND TIT_CRE_DS12_RUT = :rut
                  AND TIT_CRE_DS12_NUM_OPR_CRE_ORIG = :num_op
            """),
            ("DS12", "Reprogramación", """
                SELECT COUNT(*) AS existe
                FROM PRODUCCION_MIGRA_TITULAR_CREDITO_REPROGRAMACION_DS12 a
                JOIN PRODUCCION_MIGRA_TITULAR_CREDITO_DS12 b ON a.TIT_CRE_DS12_ID = b.TIT_CRE_DS12_ID
                WHERE b.TIT_CRE_DS12_EST_VIG = 1
                  AND b.TIT_CRE_DS12_RUT = :rut
                  AND a.REP_CRE_DS12_NUM_OPR = :num_op
            """),
            ("DS51", "Principal", """
                SELECT COUNT(*) AS existe
                FROM PRODUCCION_MIGRA_PET_TITULAR_CREDITO
                WHERE TIT_MAS_EST = 1
                  AND TIT_RUT = :rut
                  AND TIT_NUM_OP_CRE_ORIG = :num_op
            """),
            ("DS51", "Reprogramación", """
                SELECT COUNT(*) AS existe
                FROM PRODUCCION_MIGRA_PET_TITULAR_CREDITO_REPROGRAMACION a
                JOIN PRODUCCION_MIGRA_PET_TITULAR_CREDITO b ON a.TIT_ID = b.TIT_ID
                WHERE b.TIT_MAS_EST = 1
                  AND b.TIT_RUT = :rut
                  AND a.REP_NUM_OP = :num_op
            """)
        ]

        resultados = []
        conteo = {"DS02": 0, "DS12": 0, "DS51": 0}

        # === 3. Ejecutar validaciones ===
        with engine.connect() as conn:
            for _, row in df.iterrows():
                rut = row["RUT"]
                num_op = row["NUM_OP"]
                hallado = None

                for decreto, fuente, sql in queries:
                    try:
                        r = conn.execute(text(sql), {"rut": rut, "num_op": num_op}).fetchone()
                        existe = r[0] if isinstance(r, tuple) else getattr(r, "existe", 0)
                        if existe and int(existe) > 0:
                            hallado = (decreto, fuente)
                            conteo[decreto] = conteo.get(decreto, 0) + 1
                            break
                    except Exception as e:
                        print(f"[Error SQL en {decreto}] {e}")
                        continue

                if hallado:
                    resultados.append((rut, num_op, f"✅ Encontrado en {hallado[0]}", hallado[1]))
                else:
                    resultados.append((rut, num_op, "❌ No encontrado", ""))

        # === 4. Integrar resultados al DataFrame original ===
        df_result = pd.DataFrame(resultados, columns=["RUT", "NUM_OP", "Resultado", "Fuente"])
        df_merged = df.merge(df_result, on=["RUT", "NUM_OP"], how="left")

        # Filtrar no encontrados
        df_no_encontrados = df_merged[df_merged["Resultado"].str.startswith("❌")]

        total_ok = len(df_merged) - len(df_no_encontrados)
        total_err = len(df_no_encontrados)

        observaciones = (
            f"✅ {total_ok} encontrados | ❌ {total_err} no encontrados.\n"
            f"DS02: {conteo['DS02']} | DS12: {conteo['DS12']} | DS51: {conteo['DS51']}"
        )

        resultado = "OK" if total_err == 0 else "Con observaciones"

        return {
            "nombre_validacion": "Validación RUT y Operación",
            "resultado": resultado,
            "observaciones": observaciones,
            "detalle": df_no_encontrados if total_err > 0 else None
        }

    except Exception as e:
        return {
            "nombre_validacion": "Validación RUT y Operación",
            "resultado": "Error",
            "observaciones": f"Error al validar RUT y número de operación: {e}",
            "detalle": None
        }
