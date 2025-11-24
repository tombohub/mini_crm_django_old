import datetime as dt
from dataclasses import dataclass
from zoneinfo import ZoneInfo

import pandas as pd
from django.core.files.uploadedfile import UploadedFile
from ez_address_parser import AddressParser

from .models import ColdCallRecord, Prospect
from .utils import parse_website_url


def is_xlsx(uploaded_file: UploadedFile) -> bool:
    """
    Checks if the uploaded file is an Excel file with a .xlsx extension.

    Args:
        uploaded_file (UploadedFile): The file uploaded by the user.

    Returns:
        bool: True if the file is an Excel (.xlsx) file, False otherwise.
    """
    return uploaded_file.name.lower().endswith(".xlsx")


def validate_excel_columns(excel_file: UploadedFile, required_columns: list) -> bool:
    """
    Validates if the uploaded Excel file has the required columns.

    Args:
        excel_file (UploadedFile): The file uploaded by the user.
        required_columns (list): The list of required column names.

    Returns:
        bool: True if all required columns are present, False otherwise.
    """
    df = pd.read_excel(excel_file)
    return all(column in df.columns for column in required_columns)


def validate_yellow_pages_ca_excel_columns(excel_file: UploadedFile):
    """
    Validates columns for exported yellow pages CA excel
    """
    required_columns = ["Name", "Website", "Phone", "Address", "Link"]
    return validate_excel_columns(
        excel_file=excel_file, required_columns=required_columns
    )


def import_prospects_from_excel(excel_file: UploadedFile, industry: str):
    if not is_xlsx(excel_file):
        raise ValueError("Not an excel file")

    if not validate_yellow_pages_ca_excel_columns(excel_file=excel_file):
        raise ValueError(f"Excel columns are not correct")

    df1_dirty = pd.read_excel(excel_file)
    df2_removed_duplicates = df1_dirty.drop_duplicates(subset="Phone")
    df3_nan_to_none = df2_removed_duplicates.where(
        pd.notna(df2_removed_duplicates), None
    )

    prospect_list = []
    for row in df3_nan_to_none.itertuples():
        business_name = row.Name
        phone_number = row.Phone
        street_address = row.Address
        industry = industry
        yellow_pages_link = row.Link
        website_url = parse_website_url(row.Website) if row.Website else None
        city = extract_city_ca(street_address) if row.Address else None
        province = extract_province_ca(street_address) if row.Address else None

        prospect = Prospect(
            business_name=business_name,
            phone_number=phone_number,
            street_address=street_address,
            industry=industry,
            yellow_pages_link=yellow_pages_link,
            website_url=website_url,
            city=city,
            province=province,
        )
        prospect_list.append(prospect)
    Prospect.objects.bulk_create(
        prospect_list,
        update_conflicts=True,
        update_fields=["industry"],
        unique_fields=["phone_number"],
    )


def parse_yellow_pages_ca_address(address: str) -> dict:
    """
    Parses an address from Yellow Pages Canada and returns a dictionary with city and province.

    Args:
        address (str): The address string to parse, expected to be in the format "Street, City, Province PostalCode".

    Returns:
        dict: A dictionary with keys "city" and "province", containing the parsed city and province from the address.

    Raises:
        ValueError: If the address does not contain at least three parts separated by commas, a ValueError will be raised.
    """
    parts = address.split(",")
    if len(parts) < 3:
        raise ValueError("Address doesn't seem to be yellow pages CA")
    city = parts[1].strip()
    province = parts[2].split()[0]
    return {"city": city, "province": province}


def extract_city_ca(address: str) -> str:
    """
    Extracts the city name from a given Canadian address.

    Parameters:
    - address (str): The address string to be parsed.

    Returns:
    - str: The concatenated city name extracted from the address.

    Raises:
    - ValueError: If the city component is missing from the address or cannot be determined.

    Example:
    >>> extract_city_ca("296 Brock St E, Thunder Bay, ON P7E 4H4")
    'Thunder Bay'
    """
    parser = AddressParser()
    result = parser.parse(address)

    # parser returns structure like:
    # [('296', 'StreetNumber'),
    #  ('Brock', 'StreetName'),
    #  ('St', 'StreetType'),
    #  ('E', 'StreetDirection'),
    #  ('Thunder', 'Municipality'),
    #  ('Bay', 'Municipality'),
    #  ('ON', 'Province'),
    #  ('P7E', 'PostalCode'),
    #  ('4H4', 'PostalCode')]

    city = ""
    for item in result:
        if item[1] == "Municipality":
            city += (
                " " + item[0] if city else item[0]
            )  # to add space if more than one word
    return city


def extract_province_ca(address: str) -> str:
    parser = AddressParser()
    result = parser.parse(address)

    # parser returns structure like:
    # [('296', 'StreetNumber'),
    #  ('Brock', 'StreetName'),
    #  ('St', 'StreetType'),
    #  ('E', 'StreetDirection'),
    #  ('Thunder', 'Municipality'),
    #  ('Bay', 'Municipality'),
    #  ('ON', 'Province'),
    #  ('P7E', 'PostalCode'),
    #  ('4H4', 'PostalCode')]

    # library thinks city is province if province is missing
    province_codes = [
        "AB",
        "BC",
        "MB",
        "NB",
        "NL",
        "NT",
        "NS",
        "NU",
        "ON",
        "PE",
        "QC",
        "SK",
        "YT",
    ]

    province = ""
    for item in result:
        if item[1] == "Province":
            province = item[0]
    return province


def calls_outcome_no_count():
    outcome_no_count = ColdCallRecord.objects.filter(outcome="no").count()
    return outcome_no_count


def calls_total_count():
    calls_count = ColdCallRecord.objects.all().count()
    return calls_count


def prospects_total_count():
    count = Prospect.objects.all().count()
    return count


def calls_today_count():
    today = dt.date.today()
    count = ColdCallRecord.objects.filter(date__date=today).count()
    return count


def get_city_local_times():
    """
    This function returns the current local times for five
    Canadian cities: Halifax, Toronto, Winnipeg, Edmonton, and Vancouver.

    It uses the Python built-in `zoneinfo` module to handle time zones,
    and the `datetime` module to get the current time.

    Returns:
        CityTimes: A dataclass instance containing the local times
        for the five cities. Each city's time is a string in
        the format "HH:MM".
    """

    @dataclass
    class CityTimes:
        halifax: str
        toronto: str
        winnipeg: str
        edmonton: str
        vancouver: str

    time_zones = {
        "halifax": ZoneInfo("America/Halifax"),
        "toronto": ZoneInfo("America/Toronto"),
        "winnipeg": ZoneInfo("America/Winnipeg"),
        "edmonton": ZoneInfo("America/Edmonton"),
        "vancouver": ZoneInfo("America/Vancouver"),
    }

    current_time = lambda time_zone: (
        dt.datetime.now(time_zone).time().isoformat("minutes")
    )
    city_times = CityTimes(
        halifax=current_time(time_zones["halifax"]),
        toronto=current_time(time_zones["toronto"]),
        winnipeg=current_time(time_zones["winnipeg"]),
        edmonton=current_time(time_zones["edmonton"]),
        vancouver=current_time(time_zones["vancouver"]),
    )

    return city_times
