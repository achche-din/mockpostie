from django.db import models

class Link(models.Model):
    customUrl = models.CharField(max_length=200)
    response = models.TextField()
    user_id = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.customUrl
