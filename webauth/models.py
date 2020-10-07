'''webauth Models'''
from django.db import models

class User(models.Model):
    '''User Model'''
    username = models.CharField(max_length=100, unique=True, blank=False, null=False)
    email = models.EmailField(unique=True, blank=False, null=False)

    def save(self, *args, **kwargs):
        super().full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return str(self.username)

class Tool(models.Model):
    '''Tool Model'''
    short_name = models.CharField(max_length=100, unique=True, blank=False, null=False)
    long_name = models.CharField(max_length=100, unique=True, blank=False, null=False)

    def __str__(self):
        return str(self.short_name)

class UserAccess(models.Model):
    '''UserAccess model'''
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    tool_id = models.ForeignKey(Tool, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.user_id) + ':' + str(self.tool_id)

    class Meta:
        '''UserAccess model Meta information'''
        constraints = [
            models.UniqueConstraint(fields=['user_id', 'tool_id'], name='unique_access')
        ]
