"""Serializers for casting database models to/from JSON and XML representations.

Serializers handle the casting of database models to/from HTTP compatible
representations in a manner that is suitable for use by RESTful endpoints.
They encapsulate object serialization, data validation, and database object
creation.
"""

from rest_framework import serializers

from .models import *

__all__ = ['ResearchGroupSerializer', 'UsernameSerializer', 'UserSerializer']


class UserSerializer(serializers.ModelSerializer):
    """Object serializer for the `User` class"""

    class Meta:
        model = User
        exclude = ('password',)


class UsernameSerializer(serializers.ModelSerializer):
    """Limited object serializer for the `User` class which returns the username online"""

    class Meta:
        model = User
        fields = ('username',)


class ResearchGroupSerializer(serializers.ModelSerializer):
    """Object serializer for the `ResearchGroup` class"""

    class Meta:
        model = ResearchGroup
        fields = '__all__'
