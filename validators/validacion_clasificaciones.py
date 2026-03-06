import pandas as pd
import re
from datetime import datetime

# === Validar RUT chileno ===
def validar_rut_numero(rut: str, dv: str) -> bool:
    """
    Valida un RUT chileno con algoritmo módulo 11.
    """
    try:
        rut = rut.zfill(8)
        reversed_digits = map(int, reversed(rut))
        factors = [2, 3, 4, 5, 6, 7]
        s = sum(d * factors[i % 6] for i, d in enumerate(reversed_digits))
        mod = 11 - (s % 11)
        dv_calc = "0" if mod == 11 else "K" if mod == 10 else str(mod)
        return dv_calc == dv.upper()
    except Exception:
        return False


# === Validación principal ===
def validar_clasificaciones(archivo):
    """
    Valida la estructura y contenido del archivo de Rebaja Clasificaciones.
    """
    errores = []

    try:
        df = pd.read_csv(archivo, sep=';', header=None, dtype=str, encoding='latin1')
        df = df.fillna('')

        # --- Validar número de columnas ---
        if df.shape[1] != 17:
            errores.append({
                "Línea": "TODAS",
                "Tipo": "Estructura",
                "Descripción": f"El archivo tiene {df.shape[1]} columnas, se esperaban 17.",
                "Valores": ""
            })
            return exportar_errores(archivo, errores)

        # --- Validar fila a fila ---
        for i, fila in df.iterrows():
            linea = i + 1
            rut = fila[0].strip()
            dv = fila[1].strip().upper()
            fecha_credito = fila[10].strip()

            # 1️⃣ Validar RUT
            if not rut.isdigit() or len(rut) > 10:
                errores.append({
                    "Línea": linea,
                    "Tipo": "Formato inválido",
                    "Descripción": "RUT no numérico o con largo incorrecto",
                    "Valores": rut
                })
            elif not re.match(r'^[0-9Kk]{1}$', dv):
                errores.append({
                    "Línea": linea,
                    "Tipo": "Formato inválido",
                    "Descripción": "Dígito verificador inválido",
                    "Valores": dv
                })
            elif not validar_rut_numero(rut, dv):
                errores.append({
                    "Línea": linea,
                    "Tipo": "Inconsistencia",
                    "Descripción": "RUT no válido (módulo 11)",
                    "Valores": f"{rut}-{dv}"
                })

            # 2️⃣ Validar fecha crédito (ddmmaaaa)
            if fecha_credito:
                try:
                    datetime.strptime(fecha_credito, "%d%m%Y")
                except ValueError:
                    errores.append({
                        "Línea": linea,
                        "Tipo": "Formato inválido",
                        "Descripción": "Fecha de crédito inválida",
                        "Valores": fecha_credito
                    })
            else:
                errores.append({
                    "Línea": linea,
                    "Tipo": "Dato faltante",
                    "Descripción": "Fecha de crédito vacía",
                    "Valores": ""
                })

            # 3️⃣ Validar campos numéricos
            for idx in [5, 6, 7, 13, 14]:  # Región, Comuna, Entidad, Cuotas totales, Saldo cuotas
                val = fila[idx].strip()
                if val and not val.isdigit():
                    errores.append({
                        "Línea": linea,
                        "Tipo": "Formato inválido",
                        "Descripción": f"Valor no numérico en columna {idx+1}",
                        "Valores": val
                    })

            # 4️⃣ Validar decimales (montos)
            for idx in [11, 12, 15, 16]:
                val = fila[idx].replace(',', '.').strip()
                if val:
                    try:
                        float(val)
                    except ValueError:
                        errores.append({
                            "Línea": linea,
                            "Tipo": "Formato inválido",
                            "Descripción": f"Valor decimal inválido en columna {idx+1}",
                            "Valores": val
                        })

        return exportar_errores(archivo, errores)

    except Exception as e:
        return f"Error inesperado en validar_clasificaciones: {str(e)}"


# === Exportar errores a Excel ===
def exportar_errores(archivo, errores):
    """
    Exporta errores a Excel (columnas ordenadas) y genera resumen legible en pantalla.
    """
    if errores:
        df_errores = pd.DataFrame(errores, columns=["Línea", "Tipo", "Descripción", "Valores"])
        nombre_salida = archivo.replace('.txt', '_errores_clasificaciones.xlsx')
        df_errores.to_excel(nombre_salida, index=False)

        # Mostrar resumen formateado
        listado = "\n".join([
            f"Línea {e['Línea']} - {e['Tipo']}: {e['Descripción']} ({e['Valores']})"
            for e in errores[:20]
        ])
        if len(errores) > 20:
            listado += f"\n... y {len(errores)-20} errores más."

        return f"Se detectaron {len(errores)} errores.\n\n{listado}\n\nArchivo generado: {nombre_salida}"
    else:
        return "Validación completada sin errores ✅"
