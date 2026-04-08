import django_filters

from . import models
from .forms import ProspectsFilterSetForm


def _coerce_bool(value: str) -> bool:
    return value.lower() in {"1", "true", "t", "yes", "y", "on"}


class ProspectsFilter(django_filters.FilterSet):
    industry = django_filters.AllValuesFilter(field_name="industry", label="Industry")
    called = django_filters.TypedChoiceFilter(
        field_name="called",
        label="Called",
        choices=(("", "All"), ("true", "Yes"), ("false", "No")),
        coerce=_coerce_bool,
    )
    conversation = django_filters.TypedChoiceFilter(
        field_name="conversation",
        label="Conversation",
        choices=(("", "All"), ("true", "Yes"), ("false", "No")),
        coerce=_coerce_bool,
    )

    class Meta:
        model = models.Prospect
        fields = ["industry"]
        form = ProspectsFilterSetForm
