from rest_framework import viewsets
from ..models import AprendizajeJuego
from ..serializer import AprendizajeSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

class AprendizajeVista(viewsets.ModelViewSet):
    serializer_class = AprendizajeSerializer
    queryset = AprendizajeJuego.objects.all()  # <--- Agrega esta línea
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get_queryset(self):
        return AprendizajeJuego.objects.filter(progreso__usuario=self.request.user)