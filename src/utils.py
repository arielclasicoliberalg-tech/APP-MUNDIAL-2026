from datetime import datetime

def es_fecha_valida(fecha_partido, hora_partido):
    # Combina fecha y hora y compara con el momento actual
    fecha_str = f"{fecha_partido} {hora_partido}"
    dt_partido = datetime.strptime(fecha_str, '%Y-%m-%d %H:%M:%S')
    return datetime.now() < dt_partido