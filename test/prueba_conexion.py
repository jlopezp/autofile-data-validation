from sqlalchemy import create_engine, text

# ==== CREDENCIALES (ajusta según tu servidor) ====
usuario = "USER"          # tu usuario SQL
contrasena = "123456"    # tu contraseña SQL
servidor = "DESARROLLO"  # puede ser "localhost", ".", "127.0.0.1" o "SERVIDOR\SQLEXPRESS"
base_datos = "ORIGEN2"  # nombre de la BD
driver = "ODBC Driver 17 for SQL Server"  # o "ODBC Driver 18 for SQL Server"

# ==== CADENA DE CONEXIÓN ====
cadena_conexion = (
    f"mssql+pyodbc://{usuario}:{contrasena}@{servidor}/{base_datos}"
    f"?driver={driver.replace(' ', '+')}"
)

try:
    # Crear el engine
    engine = create_engine(cadena_conexion)

    # Probar conexión con una consulta simple
    with engine.connect() as conexion:
        resultado = conexion.execute(text("SELECT GETDATE() as fecha"))
        fila = resultado.fetchone()
        print("✅ Conexión exitosa a SQL Server")
        print(f"Fecha del servidor SQL: {fila.fecha}")

except Exception as e:
    print("❌ Error al conectar con SQL Server")
    print(e)
