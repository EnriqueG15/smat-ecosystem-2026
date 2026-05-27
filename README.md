## 📡 Módulo IoT: Emulación de Hardware y Telemetría

Este directorio (`/iot_device`) contiene el script `sensor_emitter.py`, el cual actúa como un dispositivo Edge (simulando un microcontrolador como un ESP32 o Raspberry Pi). Su función principal es generar lecturas emuladas de nivel de agua y transmitirlas automáticamente al backend (FastAPI).

### 🔐 Comunicación con la Nube y Seguridad (JWT)

Para asegurar que solo los dispositivos autorizados puedan enviar datos al sistema SMAT, la comunicación mediante el protocolo HTTP está protegida con autenticación basada en **JSON Web Tokens (JWT)**.

El flujo de comunicación funciona de la siguiente manera:
1. **Autorización en Cabeceras:** El script de Python utiliza la librería `requests` para armar una petición `POST` dirigida a la API REST. 
2. **Inyección del Token:** En cada envío, el script inyecta un Token JWT (previamente generado por el sistema) dentro de los *headers* de la petición HTTP, utilizando el formato estándar: `Authorization: Bearer <TOKEN>`.
3. **Validación:** Cuando la nube (nuestro servidor backend) recibe el payload con la telemetría, primero intercepta la petición, verifica la firma y validez del Token JWT, y si es correcto, procesa y almacena la lectura en la base de datos.

### 🚨 Lógica de "Alerta de Desborde" (Edge Computing)
El dispositivo no solo envía datos a ciegas, sino que cuenta con lógica local:
* **Estado Normal:** Si el nivel del río es menor a 70.0 cm, envía telemetría cada 10 segundos.
* **Modo Emergencia:** Si la lectura supera los 70.0 cm, el dispositivo entra en alerta e incrementa la frecuencia de envío a cada 2 segundos, permitiendo al sistema reaccionar rápidamente ante una posible inundación.s