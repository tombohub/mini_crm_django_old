from rest_framework import serializers

from .models import ColdCallRecord, Prospect


class ProspectSerializer(serializers.ModelSerializer):
    has_been_called = serializers.SerializerMethodField()
    had_conversation = serializers.SerializerMethodField()

    class Meta:
        model = Prospect
        fields = "__all__"

    @staticmethod
    def get_has_been_called(obj: Prospect) -> bool:
        """
        Returns whether the prospect has been called.

        Args:
            obj (Prospect): The Prospect instance.

        Returns:
            bool: True if the prospect has been called, False otherwise.
        """
        return obj.has_been_called

    @staticmethod
    def get_had_conversation(obj: Prospect) -> bool:
        """
        Returns whether any call record for the prospect had a conversation.

        Args:
            obj (Prospect): The Prospect instance.

        Returns:
            bool: True if any call record for the prospect had a conversation, False otherwise.
        """
        return obj.had_owner_conversation


class ProspectsImportCsvSerializer(serializers.ModelSerializer):
    csv_file = serializers.FileField()

    class Meta:
        model = Prospect
        fields = ["csv_file", "city", "industry"]


class ColdCallRecordSerializer(serializers.ModelSerializer):

    class Meta:
        model = ColdCallRecord
        fields = "__all__"
