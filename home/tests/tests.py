from io import BytesIO
from unittest import TestCase as UnittestTestCase

import pandas as pd
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase as DjangoTestCase

from home import services
from home.business_data_extractor.extractor import extract_data
from home.models import ColdCallRecord, Prospect
from home.services import (
    import_prospects_from_excel,
    parse_yellow_pages_ca_address,
)
from home.utils import parse_website_url


class ExtractDataTest(UnittestTestCase):
    def test_extract_data(self):
        with open("home/business_data_extractor/yellow_pages_ca.html") as file:
            html = file.read()

        data = extract_data(html)

        expected_name_0 = "Elmwood Day Nursery Inc"
        expected_phone_0 = "204-668-7944"
        expected_website_0 = ""

        expected_name_4 = "YMCA"
        expected_phone_4 = "204-989-4106"
        expected_website_4 = "http://ymca.ca/"

        self.assertEqual(data[0].business_name, expected_name_0)
        self.assertEqual(data[0].phone_number, expected_phone_0)
        self.assertEqual(data[0].website_url, expected_website_0)

        self.assertEqual(data[4].business_name, expected_name_4)
        self.assertEqual(data[4].phone_number, expected_phone_4)
        self.assertEqual(data[4].website_url, expected_website_4)


class ProspectModelTest(DjangoTestCase):
    def test_has_been_called_without_calls(self):
        """Test that has_been_called is False when there are no call records."""
        prospect = Prospect.objects.create(
            business_name="Test Business",
            industry="Retail",
            phone_number="1234567890",
        )
        self.assertFalse(prospect.has_been_called)

    def test_has_been_called_with_calls(self):
        """Test that has_been_called is True when there are call records."""
        prospect = Prospect.objects.create(
            business_name="Test Business",
            industry="Retail",
            phone_number="1234567890",
        )
        ColdCallRecord.objects.create(
            prospect=prospect,
            had_owner_conversation=True,
        )
        self.assertTrue(prospect.has_been_called)

    def test_had_conversation(self):
        # Create a Prospect instance
        prospect = Prospect.objects.create(
            business_name="Test Business",
            industry="Test Industry",
            phone_number="1234567890",
            city="Test City",
        )

        # Assert that had_conversation is False when there are no related ColdCallRecords
        self.assertFalse(prospect.had_owner_conversation)

        # Create a ColdCallRecord instance related to the Prospect with had_conversation=False
        ColdCallRecord.objects.create(
            prospect=prospect,
            had_owner_conversation=False,
        )

        # Assert that had_conversation is still False
        self.assertFalse(prospect.had_owner_conversation)

        # Create a ColdCallRecord instance related to the Prospect with had_conversation=True
        ColdCallRecord.objects.create(
            prospect=prospect,
            had_owner_conversation=True,
        )

        # Assert that had_conversation is now True
        self.assertTrue(prospect.had_owner_conversation)


class TestParseYellowpagesCAAddress(UnittestTestCase):
    def test_parse_address_correctly(self):
        # Test case for a typical valid address
        address = "605 East Broadway, Vancouver, BC V5T 1X7"
        result = parse_yellow_pages_ca_address(address)
        self.assertEqual(result, {"city": "Vancouver", "province": "BC"})

        # Another test case for a different address
        address = "296 Brock St E, Thunder Bay, ON P7E 4H4"
        result = parse_yellow_pages_ca_address(address)
        self.assertEqual(result, {"city": "Thunder Bay", "province": "ON"})

    def test_parse_address_incorrect_format(self):
        # Test case for an incorrectly formatted address
        address = "605 East Broadway Vancouver BC V5T 1X7"
        with self.assertRaises(ValueError):
            parse_yellow_pages_ca_address(address)

    def test_address_with_extra_spaces(self):
        # Test case where the address contains extra spaces
        address = "  605 East Broadway  ,   Vancouver , BC V5T 1X7  "
        result = parse_yellow_pages_ca_address(address)
        self.assertEqual(result, {"city": "Vancouver", "province": "BC"})


