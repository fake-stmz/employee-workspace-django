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