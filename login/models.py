import secrets
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta

TOKEN_EXPIRY_MINUTES = 15


class LoginToken(models.Model):
    """
    A one-time, short-lived token issued after successful credential
    verification.  The user must visit /login/verify/<token>/ before
    the token expires to complete the login.
    """
    user       = models.ForeignKey(User, on_delete=models.CASCADE, related_name='login_tokens')
    token      = models.CharField(max_length=64, unique=True, db_index=True)
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name        = 'Login Token'
        verbose_name_plural = 'Login Tokens'

    def __str__(self):
        return f"Token for {self.user.username} (expires {self.expires_at})"

    # ── Class Methods ─────────────────────────────────────────────────────────

    @classmethod
    def generate(cls, user):
        """Create and persist a fresh token for the given user."""
        # Clean up any previous tokens for this user first
        cls.objects.filter(user=user).delete()

        token    = secrets.token_urlsafe(32)
        instance = cls.objects.create(
            user=user,
            token=token,
            expires_at=timezone.now() + timedelta(minutes=TOKEN_EXPIRY_MINUTES),
        )
        return instance.token

    @classmethod
    def consume(cls, token_str):
        """
        Validate and delete a token in one step.
        Returns the associated User on success, or None on failure.
        """
        try:
            entry = cls.objects.select_related('user').get(token=token_str)
        except cls.DoesNotExist:
            return None

        user = entry.user
        entry.delete()   # one-time use — always delete regardless of expiry

        if timezone.now() > entry.expires_at:
            return None  # expired

        return user