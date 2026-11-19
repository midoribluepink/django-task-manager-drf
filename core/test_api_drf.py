from django.test import TestCase
from core.models import Tarea
from datetime import date

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

    def test_get_tarea_inexistente(self):
        url = "/api/tareas-drf/9999/"

        respuesta = self.client.get(url)
        datos_respuesta = respuesta.json()

        self.assertEqual(respuesta.status_code, 404)
        self.assertIn("detail", datos_respuesta)

class TareaAPIDRFTestsConDatos(TestCase):
    def setUp(self):
        self.tarea1 = Tarea.objects.create(
            titulo="Tarea1",
            descripcion="",
            fecha_limite=date(2026,12,12),
            completada=False
        )
        self.tarea2 = Tarea.objects.create(
            titulo="Tarea2",
            descripcion="",
            fecha_limite=None,
            completada=True
        )

    def test_get_tarea_existente(self):

        url = f"/api/tareas-drf/{self.tarea1.id}/"

        respuesta = self.client.get(url)
        datos_respuesta = respuesta.json()

        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(self.tarea1.id, datos_respuesta["id"])
        self.assertEqual(self.tarea1.titulo, datos_respuesta["titulo"])
        self.assertEqual(self.tarea1.descripcion, datos_respuesta["descripcion"])
        self.assertEqual(self.tarea1.fecha_limite, date.fromisoformat(datos_respuesta["fecha_limite"]))
        self.assertEqual(self.tarea1.completada, datos_respuesta["completada"])

    def test_patch_tarea_valida(self):

        url = f"/api/tareas-drf/{self.tarea1.id}/"

        respuesta = self.client.patch(
            url,
            data={"descripcion": "Nueva descripción"},
            content_type="application/json"
        )

        datos_respuesta = respuesta.json()

        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(datos_respuesta["titulo"], self.tarea1.titulo)
        self.assertEqual(datos_respuesta["descripcion"], "Nueva descripción")

        self.tarea1.refresh_from_db()

        self.assertEqual("Nueva descripción", self.tarea1.descripcion)
        self.assertEqual(date(2026,12,12), self.tarea1.fecha_limite)
        self.assertFalse(self.tarea1.completada)

    def test_patch_tarea_invalida(self):
        url = f"/api/tareas-drf/{self.tarea1.id}/"

        respuesta = self.client.patch(
            url,
            data={"titulo": "[BORRADOR] Tarea modificada"},
            content_type="application/json"
        )

        datos_respuesta = respuesta.json()

        self.assertEqual(respuesta.status_code, 400)
        self.assertIn("titulo", datos_respuesta)

        self.tarea1.refresh_from_db()

        self.assertEqual(self.tarea1.titulo, "Tarea1")

    def test_put_tarea_campos_omitidos(self):

        url = f"/api/tareas-drf/{self.tarea2.id}/"

        respuesta = self.client.put(
            url,
            data={
                "titulo": "Título actualizado",
                "descripcion": "Descripción actualizada"
            },
            content_type="application/json"
        )

        self.assertEqual(respuesta.status_code, 200)

        self.tarea2.refresh_from_db()

        self.assertTrue(self.tarea2.completada)
        self.assertIsNone(self.tarea2.fecha_limite)
        self.assertEqual("Título actualizado", self.tarea2.titulo)
        self.assertEqual("Descripción actualizada", self.tarea2.descripcion)
