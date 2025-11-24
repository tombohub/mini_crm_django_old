from django import forms
from django.core.exceptions import ValidationError

from . import services
from .models import ColdCallRecord, Prospect


class ImportXlsxForm(forms.ModelForm):
    """
    Form for uploading a excel file.
    """

    excel_file = forms.FileField()

    class Meta:
        model = Prospect
        fields = ["excel_file", "industry"]

    def clean_excel_file(self):
        excel_file = self.cleaned_data.get("excel_file")
        if not services.is_xlsx(excel_file):
            raise ValidationError("Must be an excel file")

        if not services.validate_yellow_pages_ca_excel_columns(excel_file=excel_file):
            raise ValidationError("Columns are not correct")

        return excel_file


class YellowPagesCaHtmlForm(forms.Form):
    """
    For for pasting yellow pages canada page to import
    prospects data
    """

    html = forms.CharField(widget=forms.Textarea)


class CallRecordForm(forms.ModelForm):
    """
    Create call record
    """

    class Meta:
        model = ColdCallRecord
        exclude = ["created_at", "updated_at"]
        widgets = {
            "date": forms.DateTimeInput(attrs={"type": "datetime"}),
            "outcome": forms.RadioSelect(attrs={"class": "btn-check"}),
        }


class ProspectsFilterForm(forms.ModelForm):
    class Meta:
        model = Prospect
        fields = ["province"]
