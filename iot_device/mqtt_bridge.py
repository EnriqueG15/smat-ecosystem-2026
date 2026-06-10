import paho.mqtt.client as mqtt
import requests
import json
import sys
import time  

MQTT_BROKER = "broker.hivemq.com"  #
MQTT_PORT = 1883  #
MQTT_TOPIC = "fisi/smat/estaciones/+/lecturas"  # El '+' es un wildcard para el ID de la estación
API_URL = "http://localhost:8000/lecturas/"  #

# Token JWT generado previamente desde Swagger o la App móvil para el usuario administrador
JWT_TOKEN = "eyJhbGciOiJIUzI1NilsInR5cCl6lkpXVCJ9..."  #

cache_estaciones = {}

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print(" Conectado exitosamente al Broker MQTT")  #
        # Suscribirse al tópico global de lecturas de estaciones
        client.subscribe(MQTT_TOPIC)  #
        print(f" Escuchando transmisiones en el tópico: {MQTT_TOPIC}")  #
    else:
        print(f" Error de conexión al Broker. Código de retorno: {rc}")  #
        sys.exit(1)  #

def on_message(client, userdata, msg):
    try:
        payload_raw = msg.payload.decode("utf-8")  #
        data_json = json.loads(payload_raw)  #
        
        topic_parts = msg.topic.split('/')  #
        estacion_id = int(topic_parts[3])  #
        print(f" Telemetria recibida de Estación [{estacion_id}]: {data_json}")  #
        
        nuevo_valor = float(data_json["valor"])
        current_time = time.time()
        debe_enviar = False
        motivo_envio = ""

        if estacion_id not in cache_estaciones:
            # Si es el primer dato que llega de esta estación, se transmite obligatoriamente
            debe_enviar = True
            motivo_envio = "Primer registro de esta estación"
        else:
            ultimo_registro = cache_estaciones[estacion_id]
            ultimo_valor = ultimo_registro["valor"]
            ultimo_timestamp = ultimo_registro["timestamp"]
            
            # Calcular la variación porcentual evitando división por cero si el último fue 0
            if ultimo_valor != 0:
                variacion = abs(nuevo_valor - ultimo_valor) / ultimo_valor
            else:
                variacion = 1.0 if nuevo_valor != 0 else 0.0
                
            tiempo_transcurrido = current_time - ultimo_timestamp
            
            # Condición 1: Variación mayor al ± 5%
            if variacion > 0.05:
                debe_enviar = True
                motivo_envio = f"Variación significativa detectada ({variacion * 100:.1f}%)"
            # Condición 2: Reporte mínimo de vida superó los 60 segundos
            elif tiempo_transcurrido > 60:
                debe_enviar = True
                motivo_envio = f"Reporte mínimo de vida alcanzado ({tiempo_transcurrido:.1f}s transcurridos)"

        if debe_enviar:
            api_payload = {
                "valor": nuevo_valor,  #
                "estacion_id": estacion_id  #
            }
            
            headers = {
                "Content-Type": "application/json",  #
                "Authorization": f"Bearer {JWT_TOKEN}"  #
            }
            
            response = requests.post(API_URL, json=api_payload, headers=headers)  #
            
            if response.status_code == 200 or response.status_code == 201:  #
                print(f" [DB Sincronizada] Lectura de {api_payload['valor']} cm guardada en SQLite. Motivo: {motivo_envio}")  #
                
                # Actualizar la caché local ÚNICAMENTE tras una inserción HTTP exitosa
                cache_estaciones[estacion_id] = {
                    "valor": nuevo_valor,
                    "timestamp": current_time
                }
            else:
                print(f" [Fallo de Ingesta] API rechazó el dato. Código: {response.status_code} -\n{response.text}")  #
        else:
            # Requisito de Validación: Mostrar visualmente en consola los datos bloqueados redundantes
            print(f" ⏳ [Filtro Activo] Petición HTTP Bloqueada. Dato redundante ({nuevo_valor} cm) no supera umbrales.")

    except KeyError as e:
        print(f" Error de esquema: Falta la llave {e} en el payload MQTT.")  #
    except ValueError:
        print("Error de casteo: El valor o el ID de la estación no son numéricos.")  #
    except Exception as e:
        print(f"Error critico en el Bridge: {e}")  #

# ==========================================
# INICIALIZACIÓN DEL CLIENTE MQTT
# ==========================================
bridge_client = mqtt.Client()  #
bridge_client.on_connect = on_connect  #
bridge_client.on_message = on_message  #

try:
    print(" Inicializando el Bridge de Acoplamiento SMAT...")  #
    bridge_client.connect(MQTT_BROKER, MQTT_PORT, 60)  #
    # Mantener el hilo escuchando activamente de forma sincrona
    bridge_client.loop_forever()  #
except KeyboardInterrupt:
    print("\n Bridge detenido por el administrador.")  #