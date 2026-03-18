from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from rest_framework.routers import DefaultRouter

from apps.tasks.views import TaskViewSet, ProjectViewSet, task_list
from apps.clients.views import ClientViewSet
from apps.employees.views import EmployeeViewSet, dashboard

router = DefaultRouter()
router.register(r"tasks", TaskViewSet)
router.register(r"projects", ProjectViewSet)
router.register(r"clients", ClientViewSet)
router.register(r"employees", EmployeeViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('', dashboard, name='dashboard'),
    path('tasks/', task_list, name='task_list'),
]
