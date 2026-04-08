import django_filters

from . import models
from .forms import ProspectsFilterSetForm


class ProspectsFilter(django_filters.FilterSet):
    industry = django_filters.AllValuesFilter(field_name="industry", label="Industry")
    called = django_filters.BooleanFilter(field_name="called", label="Called")
    conversation = django_filters.BooleanFilter(
        field_name="conversation", label="Conversation"
    )

    class Meta:
        model = models.Prospect
        fields = ["province", "industry"]
        form = ProspectsFilterSetForm