class TestIsXlsxFunction(UnittestTestCase):
    def test_file_with_xlsx_extension(self):
        # Create a mock UploadedFile object with .xlsx extension
        file = SimpleUploadedFile("test.xlsx", "")
        self.assertTrue(services.is_xlsx(file))

    def test_file_with_uppercase_xlsx_extension(self):
        # Testing case insensitivity
        file = SimpleUploadedFile("test.XLSX", "")
        self.assertTrue(services.is_xlsx(file))

    def test_file_with_incorrect_extension(self):
        # Test with a non-.xlsx file
        file = SimpleUploadedFile("test.pdf", "")
        self.assertFalse(services.is_xlsx(file))

    def test_file_with_similar_extension(self):
        # Test with a similar but incorrect extension
        file = SimpleUploadedFile("test.xls", "")
        self.assertFalse(services.is_xlsx(file))


class TestValidateExcelColumns(UnittestTestCase):
    def create_excel_file(self, columns):
        """Helper function to create a mock Excel file."""
        df = pd.DataFrame(columns=columns)
        excel_io = BytesIO()
        df.to_excel(excel_io, index=False)
        excel_io.seek(0)
        return SimpleUploadedFile(
            "test.xlsx",
            excel_io.read(),
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

    def test_excel_with_required_columns(self):
        """Test with an Excel file that has all required columns."""
        required_columns = ["Name", "Email", "Phone"]
        file = self.create_excel_file(["Name", "Email", "Phone"])
        self.assertTrue(services.validate_excel_columns(file, required_columns))

    def test_excel_missing_some_required_columns(self):
        """Test with an Excel file missing some required columns."""
        required_columns = ["Name", "Email", "Phone"]
        file = self.create_excel_file(["Name", "Phone"])
        self.assertFalse(services.validate_excel_columns(file, required_columns))

    def test_excel_with_extra_columns(self):
        """Test with an Excel file that has extra columns."""
        required_columns = ["Name", "Email"]
        file = self.create_excel_file(["Name", "Email", "Phone", "Address"])
        self.assertTrue(services.validate_excel_columns(file, required_columns))


class TestExtractCity(UnittestTestCase):
    def test_extract_city_success(self):
        # Realistic address string that should successfully return a city name
        city = services.extract_city_ca("296 Brock St E, Thunder Bay, ON P7E 4H4")
        self.assertEqual(city, "Thunder Bay")


class TestExtractProvinceCA(UnittestTestCase):
    def test_extract_province_success(self):
        # Using a realistic address string that includes a clear province code
        province = services.extract_province_ca(
            "296 Brock St E, Thunder Bay, ON P7E 4H4"
        )
        self.assertEqual(
            province, "ON", "The function should correctly extract the province code."
        )


class TestParseWebsiteUrl(UnittestTestCase):
    def test_parse_valid_redirect_link(self):
        redirect_link = "http://example.com/?redirect=https://actualwebsite.com"
        expected_url = "https://actualwebsite.com"
        result = parse_website_url(redirect_link)
        self.assertEqual(
            result,
            expected_url,
            "The URL should be parsed correctly from a valid redirect link.",
        )

    def test_parse_missing_redirect(self):
        redirect_link = "http://example.com/?url=https://actualwebsite.com"
        with self.assertRaises(IndexError):
            parse_website_url(redirect_link)

    def test_input_none(self):
        result = parse_website_url(None)
        self.assertIsNone(
            result, "The function should return None when None is passed as input."
        )

    def test_malformed_url(self):
        redirect_link = "http:///badurl.com/?redirect=https://actualwebsite.com"
        expected_url = "https://actualwebsite.com"
        result = parse_website_url(redirect_link)
        self.assertEqual(
            result,
            expected_url,
            "The function should correctly parse even from a malformed base URL.",
        )
