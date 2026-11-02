from django.db import models
from django.contrib.auth.models import User 

class ProgresoJuego(models.Model):
    usuario = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name="progreso",
        primary_key=True  # <--- Asigna el ID del User como la PK propia del progreso
    )
    cantidadMsjDesbloqueados = models.PositiveIntegerField(default=0)
    cantidadApzjDesbloqueados = models.PositiveIntegerField(default=0)
    fechaJuego = models.DateField(auto_now_add=False, blank=True, null=True)
    experiencia = models.PositiveIntegerField(default=0)
    
    def __str__(self):
        return f"{self.usuario.first_name} - Msj: {self.cantidadMsjDesbloqueados} - Apzj: {self.cantidadApzjDesbloqueados}"