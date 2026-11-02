from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Planta, ProgresoJuego, AporteAmbiental, AprendizajeJuego, MensajeJuego

class PlantaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Planta
        fields = '__all__'
        read_only_fields = ['usuario']

class MensajeSerializer(serializers.ModelSerializer):
    class Meta:
        model = MensajeJuego
        fields = '__all__'

class AprendizajeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AprendizajeJuego
        fields = '__all__'

class ProgresoSerializer(serializers.ModelSerializer):
    # Incluir los serializadores anidados utilizando el related_name correspondiente
    mensajes = MensajeSerializer(many=True, read_only=True)
    aprendizajes = AprendizajeSerializer(many=True, read_only=True)

    class Meta:
        model = ProgresoJuego
        fields = [
            'usuario',
            'cantidadMsjDesbloqueados',
            'cantidadApzjDesbloqueados',
            'fechaJuego',
            'experiencia',
            'mensajes',
            'aprendizajes'
        ]

class AporteSerializer(serializers.ModelSerializer):
    class Meta:
        model = AporteAmbiental
        fields = '__all__'

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = User
        fields = ['username', 'password', 'email', 'first_name', 'last_name']

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
            email=validated_data.get('email', ''),
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', '')
        )
        return user