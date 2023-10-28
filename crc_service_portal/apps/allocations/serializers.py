from rest_framework import serializers

from .models import *


class ClusterSerializer(serializers.ModelSerializer):
    """Object JSON serializer for the `Cluster` class"""

    class Meta:
        model = Cluster
        fields = '__all__'


class AllocationSerializer(serializers.ModelSerializer):
    """Object JSON serializer for the `Allocation` class"""

    class Meta:
        model = Allocation
        fields = '__all__'


class PublicationSerializer(serializers.ModelSerializer):
    """Object JSON serializer for the `Publication` class"""

    class Meta:
        model = Publication
        fields = '__all__'


class ProposalSerializer(serializers.ModelSerializer):
    """Object JSON serializer for the `Proposal` class"""

    class Meta:
        model = Proposal
        fields = '__all__'
