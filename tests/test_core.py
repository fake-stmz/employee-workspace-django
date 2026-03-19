from django.test import TestCase, Client
from django.contrib.auth.models import User, Group
from django.urls import reverse

from apps.tasks.models import Task
from apps.wiki.models import WikiPage
from apps.mail.models import EmailMessage
from apps.employees.models import Employee


class CoreTests(TestCase):

    def setUp(self):
        self.client = Client()

        # группы
        self.manager_group = Group.objects.create(name="Manager")
        self.employee_group = Group.objects.create(name="Employee")

        # пользователь
        self.user = User.objects.create_user(
            username="testuser",
            password="12345"
        )
        self.user.groups.add(self.employee_group)

        self.employee = Employee.objects.create(
            user=self.user,
            position="Manager"
        )
    
    def test_create_task(self):
        self.client.login(username="testuser", password="12345")

        response = self.client.post(reverse("task_create"), {
            "title": "Test Task",
            "status": "new",
            "assigned_to": self.employee.id
        })

        self.assertEqual(response.status_code, 302)
        self.assertEqual(Task.objects.count(), 1)
    
    def test_task_visibility(self):
        Task.objects.create(
            title="User Task",
            status="new",
            assigned_to=self.employee
        )

        self.client.login(username="testuser", password="12345")

        response = self.client.get(reverse("task_list"))

        self.assertContains(response, "User Task")
