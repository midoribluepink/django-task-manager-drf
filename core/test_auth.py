from django.test import TestCase, Client
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

    def test_inicio_sesion(self):
        url = "/api/login/"

        respuesta = self.client.post(
            url,
            data={
                "username": self.ana.username,
                "password": "ClaveAna123!"
            },
            content_type="application/json"
        )

        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
        self.assertEqual(respuesta.json()["username"], "ana")

        respuesta2 = self.client.get("/api/quien-soy/")

        self.assertEqual(respuesta2.status_code, status.HTTP_200_OK)
        self.assertEqual(respuesta2.json()["usuario"], "ana")

    def test_cierre_sesion(self):
        url_login = "/api/login/"
        url_logout = "/api/logout/"
        url_quien_soy = "/api/quien-soy/"

        respuesta_login = self.client.post(
            url_login,
            data={
                "username": self.ana.username,
                "password": "ClaveAna123!"
            },
            content_type="application/json"
        )

        self.assertEqual(respuesta_login.status_code, status.HTTP_200_OK)

        respuesta_quien_soy = self.client.get("/api/quien-soy/")

        self.assertEqual(respuesta_quien_soy.status_code, status.HTTP_200_OK)
        self.assertEqual("ana", respuesta_quien_soy.json()["usuario"])

        respuesta_logout = self.client.post(url_logout)

        self.assertEqual(respuesta_logout.status_code, status.HTTP_200_OK)

        respuesta_despues_logout = self.client.get(url_quien_soy)
        self.assertEqual(respuesta_despues_logout.status_code, status.HTTP_403_FORBIDDEN)

    def test_obtener_cookie_csrf(self):
        respuesta = self.client.get("/api/csrf/")

        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
        self.assertIn("csrftoken", respuesta.cookies)
        self.assertTrue(respuesta.cookies["csrftoken"].value)

    def test_login_sin_csrf(self):
        cliente = Client(enforce_csrf_checks=True)

        respuesta = cliente.post(
            "/api/login/",
            data={
                "username": self.ana.username,
                "password": "ClaveAna123!"
            },
            content_type="application/json"
        )

        self.assertEqual(respuesta.status_code, status.HTTP_403_FORBIDDEN)

    def test_login_con_csrf(self):
        cliente = Client(enforce_csrf_checks=True)

        respuesta_csrf = cliente.get("/api/csrf/")

        self.assertEqual(respuesta_csrf.status_code, status.HTTP_200_OK)

        token = cliente.cookies["csrftoken"].value 

        respuesta_login = cliente.post(
            "/api/login/",
            data={
                "username": "ana",
                "password": "ClaveAna123!"
            },
            content_type="application/json",
            headers={"X-CSRFToken": token}
        )

        self.assertEqual(respuesta_login.status_code, status.HTTP_200_OK)

        respuesta_quien_soy = cliente.get("/api/quien-soy/")

        self.assertEqual(respuesta_quien_soy.status_code, status.HTTP_200_OK)
        self.assertEqual("ana", respuesta_quien_soy.json()["usuario"])

    def test_login_con_csrf_invalido(self):
        cliente = Client(enforce_csrf_checks=True)

        respuesta_csrf = cliente.get("/api/csrf/")

        self.assertEqual(respuesta_csrf.status_code, status.HTTP_200_OK)

        respuesta_login = cliente.post(
            "/api/login/",
            data={
                "username": "ana",
                "password": "ClaveAna123!"
            },
            content_type="application/json",
            headers={"X-CSRFToken": "tokeninvalido"}
        )

        self.assertEqual(respuesta_login.status_code, status.HTTP_403_FORBIDDEN)
