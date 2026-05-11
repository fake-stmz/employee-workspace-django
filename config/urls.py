from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from rest_framework.routers import DefaultRouter
from django.conf import settings
from django.conf.urls.static import static

from apps.tasks.views import *
from apps.clients.views import *
from apps.employees.views import *
from apps.wiki.views import *
from apps.mail.views import *
from apps.core.views import *

router = DefaultRouter()
router.register(r"tasks", TaskViewSet)
router.register(r"projects", ProjectViewSet)
router.register(r"clients", ClientViewSet)
router.register(r"employees", EmployeeViewSet)
router.register(r"wiki", WikiViewSet)

urlpatterns = [
    # Стандартная админ-панель Django
    path('admin/', admin.site.urls),
    # DRF API
    path('api/', include(router.urls)),
    # Авторизация
    path('login/', auth_views.LoginView.as_view(
        template_name='login.html',
        redirect_authenticated_user=True,
    ), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    # Главная панель
    path('', dashboard, name='dashboard'),
    # Проекты
    path('projects/', project_list, name='project_list'),
    path('projects/create/', project_create, name='project_create'),
    path('projects/<int:pk>/', project_detail, name='project_detail'),
    path('projects/<int:pk>/edit/', project_update, name='project_update'),
    path('projects/<int:pk>/delete/', project_delete, name='project_delete'),
    # Задачи
    path('tasks/', task_list, name='task_list'),
    path('tasks/kanban/', task_kanban, name='task_kanban'),
    path('tasks/<int:pk>/', task_detail, name='task_detail'),
    path('tasks/create/', task_create, name='task_create'),
    path('tasks/<int:pk>/edit/', task_update, name='task_update'),
    path('tasks/<int:pk>/delete/', task_delete, name='task_delete'),
    path('tasks/<int:pk>/comment/', add_task_comment, name='add_task_comment'),
    path('tasks/<int:pk>/update-status/', task_update_status, name='task_update_status'),
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
    # Удаленные записи
    path('deleted/', deleted_items, name='deleted_items'),
    # Восстановление записи
    path('restore/<str:model_name>/<int:pk>/', restore_item, name='restore_item'),
    # Полное удаление
    path('permanent-delete/<str:model_name>/<int:pk>/', permanent_delete, name='permanent_delete'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
