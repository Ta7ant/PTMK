from django.db import models
from datetime import date


class Employee(models.Model):
    GENDER_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female'),
    ]

    full_name = models.CharField(max_length=200)
    birth_date = models.DateField()
    gender = models.CharField(max_length=6, choices=GENDER_CHOICES)

    class Meta:
        db_table = 'employees'
        indexes = [
            models.Index(fields=['gender', 'full_name']),
            models.Index(fields=['full_name', 'birth_date']),
        ]

    def calculate_age(self):
        today = date.today()
        return today.year - self.birth_date.year - (
                (today.month, today.day) < (self.birth_date.month, self.birth_date.day)
        )

    def save_to_db(self):
        self.save()

    def __str__(self):
        return f"{self.full_name} ({self.birth_date})"