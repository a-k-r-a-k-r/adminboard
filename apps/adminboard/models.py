from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class TodoList(models.Model):
    text = models.CharField(max_length=200)
    completed = models.BooleanField(default=False)
    priority = models.IntegerField()
    details = models.TextField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.text

    class Meta:
        ordering = ['priority']