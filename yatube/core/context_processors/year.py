from datetime import datetime


def year(request):
    time = datetime.now().year
    """Добавляет переменную с текущим годом."""
    return {
        'year': time,
    }
