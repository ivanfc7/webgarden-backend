from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from ..models import AprendizajeJuego, ProgresoJuego
from ..serializer import AprendizajeSerializer

class AprendizajeVista(viewsets.ModelViewSet):
    serializer_class = AprendizajeSerializer
    queryset = AprendizajeJuego.objects.all()
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get_queryset(self):
        return AprendizajeJuego.objects.filter(progreso__usuario=self.request.user)

    def perform_create(self, serializer):
        # Asigna automáticamente el ProgresoJuego correspondiente al usuario autenticado
        progreso = ProgresoJuego.objects.get(usuario=self.request.user)
        serializer.save(progreso=progreso)