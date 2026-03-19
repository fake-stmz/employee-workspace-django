from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import EmailMessage
from .forms import EmailMessageForm
from apps.employees.models import Employee
from django.utils import timezone


@login_required
def email_list(request):

    if request.user.groups.filter(name='Manager').exists():
        emails = EmailMessage.objects.all().order_by("-sent_at")
    else:
        emails = EmailMessage.objects.filter(
            employee__user=request.user
        ).order_by("-sent_at")

    context = {
        "emails": emails
    }

    return render(request, "mail/email_list.html", context)


@login_required
def email_create(request):

    if request.method == "POST":
        form = EmailMessageForm(request.POST)
        if form.is_valid():
            email = form.save(commit=False)

            # заглушка вместо реальной отправки
            email.sender_email = request.user.email
            email.employee = request.user.employee
            email.sent_at = timezone.now()

            email.save()

            return redirect("email_list")
    else:
        form = EmailMessageForm()

    context = {
        "form": form
    }

    return render(request, "mail/email_form.html", context)
