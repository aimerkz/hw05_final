from django.db import models


class CreatedModel(models.Model):
    """Абстрактная модель. Добавляет дату создания."""
    pub_date = models.DateTimeField(
        'Дата добавления',
        auto_now_add=True
    )

    class Meta:
        abstract = True
