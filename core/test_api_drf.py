from django.test import TestCase
from core.models import Tarea

class TareaAPIDRFTests(TestCase):

    def test_post_tarea_invalida(self):
        self.assertEqual(Tarea.objects.count(), 0)

        respuesta = self.client.post(
            "/api/tareas-drf/",
            data={
                "titulo": "[BORRADOR] Titulo de prueba",
                "completada": False
            },
            content_type="application/json"
        )

        datos_respuesta = respuesta.json()

        self.assertEqual(respuesta.status_code, 400)
        self.assertIn("titulo", datos_respuesta)
        self.assertEqual(Tarea.objects.count(), 0)

    def test_post_tarea_valida(self):

        respuesta = self.client.post(
            "/api/tareas-drf/",
            data={
                "titulo": "Aprender DRF",
                "descripcion": "Estudiar las vistas",
                "completada": False
            },
            content_type="application/json"
        )

        datos_respuesta = respuesta.json()

        self.assertEqual(respuesta.status_code, 201)
        self.assertEqual(Tarea.objects.count(), 1)
        self.assertIn("id", datos_respuesta)
        self.assertEqual("Aprender DRF", datos_respuesta["titulo"])
        self.assertEqual("Estudiar las vistas", datos_respuesta["descripcion"])

        tarea = Tarea.objects.get(id=datos_respuesta["id"])

        self.assertEqual("Aprender DRF", tarea.titulo)
        self.assertEqual("Estudiar las vistas", tarea.descripcion)
        self.assertIsNone(tarea.fecha_limite)
        self.assertFalse(tarea.completada)