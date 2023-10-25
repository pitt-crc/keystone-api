from rest_framework import serializers

from . import models


class AllocationSerializer(serializers.ModelSerializer):
    """Object JSON serializer for the `` class"""

    class Meta:
        model = models.Allocation
        fields = '__all__'


class ProjectProposalSerializer(serializers.ModelSerializer):
    """Object JSON serializer for the `ProjectProposal` class"""

    class Meta:
        model = models.ProjectProposal
        fields = '__all__'


class PublicationSerializer(serializers.ModelSerializer):
    """Object JSON serializer for the `Publication` class"""

    class Meta:
        model = models.Publication
        fields = '__all__'
