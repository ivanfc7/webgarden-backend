from rest_framework import viewsets
from ..models import MensajeJuego
from ..serializer import MensajeSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

class MensajeVista(viewsets.ModelViewSet):
    serializer_class = MensajeSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get_queryset(self):
        # Filtra los mensajes asociados al progreso del usuario autenticado
        return MensajeJuego.objects.filter(progreso__usuario=self.request.user)