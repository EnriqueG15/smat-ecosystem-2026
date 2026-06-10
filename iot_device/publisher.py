import time
import random
import json
import paho.mqtt.client as mqtt

BROKER = "broker.hivemq.com"
PUERTO = 1883

ESTACIONES = [1, 2]

def conectar_mqtt():
    client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION2)
    print(f"Conectando al broker {BROKER}...")
    client.connect(BROKER, PUERTO, 60)
    return client

def main():
    cliente = conectar_mqtt()
    cliente.loop_start() # Iniciar el bucle de red en segundo plano
    
    contador_mensajes = 0
    # Valor base para simular niveles (cm) o temperatura estable
    valor_base = 45.0 
    
    try:
        while True:
            for estacion_id in ESTACIONES:
                contador_mensajes += 1
                
                topico = f"fisi/smat/estaciones/{estacion_id}/lecturas"
                
                datos_sensor = {
                    "timestamp": time.time(),
                    "unidad": "cm"
                }
                
                if contador_mensajes % 7 == 0:
                    # Falla Tipo 1: Valor fuera de límites físicos (>100) para probar la validación del Bridge
                    print(f"\n[SISTEMA] Inyectando Falla de Límite en Estación {estacion_id}...")
                    datos_sensor["valor"] = 150.0
                    
                elif contador_mensajes % 5 == 0:
                    # Falla Tipo 2: Tipo de dato incorrecto (String) para hacer saltar el 'except ValueError' del Bridge
                    print(f"\n[SISTEMA] Inyectando Falla Analógica (Texto) en Estación {estacion_id}...")
                    datos_sensor["valor"] = "ERROR_ANALOGICO"
                    
                elif contador_mensajes % 3 == 0:
                    # Flujo de Cambio Brusco: Variación fuerte (> 5%) para obligar al Bridge a dejar pasar el dato
                    print(f"\n[SISTEMA] Generando variación significativa (>5%) en Estación {estacion_id}...")
                    datos_sensor["valor"] = round(valor_base + random.uniform(8.0, 15.0), 2)
                    
                else:
                    # Flujo Normal Redundante: Variaciones insignificantes (< 5%) 
                    # Esto sirve para demostrar que tu filtro Deadband funciona y BLOQUEA el tráfico en el Bridge
                    datos_sensor["valor"] = round(valor_base + random.uniform(-0.2, 0.2), 2)
                
                # Serializar a formato JSON
                mensaje = json.dumps(datos_sensor)
                
                # Publicar el mensaje con QoS 1
                info = cliente.publish(topico, mensaje, qos=1)
                info.wait_for_publish()
                
                print(f"[PUBLISHER] Enviado a {topico}: {mensaje}")
                
                # Esperar 2.5 segundos entre transmisiones intercaladas
                time.sleep(2.5)
                
    except KeyboardInterrupt:
        print("\nDeteniendo publicador del reto...")
    finally:
        cliente.loop_stop()
        cliente.disconnect()

if __name__ == "__main__":
    main()