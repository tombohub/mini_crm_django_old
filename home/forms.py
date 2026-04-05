import json

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


class ProspectJsonCreateForm(forms.Form):
    """
    Create a prospect from a JSON payload.
    """

    prospect_json = forms.CharField(
        label="Prospect JSON",
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "rows": 8,
                "spellcheck": "false",
                "placeholder": '{\n  "business_name": "Acme Inc",\n  "industry": "Electrician",\n  "phone_number": "416-555-0100"\n}',
            }
        ),
    )

    def clean(self):
        cleaned_data = super().clean()
        raw_json = cleaned_data.get("prospect_json")
        if not raw_json:
            return cleaned_data

        try:
            payload = json.loads(raw_json)
        except json.JSONDecodeError as exc:
            self.add_error("prospect_json", f"Invalid JSON: {exc.msg}")
            return cleaned_data

        if not isinstance(payload, dict):
            self.add_error("prospect_json", "JSON payload must be an object.")
            return cleaned_data

        managed_fields = {"id", "created_at", "updated_at"}
        present_managed_fields = sorted(managed_fields.intersection(payload))
        if present_managed_fields:
            self.add_error(
                "prospect_json",
                "These fields are managed automatically: "
                + ", ".join(present_managed_fields),
            )

        allowed_fields = {
            field.name
            for field in Prospect._meta.fields
            if field.editable and not field.auto_created
        }
        unknown_fields = sorted(set(payload) - allowed_fields)
        if unknown_fields:
            self.add_error(
                "prospect_json",
                "Unknown fields: " + ", ".join(unknown_fields),
            )

        if self.errors:
            return cleaned_data

        prospect = Prospect(**payload)
        try:
            prospect.full_clean()
        except ValidationError as exc:
            if hasattr(exc, "message_dict"):
                for field_name, errors in exc.message_dict.items():
                    for error in errors:
                        self.add_error(
                            None,
                            f"{field_name.replace('_', ' ').capitalize()}: {error}",
                        )
            else:
                for error in exc.messages:
                    self.add_error(None, error)
            return cleaned_data

        self.cleaned_data["prospect_instance"] = prospect
        return cleaned_data

    def save(self) -> Prospect:
        prospect = self.cleaned_data["prospect_instance"]
        prospect.save()
        return prospect
