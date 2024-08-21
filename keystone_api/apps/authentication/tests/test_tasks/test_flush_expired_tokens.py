"""Unit tests for the `flush_expired_tokens` function."""

from datetime import timedelta

from django.test import TestCase
from django.utils.timezone import now
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken
from rest_framework_simplejwt.tokens import AccessToken

from apps.authentication.tasks import flush_expired_tokens


class FlushExpiredTokens(TestCase):
    """Test the flushing of expired access tokens."""

    def setUp(self) -> None:
        """Create mock token records in the database."""

        self.expired_token = OutstandingToken.objects.create(
            token=AccessToken(),
            jti='expired-token-jti',
            expires_at=now() - timedelta(days=1)
        )

        self.valid_token = OutstandingToken.objects.create(
            token=AccessToken(),
            jti='valid-token-jti',
            expires_at=now() + timedelta(days=1)
        )

    def test_expired_tokens_are_deleted(self) -> None:
        """Test expired tokens are deleted."""

        flush_expired_tokens()
        self.assertFalse(OutstandingToken.objects.filter(id=self.expired_token.id).exists())

    def test_valid_tokens_are_preserved(self) -> None:
        """Test unexpired tokens are not deleted."""

        flush_expired_tokens()
        self.assertFalse(OutstandingToken.objects.filter(id=self.expired_token.id).exists())
