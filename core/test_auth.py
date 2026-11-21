from django.test import TestCase
from core.models import Tarea
from rest_framework import status
from django.contrib.auth import get_user_model

#--- PRUEBAS AUTOMATIZADAS DE AUTENTICACIÓN---
#---------------------------------------------

class AutenticationTests(TestCase):

    def test_quien_soy_anonimo(self):

        url = "/api/quien-soy/"
        respuesta = self.client.get(url)

        self.assertEqual(respuesta.status_code, status.HTTP_403_FORBIDDEN)

    def test_quien_soy_autenticado(self):

        url = "/api/quien-soy/"

        User = get_user_model()

        usuario = User.objects.create_user(
            username="test",
            password="test1234"
        )

        self.client.force_login(usuario)
        respuesta = self.client.get(url)
        datos_respuesta = respuesta.json()

        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
        self.assertTrue(datos_respuesta["autenticado"])
        self.assertEqual(usuario.username, datos_respuesta["usuario"])


class AutorizacionTareasTests(TestCase):

    def setUp(self):
        User = get_user_model()

        self.ana = User.objects.create_user(
            username="ana",
            password="ClaveAna123!"
        )

        self.luis = User.objects.create_user(
            username="luis",
            password="ClaveLuis123!"
        )

        self.tarea_ana = Tarea.objects.create(
            titulo="Tarea de Ana",
            usuario=self.ana
        )

        self.tarea_luis = Tarea.objects.create(
            titulo="Tarea de Luis",
            usuario=self.luis
        )

    def test_usuario_no_puede_ver_tarea_ajena(self):
        url_luis = f"/api/tareas-genericas/{self.tarea_luis.id}/"
        url_ana = f"/api/tareas-genericas/{self.tarea_ana.id}/"
        self.client.force_login(self.ana)

        respuesta1 = self.client.get(url_luis)
        self.assertEqual(respuesta1.status_code, status.HTTP_404_NOT_FOUND)

        respuesta2 = self.client.get(url_ana)
        self.assertEqual(respuesta2.status_code, status.HTTP_200_OK)
        self.assertEqual(respuesta2.json()["id"], self.tarea_ana.id)

    def test_usuario_no_puede_eliminar_tarea_ajena(self):
        url_luis = f"/api/tareas-genericas/{self.tarea_luis.id}/"
        self.client.force_login(self.ana)

        respuesta = self.client.delete(url_luis)

        self.assertEqual(respuesta.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Tarea.objects.filter(id=self.tarea_luis.id).exists())

    def test_usuario_no_puede_modificar_tarea_ajena(self):
        url_luis = f"/api/tareas-genericas/{self.tarea_luis.id}/"
        self.client.force_login(self.ana)

        respuesta = self.client.patch(
            url_luis,
            data={"titulo": "Modificada por Ana"},
            content_type="application/json"
        )

        self.assertEqual(respuesta.status_code, status.HTTP_404_NOT_FOUND)
        self.tarea_luis.refresh_from_db()
        self.assertEqual(self.tarea_luis.titulo, "Tarea de Luis")



        