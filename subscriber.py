import pika
import json
import django
import os
from sys import path

path.append('/home/ubuntu/latencia')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import authenticate

# ---- Configuración del broker ----
rabbit_host     = '172.31.42.38'
rabbit_user     = 'broker_user'
rabbit_password = 'isis2503'
exchange        = 'user_requests'
topics          = ['usuarios.#']

# ---- Conexión ----
connection = pika.BlockingConnection(
    pika.ConnectionParameters(
        host=rabbit_host,
        credentials=pika.PlainCredentials(rabbit_user, rabbit_password)
    )
)
channel = connection.channel()
channel.exchange_declare(exchange=exchange, exchange_type='topic')

result     = channel.queue_declare('', exclusive=True)
queue_name = result.method.queue

for topic in topics:
    channel.queue_bind(exchange=exchange, queue=queue_name, routing_key=topic)

def callback(ch, method, properties, body):
    payload = json.loads(body.decode('utf-8'))
    print("Solicitud recibida:", payload)
    user = authenticate(username=payload['username'], password=payload['password'])
    if user is not None:
        print(f"Autenticacion exitosa: {user.username}")
    else:
        print("Autenticacion fallida")

channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)
print('> Esperando solicitudes. CTRL+C para salir.')
channel.start_consuming()
