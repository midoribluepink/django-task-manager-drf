from rest_framework import serializers
from core.models import Tarea

from django.utils import timezone

class TareaSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    titulo = serializers.CharField(max_length=100)
    descripcion = serializers.CharField(allow_blank=True)
    fecha_limite = serializers.DateField(allow_null=True, required=False)
    completada = serializers.BooleanField(default=False)

    def create(self, validated_data):
        tarea_creada = Tarea.objects.create(**validated_data)
        return tarea_creada

    def update(self, instance, validated_data):
        for campo, valor in validated_data.items():
            setattr(instance, campo, valor)

        instance.save()

        return instance


class TareaModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tarea
        fields = ["id", "titulo", "descripcion", "fecha_limite", "completada"]

    # Validación de prueba que excluye títulos que inician con [borrador]
    def validate_titulo(self, value):

        if value.lower().startswith("[borrador]"):
            raise serializers.ValidationError("El título no puedo comenzar con ['borrador']")

        return value

    # Validar que una tarea completada no puede tener fecha límite futura (condición artificial)
    def validate(self, attrs):
        hoy = timezone.localdate()

        if "fecha_limite" in attrs:
            fecha_limite = attrs["fecha_limite"]
        elif self.instance is not None:
            fecha_limite = self.instance.fecha_limite
        else:
            fecha_limite = None

        if "completada" in attrs:
            completada = attrs["completada"]
        elif self.instance is not None:
            completada = self.instance.completada
        else:
            completada = False

        if fecha_limite is not None and fecha_limite > hoy and completada:
            raise serializers.ValidationError("No puede haber tarea completada con fecha límite futura")

        return attrs
