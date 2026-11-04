from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from ..models import MensajeJuego, ProgresoJuego
from ..serializer import MensajeSerializer

class MensajeVista(viewsets.ModelViewSet):
    serializer_class = MensajeSerializer
    queryset = MensajeJuego.objects.all()
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get_queryset(self):
        return MensajeJuego.objects.filter(progreso__usuario=self.request.user)

    def perform_create(self, serializer):
        # Asigna automáticamente el ProgresoJuego correspondiente al usuario autenticado
        progreso = ProgresoJuego.objects.get(usuario=self.request.user)
        serializer.save(progreso=progreso)