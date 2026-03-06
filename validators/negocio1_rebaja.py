from validators.validacion_estructura import validar_estructura

def placeholder(*args, **kwargs):
    """Función temporal hasta implementar la validación real."""
    return True

VALIDACIONES_REBAJA = [
    ("Revisión de estructura del archivo (formatos)",
     lambda archivo: validar_estructura(archivo, "Negocio1 - Rebaja")[0]),
    ("Revisar y contar los registros con todos los estados", placeholder),
    ("Revisar dividendos duplicados en el mismo periodo", placeholder),
    ("Revisar montos donde superan las 20 UF", placeholder),
    ("Revisar los cuotones", placeholder),
    ("Revisar periodos en el archivo", placeholder),
    ("Revisar existencia de RUT y número de operación", placeholder),
    ("Revisión de cuotas pagadas (pagos retroactivos)", placeholder),
    ("Revisión de estados de vigencia y saldo cuotas", placeholder),
    ("Generar reporte de procesos anteriores", placeholder),
    ("Generar archivos de resultado y periodo", placeholder),
    ("Proceso especial de separación (6 meses)", placeholder),
    ("Generar informes desde archivos de nóminas", placeholder)
]
