import django_filters

from . import models


class ProspectsFilter(django_filters.FilterSet):
    called = django_filters.BooleanFilter(field_name="called", label="Called")
    conversation = django_filters.BooleanFilter(
        field_name="conversation", label="Conversation"
    )

    class Meta:
        model = models.Prospect
        fields = ["province"]
