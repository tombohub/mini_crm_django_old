from django.contrib import admin
from django.db.models import Exists, OuterRef
from django.db.models.query import QuerySet
from django.http import HttpRequest
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
        "called_status",
    ]
    search_fields = ["business_name"]
    inlines = [ColdCallRecordInline]

    def get_queryset(self, request: HttpRequest) -> QuerySet:
        queryset = super().get_queryset(request)
        return queryset.annotate(
            has_been_called_db=Exists(
                ColdCallRecord.objects.filter(prospect_id=OuterRef("pk"))
            )
        )

    @admin.display(
        boolean=True, description="Has been called", ordering="has_been_called_db"
    )
    def called_status(self, obj):
        return obj.has_been_called_db

    def display_website_url(self, obj: Prospect):
        return format_html(
            "<a href='{url}' target='_blank'>{url}</a>", url=obj.website_url
        )
