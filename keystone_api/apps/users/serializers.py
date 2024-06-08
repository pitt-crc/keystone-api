"""Serializers for casting database models to/from JSON and XML representations.

Serializers handle the casting of database models to/from HTTP compatible
representations in a manner that is suitable for use by RESTful endpoints.
They encapsulate object serialization, data validation, and database object
creation.
"""

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


class PrivilegeUserSerializer(serializers.ModelSerializer):
    """Object serializer for the `User` class"""

    password = serializers.CharField(write_only=True)

    class Meta:
        """Serializer settings"""

        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'is_staff', 'is_active', 'is_ldap_user', 'password']

    def create(self, validated_data: dict) -> User:
        """Create a new user

        Args:
            validated_data: Validated user data

        Returns:
            A new user instance
        """

        # User `create_user` instead of `create` to ensure passwords are salted/hashed properly
        return User.objects.create_user(**validated_data)


class RestrictedUserSerializer(serializers.ModelSerializer):
    """Object serializer for the `User` class"""

    class Meta:
        """Serializer settings"""

        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'is_staff', 'is_active', 'is_ldap_user']
        read_only_fields = ['is_staff', 'is_active', 'is_ldap_user']
