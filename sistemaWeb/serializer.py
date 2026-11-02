from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Planta, ProgresoJuego, AporteAmbiental, AprendizajeJuego, MensajeJuego

class PlantaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Planta
        fields = '__all__'
        read_only_fields = ['usuario']

class ProgresoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProgresoJuego
        fields = '__all__'
        read_only_fields = ['usuario']

class AporteSerializer(serializers.ModelSerializer):
    class Meta:
        model = AporteAmbiental
        fields = '__all__'

class AprendizajeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AprendizajeJuego
        fields = '__all__'

class MensajeSerializer(serializers.ModelSerializer):
    class Meta:
        model = MensajeJuego
        fields = '__all__'

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = User
        fields = ['username', 'password', 'email', 'first_name', 'last_name']

    def create(self, validated_data):
        # Esto asegura que la contraseña se guarde hasheada
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
            email=validated_data.get('email', ''),
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', '')
        )
        return user