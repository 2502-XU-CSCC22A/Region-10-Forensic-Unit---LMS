from django.db import models

ROLE_CHOICES = [
    ('admin', 'Admin'),
    ('viewer', 'Viewer'),
    ('editor', 'Editor'),
]

role = models.CharField(max_length=100, choices=ROLE_CHOICES)
class UserProfile(models.Model):
    user_id = models.BigAutoField(primary_key=True)
    full_name = models.CharField(max_length=255, null=True, blank=True)
    email = models.CharField(max_length=255, null=True, blank=True)
    phone_num = models.CharField(max_length=50, null=True, blank=True)
    role = models.CharField(max_length=100, choices=ROLE_CHOICES, null=True, blank=True)
    last_login = models.DateTimeField(null=True, blank=True)
    avatar = models.CharField(max_length=255, null=True, blank=True, unique=True)

    class Meta:
        db_table = 'user_profiles'  

    def __str__(self):
        return self.full_name or self.email or str(self.user_id)