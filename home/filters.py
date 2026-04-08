import django_filters

from . import models
from .forms import ProspectsFilterSetForm


class ProspectsFilter(django_filters.FilterSet):
    industry = django_filters.AllValuesFilter(
        field_name="industry", label="Industry", empty_label="All"
    )
    called = django_filters.BooleanFilter(
        field_name="called", label="Called", empty_label="All"
    )
    conversation = django_filters.BooleanFilter(
        field_name="conversation", label="Conversation", empty_label="All"
    )

    class Meta:
        model = models.Prospect
        fields = ["industry"]
        form = ProspectsFilterSetForm
