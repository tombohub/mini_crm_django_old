from django.db import models


class Prospect(models.Model):
    """
    prospect's business details
    """

    PROVINCE_CHOICES = [
        ("AB", "Alberta"),
        ("BC", "British Columbia"),
        ("MB", "Manitoba"),
        ("NB", "New Brunswick"),
        ("NL", "Newfoundland and Labrador"),
        ("NT", "Northwest Territories"),
        ("NS", "Nova Scotia"),
        ("NU", "Nunavut"),
        ("ON", "Ontario"),
        ("PE", "Prince Edward Island"),
        ("QC", "Quebec"),
        ("SK", "Saskatchewan"),
        ("YT", "Yukon"),
    ]

    class ExistenceChoices(models.TextChoices):
        EXISTS = "exists"
        DOES_NOT_EXIST = "does_not_exist"
        UNKNOWN = "unknown"

    business_name = models.CharField(max_length=255, null=True, blank=True)
    industry = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=20, unique=True, null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    province = models.CharField(
        choices=PROVINCE_CHOICES, max_length=2, null=True, blank=True
    )
    street_address = models.CharField(max_length=255, null=True, blank=True)
    website_url = models.URLField(blank=True, null=True, max_length=255)
    yellow_pages_link = models.URLField(blank=True, null=True, max_length=255)

    existence_status = models.CharField(
        choices=ExistenceChoices, default=ExistenceChoices.UNKNOWN, max_length=20
    )
    """Does business still exist?"""

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def has_been_called(self) -> bool:
        """
        Check if the prospect has been called.

        This property returns True if there is at least one ColdCallRecord
        associated with the Prospect, and False otherwise.

        Returns:
            bool: True if the prospect has been called, False otherwise.
        """
        return self.coldcallrecord_set.exists()

    @property
    def had_owner_conversation(self) -> bool:
        """
        Check if any of the call records for the prospect had a conversation.

        This property returns True if there is at least one ColdCallRecord
        associated with the Prospect where had_conversation is True, and False otherwise.

        Returns:
            bool: True if any of the call records for the prospect had a conversation, False otherwise.
        """
        return self.coldcallrecord_set.filter(had_owner_conversation=True).exists()

    def __str__(self) -> str:
        return str(self.business_name)


class ColdCallRecord(models.Model):
    """
    record track of a cold call
    """

    OUTCOME_CHOICES = [
        ("no", "no"),
        ("yes", "yes"),
        ("meeting", "meeting"),
    ]

    PICK_UP_STATUS_CHOICES = [
        ("yes", "yes"),
        ("no", "no"),
        ("ivr", "ivr"),
        ("voicemail", "voicemail"),
        ("not connecting", "not connecting"),
    ]

    date = models.DateTimeField(null=True, blank=True)
    pick_up_status = models.CharField(
        choices=PICK_UP_STATUS_CHOICES,
        default="no",
        blank=True,
        null=True,
        max_length=255,
    )
    had_owner_conversation = models.BooleanField()
    outcome = models.CharField(
        choices=OUTCOME_CHOICES, blank=True, null=True, max_length=255
    )
    prospect = models.ForeignKey(Prospect, on_delete=models.PROTECT, null=True)
    my_area_code_city = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        default="Toronto",
    )
    product_selling = models.CharField(max_length=255, null=True, blank=True)
    opening = models.CharField(max_length=255, blank=True, null=True)
    objection = models.CharField(max_length=255, blank=True, null=True)
    note = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"{self.prospect} - {self.call_time}"
