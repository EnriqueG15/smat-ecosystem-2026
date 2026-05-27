import requests
import time
import random

# CONFIGURACIÓN
API_URL = "http://localhost:8000/lecturas/"
ESTACION_ID = 1 # ID de la estación registrada en la DB
TOKEN = "TU_TOKEN_JWT_AQUI" # Obtenido del login

def leer_sensor_emulado():
    # Simulamos una lectura de nivel de río (0 a 100 cm)
    return round(random.uniform(10.5, 85.0), 2)

def enviar_telemetria():
    print(f"--- Iniciando Emisor IOT para Estación {ESTACION_ID} ---")
    
    while True:
        valor = leer_sensor_emulado()
        payload = {
            "valor": valor,
            "estacion_id": ESTACION_ID
        }
        headers = {
            "Authorization": f"Bearer {TOKEN}"
        }
        
        try:
            response = requests.post(API_URL, json=payload, headers=headers)
            if response.status_code == 200:
                print(f"[OK] Lectura enviada: {valor} cm")
            else:
                print(f"[ERROR] Código: {response.status_code}")
        except Exception as e:
            print(f"[CRÍTICO] No hay conexión con el servidor: {e}")
        
        # --- LÓGICA DEL RETO: ALERTA DE DESBORDE ---
        if valor > 70.0:
            print("[ALERTA] Umbral de inundación superado.")
            tiempo_espera = 2 # Modo de Emergencia
        else:
            tiempo_espera = 10 # Frecuencia dinámica normal
            
        # Esperar el tiempo definido antes de la siguiente iteración
        time.sleep(tiempo_espera)

if __name__ == "__main__":
    enviar_telemetria()