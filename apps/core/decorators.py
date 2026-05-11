from django.shortcuts import redirect
from django.contrib import messages
from functools import wraps


def handle_exceptions(view_func):
    """Декоратор для безопасной обработки исключений в views"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        
        return view_func(request, *args, **kwargs)
        """
        try:
            return view_func(request, *args, **kwargs)
        except Exception as e:
            error_message = str(e)
            if "does not exist" in error_message.lower():
                messages.error(request, "Запись не найдена.")
            elif "permission" in error_message.lower():
                messages.error(request, "У вас недостаточно прав для выполнения этого действия.")
            else:
                messages.error(request, f"Произошла ошибка: {error_message[:150]}")
            
            return redirect('dashboard')
        """
    return wrapper