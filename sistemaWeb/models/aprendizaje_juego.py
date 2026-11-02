from django.db import models
from .progreso_juego import ProgresoJuego

class AprendizajeJuego(models.Model):
    progreso = models.ForeignKey(ProgresoJuego, on_delete=models.CASCADE, related_name='aprendizajes')
    titulo = models.CharField(max_length=150)
    contenido = models.TextField()
    imagen = models.CharField(max_length=200)
    fuente = models.TextField()
    desbloqueado = models.BooleanField(default=False)

    class Meta:
        unique_together = ('progreso', 'titulo') 

    def __str__(self):
        return f"{self.titulo} - {self.desbloqueado}"