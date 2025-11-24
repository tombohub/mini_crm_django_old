from django.contrib import admin
from django.utils.html import format_html

from .models import ColdCallRecord, Prospect


# Register your models here.
@admin.register(ColdCallRecord)
class ColdCallRecordAdmin(admin.ModelAdmin):
    list_display = [
        field.name
        for field in ColdCallRecord._meta.fields
        if field.name not in ["created_at", "updated_at"]
    ]


class ColdCallRecordInline(admin.StackedInline):
    model = ColdCallRecord
    extra = 0


@admin.register(Prospect)
class ProspectAdmin(admin.ModelAdmin):
    list_display = [
        "business_name",
        "city",
        "industry",
        "phone_number",
        "display_website_url",
        "has_been_called",
    ]
    search_fields = ["business_name"]
    inlines = [ColdCallRecordInline]

    def display_website_url(self, obj: Prospect):
        return format_html(
            "<a href='{url}' target='_blank'>{url}</a>", url=obj.website_url
        )
