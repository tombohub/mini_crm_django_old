import datetime
import datetime as dt

from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Exists, OuterRef
from django.http import HttpResponseBadRequest
from django.shortcuts import get_object_or_404, redirect, render

from . import filters, services
from .forms import CallRecordForm, ImportXlsxForm
from .models import ColdCallRecord, Prospect


def home(request):
    return render(request, "home/home.html")


def prospects_list(request):
    prospects = Prospect.objects.prefetch_related("coldcallrecord_set").annotate(
        called=Exists(ColdCallRecord.objects.filter(prospect_id=OuterRef("pk"))),
        conversation=Exists(
            ColdCallRecord.objects.filter(
                prospect_id=OuterRef("pk"), had_owner_conversation=True
            )
        ),
    )

    prospects_filter = filters.ProspectsFilter(request.GET, queryset=prospects)

    paginator = Paginator(prospects_filter.qs, 10)
    page_number = request.GET.get("page")
    prospects_paginated = paginator.get_page(page_number)
    context = {
        "prospects_paginated": prospects_paginated,
        "prospects_filter": prospects_filter,
        "prospects_filtered_count": prospects_filter.qs.count(),
        "outcome_no_count": services.calls_outcome_no_count(),
        "total_calls_count": services.calls_total_count(),
        "calls_today": services.calls_today_count(),
        "prospects_total_count": services.prospects_total_count(),
        "local_times": services.get_city_local_times(),
    }
    return render(request, "home/prospects.html", context)


def prospects_delete_all(request):
    Prospect.objects.all().delete()
    return redirect("home:prospects-list")


def prospects_import_excel(request):
    if request.method == "POST":
        import_excel_form = ImportXlsxForm(request.POST, request.FILES)
        if import_excel_form.is_valid():
            industry = import_excel_form.cleaned_data["industry"]
            excel_file = request.FILES["excel_file"]
            services.import_prospects_from_excel(
                excel_file=excel_file, industry=industry
            )
            messages.success(request, "Prospects imported")
            return redirect("home:prospects-list")
    else:
        import_excel_form = ImportXlsxForm()

    context = {"import_excel_form": import_excel_form}
    return render(request, "home/prospects_import_excel.html", context)


def prospects__call_record_create(request, prospect_id):
    prospect = get_object_or_404(Prospect, id=prospect_id)

    if request.method == "POST":
        call_record_form = CallRecordForm(request.POST)
        if call_record_form.is_valid():
            call_record_form.save()
            next_url = request.GET.get("next")
            return redirect(next_url or "home:prospects-list")
    else:
        call_record_form = CallRecordForm(
            initial={
                "date": dt.datetime.now(datetime.UTC),
                "prospect": prospect,
                "my_area_code_city": "Toronto",
            }
        )

    context = {"call_record_form": call_record_form, "prospect": prospect}
    return render(
        request,
        "home/prospects__add_call.html",
        context,
    )


def call_records_list(request):
    call_records = ColdCallRecord.objects.all()
    context = {"call_records": call_records}
    return render(request, "home/call_records.html", context)


def call_record_create(request):
    if request.method == "POST":
        call_record_form = CallRecordForm(request.POST)
        if call_record_form.is_valid():
            call_record_form.save()
            next_url = request.GET.get("next")
            if next_url:
                return redirect(next_url)
            return redirect("home:call-records")
    else:
        prospect_id = request.GET.get("prospect_id")
        prospect = None
        if prospect_id:
            prospect = get_object_or_404(Prospect, id=prospect_id)

        call_record_form = CallRecordForm(
            initial={
                "date": dt.date.today(),
                "prospect": prospect,
                "my_area_code_city": "Toronto",
                "outcome": "no",
            }
        )

    return render(
        request,
        "home/call_records_create.html",
        {"call_record_form": call_record_form},
    )


def call_records_delete_all(request):
    ColdCallRecord.objects.all().delete()
    return redirect("home:call-records")


def htmx_test(request, action: str):
    match action:
        case "update_existence_status":
            existence_status = request.GET.get("existence_status")
            prospect_id = request.GET.get("prospect_id")
            if not existence_status:
                return HttpResponseBadRequest("existence_status is not in query param")
            if not prospect_id:
                return HttpResponseBadRequest("prospect_id is not in query param")

            prospect = Prospect.objects.get(id=prospect_id)
            prospect.existence_status = existence_status
            prospect.full_clean()
            prospect.save()

            context = {"existence_status": existence_status}
            return render(request, "home/htmx/test.html", context)

        case _:
            return HttpResponseBadRequest(f"invalid action: {action}")
