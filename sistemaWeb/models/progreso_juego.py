from django.db import models
from django.contrib.auth.models import User 

# models.py
class ProgresoJuego(models.Model):
    # Sin primary_key=True. Django creará la columna 'id' automática.
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name="progreso")
    cantidadMsjDesbloqueados = models.IntegerField(default=3)
    cantidadApzjDesbloqueados = models.IntegerField(default=1)
    fechaJuego = models.DateField(null=True, blank=True)
    experiencia = models.IntegerField(default=0)
    
    def __str__(self):
        return f"{self.usuario.first_name} - Msj: {self.cantidadMsjDesbloqueados} - Apzj: {self.cantidadApzjDesbloqueados}"