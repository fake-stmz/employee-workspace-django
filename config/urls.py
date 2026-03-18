from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from apps.tasks.views import TaskViewSet, ProjectViewSet
from apps.clients.views import ClientViewSet
from apps.employees.views import EmployeeViewSet

router = DefaultRouter()
router.register(r"tasks", TaskViewSet)
router.register(r"projects", ProjectViewSet)
router.register(r"clients", ClientViewSet)
router.register(r"employees", EmployeeViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
]
