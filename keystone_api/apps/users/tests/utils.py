"""Testing utilities specific to dealing with user accounts"""

from apps.users.models import User


def create_test_user(
    username: str,
    password: str = "foobar123",
    **kwargs
) -> User:
    """Create a user account for testing purposes

    Args:
        username: The account username
        password: The account password
        **kwargs: Any other values in the user model

    Return:
        The saved user account
    """

    kwargs.setdefault('first_name', "foo")
    kwargs.setdefault('last_name', "bar")
    kwargs.setdefault('email', "foo@bar.com")

    return User.objects.create_user(username, password, **kwargs)
