"""Unit tests for the `Preference` class."""

from django.contrib.auth import get_user_model
from django.test import TestCase

from apps.notifications.models import default_alloc_thresholds, default_expiry_thresholds, Preference

User = get_user_model()


class PreferenceModelTest(TestCase):
    """Tests for getting user preferences."""

    def setUp(self) -> None:
        """Create a test user."""

        self.user = User.objects.create_user(username='testuser', password='foobar123!')

    def test_get_user_preference_creates_new_preference(self) -> None:
        """Test a new Preference object is created if one does not exist."""

        # Test a record is created
        self.assertFalse(Preference.objects.filter(user=self.user).exists())
        preference = Preference.get_user_preference(user=self.user)
        self.assertTrue(Preference.objects.filter(user=self.user).exists())

        # Ensure preference is created with appropriate defaults
        self.assertEqual(self.user, preference.user)
        self.assertListEqual(default_alloc_thresholds(), preference.alloc_thresholds)
        self.assertListEqual(default_expiry_thresholds(), preference.expiry_thresholds)

    def test_get_user_preference_returns_existing_preference(self) -> None:
        """Test an existing Preference object is returned if it already exists."""

        existing_preference = Preference.objects.create(user=self.user)
        preference = Preference.get_user_preference(user=self.user)
        self.assertEqual(existing_preference, preference)


class PreferenceSetTest(TestCase):
    """Tests for setting user preferences."""

    def setUp(self) -> None:
        """Create a test user."""

        self.user = User.objects.create_user(username='testuser', password='foobar123!')

    def test_set_user_preference_creates_preference(self) -> None:
        """Test that a new Preference object is created with specified values."""

        self.assertFalse(Preference.objects.filter(user=self.user).exists())

        Preference.set_user_preference(user=self.user, notify_status_update=False)
        preference = Preference.objects.get(user=self.user)
        self.assertFalse(preference.notify_status_update)

    def test_set_user_preference_updates_existing_preference(self) -> None:
        """Test that an existing Preference object is updated with specified values."""

        preference = Preference.objects.create(user=self.user, notify_status_update=True)
        self.assertTrue(Preference.objects.filter(user=self.user).exists())

        Preference.set_user_preference(user=self.user, notify_status_update=False)
        preference.refresh_from_db()
        self.assertFalse(preference.notify_status_update)
