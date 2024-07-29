from django.db import models
from user.models import User

class Expense(models.Model):
    description = models.CharField(max_length=255)
    amount = models.FloatField()
    currency = models.CharField(max_length=10)
    date = models.DateField()
    payer = models.ForeignKey(User, related_name='expenses_paid', on_delete=models.CASCADE)
    payment_type = models.CharField(max_length=10, choices=[('equal', 'Equal'), ('exact', 'Exact'), ('percentage', 'Percentage')])

    def __str__(self):
        return self.description

class Participant(models.Model):
    expense = models.ForeignKey(Expense, related_name='participants', on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name='expenses_participated', on_delete=models.CASCADE)
    amount = models.FloatField()

    def __str__(self):
        return f"{self.user.username} - {self.amount}"
