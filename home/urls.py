from django.urls import path

from . import views

app_name = "home"

urlpatterns = [
    path("", views.home, name="home"),
    path("call-records/", views.call_records_list, name="call-records"),
    path("call-records/create", views.call_record_create, name="call-records-create"),
    path("prospects/", views.prospects_list, name="prospects-list"),
    path("prospects/create", views.prospects_create, name="prospects-create"),
    path(
        "prospects/import-excel",
        views.prospects_import_excel,
        name="prospects-import-excel",
    ),
    path(
        "prospects/<int:prospect_id>/add-call",
        views.prospects__call_record_create,
        name="prospects--call-record-create",
    ),
    # HTMX
    path("htmx/<str:action>", views.htmx_test, name="htmx"),
]
