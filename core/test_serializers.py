from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from core.serializers import TareaModelSerializer
from core.models import Tarea

class TareaSerializerTests(TestCase):

    def test_tarea_completada_con_fecha_futura(self):
        hoy = timezone.localdate()
        futura = hoy + timedelta(days=5)

        serializer = TareaModelSerializer(data={
            "titulo": "Titulo de prueba",
            "descripcion": "",
            "fecha_limite": futura,
            "completada": True
        })

        self.assertFalse(serializer.is_valid())
        self.assertIn("non_field_errors",serializer.errors)

    def test_patch_tarea_completada_con_fecha_futura(self):
        hoy = timezone.localdate()
        futura = hoy + timedelta(days=5)

        tarea = Tarea.objects.create(
            titulo="Titulo de prueba",
            fecha_limite=futura,
            completada=False
        )

        serializer = TareaModelSerializer(tarea, data={"completada": True}, partial=True)

        self.assertFalse(serializer.is_valid())
        self.assertIn("non_field_errors", serializer.errors)

        tarea.refresh_from_db()

        self.assertFalse(tarea.completada)

    def test_patch_tarea_valida(self):
        hoy = timezone.localdate()
        futura = hoy + timedelta(days=5)


        tarea = Tarea.objects.create(
            titulo="Tarea de prueba",
            fecha_limite=futura,
            completada=False
        )

        serializer = TareaModelSerializer(
            tarea,
            data={
                "fecha_limite": None,
                "completada": True
            },
            partial=True
        )

        self.assertTrue(serializer.is_valid())
        serializer.save()

        tarea.refresh_from_db()

        self.assertTrue(tarea.completada)
        self.assertIsNone(tarea.fecha_limite)