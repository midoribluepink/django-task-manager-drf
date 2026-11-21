"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from core.views import listar_tareas, detalle_tarea, estado_api, listar_tareas_drf, detalle_tarea_drf
from core.views import ListaTareasGenericaView, DetalleTareaGenericaView
from core.views import quien_soy

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/tareas/', listar_tareas),
    path('api/tareas/<int:id>/', detalle_tarea),
    path('api/estado/', estado_api),
    path('api/tareas-drf/', listar_tareas_drf),
    path('api/tareas-drf/<int:id>/', detalle_tarea_drf),
    path('api/tareas-genericas/', ListaTareasGenericaView.as_view()),
    path('api/tareas-genericas/<int:id>/', DetalleTareaGenericaView.as_view()),
    path('api/quien-soy/', quien_soy),
    path('api-auth/', include("rest_framework.urls"))
]
