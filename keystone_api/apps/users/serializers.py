"""Serializers for casting database models to/from JSON and XML representations.

Serializers handle the casting of database models to/from HTTP compatible
representations in a manner that is suitable for use by RESTful endpoints.
They encapsulate object serialization, data validation, and database object
creation.
"""

from django.contrib.auth import password_validation
from rest_framework import serializers

from .models import *

__all__ = [
    'PrivilegeUserSerializer',
    'ResearchGroupSerializer',
    'RestrictedUserSerializer'
]


class ResearchGroupSerializer(serializers.ModelSerializer):
    """Object serializer for the `ResearchGroup` class"""

    class Meta:
        """Serializer settings"""

        model = ResearchGroup
        fields = '__all__'


class RestrictedUserSerializer(serializers.ModelSerializer):
    """Object serializer for the `User` class with administrative fields marked as read only"""

    class Meta:
        """Serializer settings"""

        model = User
        fields = '__all__'
        read_only_fields = ['is_active', 'is_staff', 'is_ldap_user', 'date_joined', 'last_login']
        extra_kwargs = {'password': {'write_only': True}}

    def validate(self, attrs: dict) -> None:
        """Validate user attributes match the ORM data model

        Args:
            attrs: Dictionary of user attributes
        """

        if 'password' in attrs:
            password_validation.validate_password(attrs['password'])

        return super().validate(attrs)

    def create(self, validated_data: dict) -> None:
        """Raises an error when attempting to create a new record

        Raises:
            RuntimeError: Every time the function is called
        """

        raise RuntimeError('Attempted to create new user record using a serializer with restricted permissions.')

    def update(self, instance: User, validated_data: dict) -> User:
        """Update a given database record with the given data

        Args:
            instance: A `User` record reflecting current database values
            validated_data: The new values to set on the instance

        Returns:
            An instance reflecting the new database state
        """

        # Use the `set_password` method to ensure proper salting/hashing
        if 'password' in validated_data:
            password = validated_data.pop('password')
            password_validation.validate_password(password)
            instance.set_password(password)

        return super().update(instance, validated_data)


class PrivilegeUserSerializer(RestrictedUserSerializer):
    """Object serializer for the `User` class"""

    class Meta:
        """Serializer settings"""

        model = User
        fields = '__all__'
        read_only_fields = ['date_joined', 'last_login']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data: dict) -> User:
        """Create a new user

        Args:
            validated_data: Validated user data

        Returns:
            A new user instance
        """

        # Use `create_user` instead of `create` to ensure passwords are salted/hashed properly
        return User.objects.create_user(**validated_data)
