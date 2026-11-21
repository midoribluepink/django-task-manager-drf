from django.db import models
from django.conf import settings

class Tarea(models.Model):
    titulo = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)
    fecha_limite = models.DateField(null=True, blank=True)
    completada = models.BooleanField(default=False)
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    def __str__(self):
        return f"{self.titulo[:25]}: {self.completada}" 