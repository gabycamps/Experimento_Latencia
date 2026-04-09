from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
import pika
import json

def publicar_evento(username, exitoso):
    try:
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host='172.31.42.38',
                credentials=pika.PlainCredentials('broker_user', 'isis2503')
            )
        )
        channel = connection.channel()
        channel.exchange_declare(exchange='user_requests', exchange_type='topic')
        payload = json.dumps({'username': username, 'autenticado': exitoso})
        channel.basic_publish(
            exchange='user_requests',
            routing_key='usuarios.autenticacion',
            body=payload
        )
        connection.close()
    except Exception as e:
        print(f"Error publicando al broker: {e}")

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            publicar_evento(username, True)   # publica al broker, no bloquea
            return redirect('home')
        else:
            publicar_evento(username, False)
            return render(request, 'login.html', {'error': 'Credenciales inválidas'})
    return render(request, 'login.html')

@login_required
def home(request):
    return render(request, 'home.html')
