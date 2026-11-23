import json
from datetime import date

from django.forms.models import model_to_dict
from django.http import HttpResponseNotAllowed, JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.csrf import csrf_protect, ensure_csrf_cookie

from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import generics
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny

from core.models import Tarea
from core.serializers import TareaModelSerializer

@ensure_csrf_cookie
@api_view(["GET"])
@permission_classes([AllowAny])
def csrf_token(request):
    return Response(
        {"message": "Comunicación CSRF establecida"},
        status=status.HTTP_200_OK
    )

@csrf_protect
def iniciar_sesion_no_drf(request):
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])

    try:
        datos = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse(
            {"error": "No se pudo leer el objeto JSON"},
            status=status.HTTP_400_BAD_REQUEST
        )

    if not isinstance(datos, dict):
        return JsonResponse(
            {"error": "Se esperaba un diccionario"},
            status=status.HTTP_400_BAD_REQUEST
        )

    username = datos.get("username")
    password = datos.get("password") 

    if not isinstance(username, str) or not isinstance(password, str):
        return JsonResponse(
            {"error": "El usuario/contraseña tiene que ser cadenas"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    if not username.strip() or not password:
        return JsonResponse(
            {"error": "El usuario/contraseña no pueden ser cadenas vacías"},
            status=status.HTTP_400_BAD_REQUEST
        )

    usuario = authenticate(
        request,
        username=username,
        password=password
    )

    if usuario is None:
        return JsonResponse(
            {"error": "Las credenciales son incorrectas"},
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    login(request, usuario)

    return JsonResponse(
        {"username": usuario.username},
        status=status.HTTP_200_OK
    )

@api_view(["POST"])
@permission_classes([AllowAny])
def iniciar_sesion(request):
    """
    Endpoint que autentica e inicia sesión. La sesión se mantiene
    activa mediante el uso de una cookie de sesión.
    endpoint: /api/login/
    """
    username = request.data.get("username")
    password = request.data.get("password")

    if not isinstance(username, str) or not isinstance(password, str):
        return Response(
            {"error": "Los campos tienen que ser cadenas de texto"},
            status=status.HTTP_400_BAD_REQUEST
        )

    if not username.strip() or not password:
        return Response(
            {"error": "El usuario o la contraseña están vacíos"},
            status=status.HTTP_400_BAD_REQUEST
        )

    usuario = authenticate(
        request,
        username=username,
        password=password
    )

    if usuario is None:
        return Response(
            {"error": "Las credenciales son incorrectas"},
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    login(request, usuario)

    return Response(
        {"username": usuario.username},
        status=status.HTTP_200_OK
    )

@csrf_protect
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def cerrar_sesion(request):
    """
    Endpoit para cerrar sesión: /api/logout/
    """
    logout(request)
    return Response(
        {"message": "La sesión ha sido cerrada"},
        status=status.HTTP_200_OK
    )

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def quien_soy(request):
    """
    Devuelve el usuario autenticado y su estado.
    """
    usuario = request.user

    return Response({
        "autenticado": usuario.is_authenticated,
        "usuario": usuario.username if usuario.is_authenticated else None
    })


#----- VISTAS GENÉRICAS DE REST FRAMEWORK ---
#--------------------------------------------

class DetalleTareaGenericaView(generics.RetrieveUpdateDestroyAPIView):
    """
    Vista genérica que implementa GET, PUT, PATCH y DELETE a una
    tarea específica, filtrada mediante el id.
    Se requiere ser un usuario autenticado para acceder a las tareas
    asociadas a ese usuario.
    endpoint: /api/tareas-genericas/id/
    """
    permission_classes = [IsAuthenticated]
    #queryset = Tarea.objects.all()
    serializer_class = TareaModelSerializer
    lookup_field = "id"

    def get_queryset(self):
        return Tarea.objects.filter(usuario=self.request.user) 

class ListaTareasGenericaView(generics.ListCreateAPIView):
    """
    Vista genérica que implementa GET para listar todas las tareas
    y POST para crear una nueva.
    Se requiere ser un usuario autenticado para acceder a las tareas
    asociadas a ese usuario.
    perform_create() asocia la tarea creada en POST con el usuario 
    que se autenticó previamente.
    endpoint: /api/tareas-genericas/
    """
    permission_classes = [IsAuthenticated]
    queryset = Tarea.objects.all()
    serializer_class = TareaModelSerializer

    def get_queryset(self):
        return Tarea.objects.filter(usuario=self.request.user)

    def perform_create(self, serializer):
        serializer.save(usuario=self.request.user)

#------- FUNCIONES API REST FRAMEWORK -------
#--------------------------------------------

# Vista de prueba de la API REST
@api_view(["GET"])
def estado_api(request):
    objeto = {
        "estado": "activo",
        "framework": "DRF"
    }

    return Response(objeto)

@api_view(["GET", "POST"])
def listar_tareas_drf(request):
    """
    Vista diseñana para listar todas las tareas mediante GET y
    crear una nueva tarea mediate POST.
    endpoint: /api/tareas-drf/
    """

    # GET para listar todas las tareas
    if request.method == "GET":
        tareas = Tarea.objects.all()
        serializer = TareaModelSerializer(tareas, many=True)

        return Response(serializer.data)

    # POST para crear una tarea nueva
    if request.method == "POST":

        serializer = TareaModelSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(["GET", "PATCH", "PUT", "DELETE"])
def detalle_tarea_drf(request, id):
    """
    Vista diseñada puede ver, modificar, reemplazar y
    eliminar una tarea específica mediante los métodos:
    GET, PATCH, PUT Y DELETE.
    endpoint: /api/tareas-drf/id/
    """

    tarea = get_object_or_404(Tarea, id=id)
    
    # GET para listar la tarea
    if request.method == "GET":
        serializer = TareaModelSerializer(tarea)

        return Response(serializer.data, status=status.HTTP_200_OK)

    # PATCH para modificar valores de la tarea
    if request.method == "PATCH":
        serializer = TareaModelSerializer(tarea, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # PUT para reempalzar valores de la tarea
    if request.method == "PUT":
        serializer = TareaModelSerializer(tarea, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # DELETE para eliminar la tarea
    if request.method == "DELETE":
        tarea.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


#-------- FUNCIONES API (NO REST) -----------
#--------------------------------------------

def listar_tareas(request):
    """
    Gestiona la colección de tareas mediante HTTP.

    GET: devuelve todas las tareas.
    POST: valida los datos recibidos y crea una tarea.

    Las tareas nuevas comienzan con completada=False.
    """

    # Consultar todas las tareas existentes
    if request.method == "GET":
        tareas = list(Tarea.objects.values())
        return JsonResponse(tareas, safe=False, status=200)

    # Crear una nueva tarea
    if request.method == "POST":

        # Decodificamos el JSON y verificamos su estructura
        try:
            tarea_nueva = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"error": "JSON inválido"}, status=400)

        if not isinstance(tarea_nueva, dict):
            return JsonResponse({"error": "No es un diccionario"}, status=400)

        if not tarea_nueva:
            return JsonResponse({"error": "El diccionario está vacío"}, status=400)

        if "titulo" not in tarea_nueva:
            return JsonResponse({"error" : "Clave título inexistente"}, status=400)

        titulo = tarea_nueva["titulo"]

        if not isinstance(titulo, str):
            return JsonResponse({"error": "El campo título tiene que ser un dato tipo str"}, status=400)

        # Normalizamos el título antes de comprobar que no esté vacío
        titulo = titulo.strip()

        if not titulo:
            return JsonResponse({"error": "El título no puede ser una cadena vacía"}, status=400)

        if len(titulo) > 100:
            return JsonResponse({"error": "El título no puede contener más de 100 caracteres"}, status=400)

        if "descripcion" not in tarea_nueva:
            descripcion = ""
        else:
            descripcion = tarea_nueva["descripcion"]

        if not isinstance(descripcion, str):
            return JsonResponse({"error": "La descripción debe ser un dato tipo str"}, status=400)

        if "fecha_limite" not in tarea_nueva:
            fecha_limite = None
        else:
            fecha_limite = tarea_nueva["fecha_limite"]

        # Si se proporciona una fecha límite, validamos que esté correctamente dada
        if fecha_limite is not None:

            if not isinstance(fecha_limite, str):
                return JsonResponse({"error": "La fecha límite tiene que tener el tipo de dato str"}, status=400)

            try:
                fecha_limite = date.fromisoformat(fecha_limite)
            except ValueError:
                return JsonResponse({"error": "La fecha límite tiene que tener el formato YYYY-MM-DD"}, status=400)

        tarea_nueva_db = Tarea.objects.create(
            titulo=titulo,
            descripcion=descripcion,
            fecha_limite=fecha_limite,
            completada=False
        )

        tarea_nueva_mandar = model_to_dict(tarea_nueva_db)
        tarea_nueva_mandar["id"] = tarea_nueva_db.id

        return JsonResponse(tarea_nueva_mandar, status=201)   

    return HttpResponseNotAllowed(["GET", "POST"])

def detalle_tarea(request, id):
    """
    Consulta una tarea específica mediante su identificador.

    GET: devuelve los datos de la tarea solicitada.

    PATCH: modifica parcialmente una tarea

    PUT: modifica totalmente una tarea

    DELETE: elimina una tarea
    """

    if request.method not in ["GET", "PATCH", "PUT", "DELETE"]:
        return HttpResponseNotAllowed(["GET", "PATCH", "PUT", "DELETE"])

    tarea = Tarea.objects.filter(id=id).first()

    if tarea is None:
        return JsonResponse({"error": "La tarea no existe"}, status=404)

    if request.method == "GET":
        tarea_mandar = model_to_dict(tarea)
        tarea_mandar["id"] = tarea.id

        return JsonResponse(tarea_mandar, status=200)

    if request.method == "PATCH":

        try:
            datos_recibidos = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"error": "JSON inválido"}, status=400)

        if not isinstance(datos_recibidos, dict):
            return JsonResponse({"error": "El contenido debe ser un diccionario"}, status=400)

        # Validar campo título
        if "titulo" in datos_recibidos:
            titulo = datos_recibidos["titulo"]

            if not isinstance(titulo, str):
                return JsonResponse({"error": "El campo 'titulo' tiene que ser del tipo str"}, status=400)

            titulo = titulo.strip()

            if not titulo:
                return JsonResponse({"error": "El campo 'titulo' no puede estar vacío"}, status=400)

            if len(titulo) > 100:
                return JsonResponse({"error": "El título no puede ser mayor a 100 caracteres"}, status=400)

            tarea.titulo = titulo

        # Validar campo descripcion
        if "descripcion" in datos_recibidos:
            descripcion = datos_recibidos["descripcion"]
            
            if not isinstance(descripcion, str):
                return JsonResponse({"error": "El campo 'descripción' tiene que ser del tipo str"}, status=400)

            tarea.descripcion = descripcion

        # Validar fecha límite
        if "fecha_limite" in datos_recibidos:
            fecha_limite = datos_recibidos["fecha_limite"]
            if fecha_limite is not None and not isinstance(fecha_limite, str):
                return JsonResponse({"error": "El campo 'fecha límite' tiene que ser del tipo null o str"}, status=400)

            if fecha_limite is None:
                tarea.fecha_limite = None
            else:
                if not fecha_limite:
                    return JsonResponse({"error": "No se ha especificado la fecha límite"}, status=400)

                try:
                    fecha_limite = date.fromisoformat(fecha_limite)
                    tarea.fecha_limite = fecha_limite
                except ValueError:
                    return JsonResponse({"error": "El formato de la fecha límite es incorrecto"}, status=400)

        # Validar campo completada
        if "completada" in datos_recibidos:

            if not isinstance(datos_recibidos["completada"], bool):
                return JsonResponse({"error": "El campo 'completada' tiene que ser del tipo bool"}, status=400)

            tarea.completada = datos_recibidos["completada"]

        tarea.save()
        tarea_mandar = model_to_dict(tarea)
        tarea_mandar["id"] = tarea.id

        return JsonResponse(tarea_mandar, status=200)

    if request.method == "PUT":
        try:
            datos_recibidos = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"error": "JSON inválido"}, status=400)

        if not isinstance(datos_recibidos, dict):
            return JsonResponse({"error": "Los datos recibidos tienen que ser un diccionario"}, status=400)

        # Validar título
        if "titulo" not in datos_recibidos:
            return JsonResponse({"error": "El campo título es necesario"}, status=400)

        titulo = datos_recibidos["titulo"]

        if not isinstance(titulo, str):
            return JsonResponse({"error": "El campo título tiene que ser del tipo str"}, status=400)

        titulo = titulo.strip()

        if not titulo:
            return JsonResponse({"error": "El campo título no puede ser una cadena vacía"}, status=400)

        if len(titulo) > 100:
            return JsonResponse({"error": "El título no puede contener más de 100 caracteres"}, status=400)

        tarea.titulo = titulo

        # Validar descripción
        descripcion = datos_recibidos.get("descripcion", "")

        if not isinstance(descripcion, str):
            return JsonResponse({"error": "El campo descripción tiene que ser del tipo str"}, status=400)

        tarea.descripcion = descripcion

        #Validar fecha límite
        fecha_limite = datos_recibidos.get("fecha_limite", None)

        if fecha_limite is not None:

            if not isinstance(fecha_limite, str):
                return JsonResponse({"error": "La fecha límite tiene que ser del tipo str o null"}, status=400)

            try:
                fecha_limite = date.fromisoformat(fecha_limite)
            except ValueError:
                return JsonResponse({"error": "El formato de la fecha límite es incorrecto"}, status=400)

        tarea.fecha_limite = fecha_limite

        # Validar completada
        completada = datos_recibidos.get("completada", False)

        if not isinstance(completada, bool):
            return JsonResponse({"error": "El campo completada debe ser del tipo bool"}, status=400)

        tarea.completada = completada

        tarea.save()
        tarea_mandar = model_to_dict(tarea)
        tarea_mandar["id"] = tarea.id

        return JsonResponse(tarea_mandar, status=200)

    if request.method == "DELETE":
        tarea.delete()
        return HttpResponse(status=204)