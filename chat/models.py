from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    pass

#its Z-Group
class Group(models.Model):
    z_name = models.CharField(max_length=255)
    z_id = models.CharField(max_length=255, unique=True)
    creator = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.z_id
    
#Message
class Messages(models.Model):
    z_group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name="group")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField(default="")
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']
        verbose_name_plural = "Messages"

    def __str__(self):
        return self.z_group.z_id + '__' + self.user.username