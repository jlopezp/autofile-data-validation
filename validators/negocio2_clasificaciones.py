from validators.validacion_estructura import validar_estructura

def placeholder(*args, **kwargs):
    """Función temporal hasta implementar la validación real."""
    return True

VALIDACIONES_CLASIFICACIONES = [
    ("Revisión de estructura de archivo (formato)",
     lambda archivo: validar_estructura(archivo, "Negocio2 - Clasificaciones")[0]),
    ("Revisar y contar los registros con todos los estados", placeholder),
    ("Cuadrar columnas 12,13,16 (monto crédito)", placeholder),
    ("Cuadrar columnas 14,15 (cuotas)", placeholder),
    ("Revisión de clasificados y rechazados", placeholder),
    ("Revisión existencia de clasificados en base de datos", placeholder),
    ("Revisión de beneficiados DS15 (pendiente)", placeholder),
    ("Clientes sobre 1200 UF (otra lista)", placeholder),
    ("Clientes sobre 1600 UF (pendiente, DS15)", placeholder),
    ("Asignación de % beneficio según criterios", placeholder),
    ("Generar informe Excel con clasificados y rechazados", placeholder)
]
