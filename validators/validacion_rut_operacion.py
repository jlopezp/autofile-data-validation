# validators/validacion_rut_operacion.py
from sqlalchemy import text

def validar_rut_operacion(rut: str, op: str, engine):
    """
    Valida si un RUT y número de operación existen en DS02, DS51 o DS12
    incluyendo reprogramaciones.
    Retorna un diccionario con mensajes amigables.
    """
    consultas = {
        "DS02": """
            SELECT TOP 1 1
            FROM PRODUCCION_MIGRA_TITULAR_CREDITO_DS02
            WHERE TIT_CRE_DS02_RUT = :rut
              AND TIT_CRE_DS02_NUM_OPR_CRE_ORIG = :op
              AND TIT_CRE_DS02_MAS_EST = 1
              AND TIT_CRE_DS02_EST_VIG = 1
        """,
        "DS02_REP": """
            SELECT TOP 1 1
            FROM PRODUCCION_MIGRA_TITULAR_CREDITO_REPROGRAMACION_DS02 a
            JOIN PRODUCCION_MIGRA_TITULAR_CREDITO_DS02 b
              ON a.TIT_CRE_DS02_ID = b.TIT_CRE_DS02_ID
            WHERE b.TIT_CRE_DS02_RUT = :rut
              AND a.REP_CRE_DS02_NUM_OPR = :op
              AND b.TIT_CRE_DS02_EST_VIG = 1
        """,
        "DS51": """
            SELECT TOP 1 1
            FROM PRODUCCION_MIGRA_PET_TITULAR_CREDITO
            WHERE TIT_RUT = :rut
              AND TIT_NUM_OP_CRE_ORIG = :op
              AND TIT_MAS_EST = 1
        """,
        "DS51_REP": """
            SELECT TOP 1 1
            FROM PRODUCCION_MIGRA_PET_TITULAR_CREDITO_REPROGRAMACION a
            JOIN PRODUCCION_MIGRA_PET_TITULAR_CREDITO b ON a.TIT_ID = b.TIT_ID
            WHERE b.TIT_RUT = :rut
              AND a.REP_NUM_OP = :op
              AND b.TIT_MAS_EST = 1
        """,
        "DS12": """
            SELECT TOP 1 1
            FROM PRODUCCION_MIGRA_TITULAR_CREDITO_DS12
            WHERE TIT_CRE_DS12_RUT = :rut
              AND TIT_CRE_DS12_NUM_OPR_CRE_ORIG = :op
              AND TIT_CRE_DS12_MAS_EST = 1
        """,
        "DS12_REP": """
            SELECT TOP 1 1
            FROM PRODUCCION_MIGRA_TITULAR_CREDITO_REPROGRAMACION_DS12 a
            JOIN PRODUCCION_MIGRA_TITULAR_CREDITO_DS12 b
              ON a.TIT_CRE_DS12_ID = b.TIT_CRE_DS12_ID
            WHERE b.TIT_CRE_DS12_RUT = :rut
              AND a.REP_CRE_DS12_NUM_OPR = :op
              AND b.TIT_CRE_DS12_EST_VIG = 1
        """
    }

    resultados = {}
    with engine.connect() as conn:
        for modelo, sql in consultas.items():
            result = conn.execute(text(sql), {"rut": rut, "op": op}).fetchone()
            if result:
                resultados[modelo] = f"✅ Existe en {modelo}"
            else:
                resultados[modelo] = f"❌ No encontrado en {modelo}"

    return resultados
