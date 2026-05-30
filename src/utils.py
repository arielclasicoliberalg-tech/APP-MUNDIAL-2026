from datetime import datetime
import pytz

def es_fecha_valida(fecha_partido, hora_partido):
    fecha_str = f"{fecha_partido} {hora_partido}"
    dt_partido = datetime.strptime(fecha_str, '%Y-%m-%d %H:%M:%S')
    
    # Zona horaria Bolivia
    tz_bolivia = pytz.timezone('America/La_Paz')
    ahora_bolivia = datetime.now(tz_bolivia).replace(tzinfo=None)
    
    return ahora_bolivia < dt_partido
