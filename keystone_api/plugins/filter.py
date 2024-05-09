"""Extends the `django-filter` package with custom filter backends.

Filter backends define the default behavior when filtering database queries
for REST API calls based on URL parameters.
"""

from django.db.models import fields
from django_filters.rest_framework import DjangoFilterBackend


class BackendFilter(DjangoFilterBackend):
    """Custom filter backend for Django REST framework

    This filter backend automatically generates filters for Django model fields based on their types.
    """

    _default_filters = ['exact', 'in', 'isnull']
    _numeric_filters = _default_filters + ['exact', 'in', 'lt', 'lte', 'gt', 'gte']
    _text_filters = _default_filters + ['exact', 'iexact', 'contains', 'icontains', 'startswith', 'istartswith', 'endswith', 'iendswith']
    _date_filters = _default_filters + ['year', 'month', 'day', 'week', 'week_day']
    _time_filters = _default_filters + ['hour', 'minute', 'second']

    _field_filter_map = {
        fields.AutoField: _numeric_filters,
        fields.BigAutoField: _numeric_filters,
        fields.BigIntegerField: _numeric_filters,
        fields.BinaryField: _default_filters,
        fields.BooleanField: _default_filters,
        fields.CharField: _text_filters,
        fields.CommaSeparatedIntegerField: _default_filters,
        fields.DateField: _date_filters,
        fields.DateTimeField: _date_filters + _time_filters,
        fields.DecimalField: _numeric_filters,
        fields.DurationField: _default_filters,
        fields.EmailField: _text_filters,
        fields.FilePathField: _text_filters,
        fields.FloatField: _numeric_filters,
        fields.GenericIPAddressField: _default_filters,
        fields.IPAddressField: _default_filters,
        fields.IntegerField: _numeric_filters,
        fields.NullBooleanField: _default_filters,
        fields.PositiveBigIntegerField: _numeric_filters,
        fields.PositiveIntegerField: _numeric_filters,
        fields.PositiveSmallIntegerField: _numeric_filters,
        fields.SlugField: _text_filters,
        fields.SmallAutoField: _numeric_filters,
        fields.SmallIntegerField: _numeric_filters,
        fields.TextField: _text_filters,
        fields.TimeField: _time_filters,
        fields.URLField: _text_filters,
        fields.UUIDField: _default_filters
    }

    def get_filter_type(self, field: fields.Field) -> list[str]:
        """Get the appropriate filter types for a given field type

         Args:
             field: A Django model field

         Returns:
             List of filter types applicable to the given field
         """

        return self._field_filter_map.get(type(field), self._default_filters)

    def get_filterset_class(self, view, queryset=None):
        """Get the filterSet class for a given view

        Args:
            view: The view instance
            queryset: The queryset for the view

        Returns:
            A FilterSet class
        """

        # Default to user provided filterset class
        # Super method returns `None` if not defined
        if filterset_class := super().get_filterset_class(view, queryset=queryset):
            return filterset_class

        class AutoFilterSet(self.filterset_base):
            class Meta:
                model = queryset.model
                fields = {field.name: self.get_filter_type(field) for field in queryset.model._meta.get_fields()}

        return AutoFilterSet
