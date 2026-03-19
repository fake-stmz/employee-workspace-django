from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from rest_framework.routers import DefaultRouter

from apps.tasks.views import *
from apps.clients.views import *
from apps.employees.views import *
from apps.wiki.views import *
from apps.mail.views import *

router = DefaultRouter()
router.register(r"tasks", TaskViewSet)
router.register(r"projects", ProjectViewSet)
router.register(r"clients", ClientViewSet)
router.register(r"employees", EmployeeViewSet)

urlpatterns = [
    # Стандартная админ-панель Django
    path('admin/', admin.site.urls),
    # DRF API
    path('api/', include(router.urls)),
    # Авторизация
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    # Главная панель - W.I.P. (пока переводит на список задач)
    path('', dashboard, name='dashboard'),
    # Задачи
    path('tasks/', task_list, name='task_list'),
    path('tasks/create/', task_create, name='task_create'),
    path('tasks/<int:pk>/edit/', task_update, name='task_update'),
    path('tasks/<int:pk>/delete/', task_delete, name='task_delete'),
    # Сотрудники
    path('employees/', employee_list, name='employee_list'),
    # Клиенты
    path('clients/', client_list, name='client_list'),
    # Мини-вики
    path('wiki/', wiki_list, name='wiki_list'),
    path('wiki/<int:pk>/', wiki_page_view, name='wiki_page'),
    path('wiki/create/', wiki_create, name='wiki_create'),
    path('wiki/<int:pk>/edit/', wiki_update, name='wiki_update'),
    path('wiki/<int:pk>/delete/', wiki_delete, name='wiki_delete'),
    # Почта (временная заглушка)
    path('mail/', email_list, name='email_list'),
    path('mail/create/', email_create, name='email_create'),
]
