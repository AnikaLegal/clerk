from core.models.issue import CaseTopic
from django.db import models
from rest_framework import serializers

from case.serializers.fields import BooleanYesNoDisplayField, ChoiceDisplayField

from .fields import FileUploadField
from .helpers import string_to_date


class RepairActions(models.TextChoices):
    INFORMED_RP = "Landlord", "Informed RP"
    ISSUED_BREACH = "Breaches", "Issued breach notice"
    APPLIED_CAV = "CAV", "Applied to CAV"
    APPLIED_VCAT = "APPLIED_VCAT", "Applied to VCAT"


class TopicSpecificSerializer(serializers.Serializer):
    def to_representation(self, instance):  # pyright: ignore [reportIncompatibleMethodOverride]
        issues = instance.get("ISSUES")
        if not isinstance(issues, list):
            issues = [issues]

        representation = {}
        for topic in issues:
            if topic == CaseTopic.REPAIRS:
                serializer = RepairsSpecificSerializer(instance)
            elif topic == CaseTopic.BONDS:
                serializer = BondsSpecificSerializer(instance)
            elif topic == CaseTopic.EVICTION_ARREARS:
                serializer = EvictionArrearsSpecificSerializer(instance)
            elif topic == CaseTopic.EVICTION_RETALIATORY:
                serializer = EvictionRetaliatorySpecificSerializer(instance)
            elif topic == CaseTopic.RENT_REDUCTION:
                serializer = RentReductionSpecificSerializer(instance)
            elif topic == CaseTopic.HEALTH_CHECK:
                serializer = HealthCheckSpecificSerializer(instance)
            elif topic == CaseTopic.OTHER:
                serializer = OtherSpecificSerializer(instance)
            else:
                continue
            representation[topic] = serializer.data or None

        if all(value is None for value in representation.values()):
            return None
        return representation

    def to_internal_value(self, data):
        data = super().to_internal_value(data)
        return {"topic_specific": data}


class RepairsSpecificSerializer(serializers.Serializer):
    issue_start = serializers.DateField(allow_null=True)
    issue_photos = serializers.ListField(
        allow_null=True, child=FileUploadField(allow_null=True)
    )
    applied_vcat = BooleanYesNoDisplayField(allow_null=True)
    vcat = serializers.ListField(
        allow_null=True, child=ChoiceDisplayField(choices=RepairActions.choices)
    )

    # Legacy fields
    issue_description = BooleanYesNoDisplayField(allow_null=True)
    required = serializers.ListField(allow_null=True, child=serializers.CharField())

    def to_representation(self, instance):  # pyright: ignore [reportIncompatibleMethodOverride]
        instance = {
            "issue_start": string_to_date(instance.get("REPAIRS_ISSUE_START")),
            "issue_photos": instance.get("REPAIRS_ISSUE_PHOTO"),
            "applied_vcat": instance.get("REPAIRS_APPLIED_VCAT"),
            "vcat": instance.get("REPAIRS_VCAT"),
            "issue_description": instance.get("REPAIRS_ISSUE_DESCRIPTION"),
            "required": instance.get("REPAIRS_REQUIRED"),
        }
        instance = super().to_representation(instance)
        if all(value is None for value in instance.values()):
            return {}
        return instance


class BondsSpecificSerializer(serializers.Serializer):
    claim_reasons = serializers.ListField(
        child=serializers.CharField(), allow_null=True
    )
    cleaning_claim_amount = serializers.IntegerField(allow_null=True)
    cleaning_claim_description = serializers.CharField(allow_null=True)
    cleaning_documents = serializers.ListField(
        allow_null=True, child=FileUploadField(allow_null=True)
    )
    damage_caused_by_tenant = BooleanYesNoDisplayField(allow_null=True)
    damage_claim_amount = serializers.IntegerField(allow_null=True)
    damage_claim_description = serializers.CharField(allow_null=True)
    damage_quote = serializers.ListField(
        allow_null=True, child=FileUploadField(allow_null=True)
    )
    has_landlord_made_rtba_application = BooleanYesNoDisplayField(allow_null=True)
    landlord_intents_to_make_claim = BooleanYesNoDisplayField(allow_null=True)
    locks_changed_by_tenant = BooleanYesNoDisplayField(allow_null=True)
    locks_claim_amount = serializers.IntegerField(allow_null=True)
    locks_change_quote = serializers.ListField(
        allow_null=True, child=FileUploadField(allow_null=True)
    )
    money_is_owed_by_tenant = BooleanYesNoDisplayField(allow_null=True)
    money_owed_claim_amount = serializers.IntegerField(allow_null=True)
    money_owed_claim_description = serializers.CharField(allow_null=True)
    move_out_date = serializers.DateField(allow_null=True)
    other_reasons_amount = serializers.IntegerField(allow_null=True)
    other_reasons_description = serializers.CharField(allow_null=True)
    tenant_has_rtba_application_copy = BooleanYesNoDisplayField(allow_null=True)
    rtba_application = serializers.ListField(
        allow_null=True, child=FileUploadField(allow_null=True)
    )

    def to_representation(self, instance):  # pyright: ignore [reportIncompatibleMethodOverride]
        instance = {
            # General
            "move_out_date": string_to_date(instance.get("BONDS_MOVE_OUT_DATE")),
            "has_landlord_made_rtba_application": instance.get(
                "BONDS_HAS_LANDLORD_MADE_RTBA_APPLICATION"
            ),
            "landlord_intents_to_make_claim": instance.get(
                "BONDS_LANDLORD_INTENTS_TO_MAKE_CLAIM"
            ),
            "tenant_has_rtba_application_copy": instance.get(
                "BONDS_TENANT_HAS_RTBA_APPLICATION_COPY"
            ),
            "rtba_application": instance.get("BONDS_RTBA_APPLICATION_UPLOAD"),
            "claim_reasons": instance.get("BONDS_CLAIM_REASONS"),
            # Cleaning
            "cleaning_claim_amount": instance.get("BONDS_CLEANING_CLAIM_AMOUNT"),
            "cleaning_claim_description": instance.get(
                "BONDS_CLEANING_CLAIM_DESCRIPTION"
            ),
            "cleaning_documents": instance.get("BONDS_CLEANING_DOCUMENT_UPLOADS"),
            # Damage
            "damage_claim_description": instance.get("BONDS_DAMAGE_CLAIM_DESCRIPTION"),
            "damage_claim_amount": instance.get("BONDS_DAMAGE_CLAIM_AMOUNT"),
            "damage_caused_by_tenant": instance.get("BONDS_DAMAGE_CAUSED_BY_TENANT"),
            "damage_quote": instance.get("BONDS_DAMAGE_QUOTE_UPLOAD"),
            # Locks
            "locks_changed_by_tenant": instance.get("BONDS_LOCKS_CHANGED_BY_TENANT"),
            "locks_claim_amount": instance.get("BONDS_LOCKS_CLAIM_AMOUNT"),
            "locks_change_quote": instance.get("BONDS_LOCKS_CHANGE_QUOTE"),
            # Money owed
            "money_is_owed_by_tenant": instance.get("BONDS_MONEY_IS_OWED_BY_TENANT"),
            "money_owed_claim_amount": instance.get("BONDS_MONEY_OWED_CLAIM_AMOUNT"),
            "money_owed_claim_description": instance.get(
                "BONDS_MONEY_OWED_CLAIM_DESCRIPTION"
            ),
            # Other reasons
            "other_reasons_amount": instance.get("BONDS_OTHER_REASONS_AMOUNT"),
            "other_reasons_description": instance.get(
                "BONDS_OTHER_REASONS_DESCRIPTION"
            ),
        }
        instance = super().to_representation(instance)
        if all(value is None for value in instance.values()):
            return {}
        return instance


class EvictionArrearsSpecificSerializer(serializers.Serializer):
    class CanAffordPaymentPlan(models.TextChoices):
        YES = "YES", "Yes"
        NO = "NO", "No"
        DISCUSS_OVER_PHONE = "DISCUSS_OVER_PHONE", "Would like to discuss over phone"

    doc_delivery_time_notice_to_vacate = serializers.DateField(allow_null=True)
    has_notice = BooleanYesNoDisplayField(allow_null=True)
    is_already_removed = BooleanYesNoDisplayField(allow_null=True)
    is_unpaid_rent = BooleanYesNoDisplayField(allow_null=True)
    is_vcat_date = BooleanYesNoDisplayField(allow_null=True)
    notice_send_date = serializers.DateField(allow_null=True)
    notice_vacate_date = serializers.DateField(allow_null=True)
    payment_fail_description = serializers.CharField(allow_null=True)
    payment_fail_reason = serializers.ListField(
        allow_null=True, child=serializers.CharField()
    )
    vcat_date = serializers.DateField(allow_null=True)
    documents = serializers.ListField(
        allow_null=True, child=FileUploadField(allow_null=True)
    )

    can_afford_payment_plan = ChoiceDisplayField(
        allow_null=True, choices=CanAffordPaymentPlan.choices
    )
    documents_provided = serializers.ListField(
        allow_null=True, child=serializers.CharField()
    )
    delivery_method_notice_to_vacate = serializers.CharField(allow_null=True)
    delivery_method_other_docs = serializers.CharField(allow_null=True)
    delivery_method_possession_order = serializers.CharField(allow_null=True)
    doc_delivery_time_other_docs = serializers.DateField(allow_null=True)
    is_on_payment_plan = BooleanYesNoDisplayField(allow_null=True)
    miscellaneous = serializers.CharField(allow_null=True)
    payment_amount = serializers.IntegerField(allow_null=True)
    payment_fail_change = serializers.CharField(allow_null=True)
    rent_cycle = serializers.CharField(allow_null=True)
    rent_unpaid = serializers.IntegerField(allow_null=True)

    def to_representation(self, instance):  # pyright: ignore [reportIncompatibleMethodOverride]
        instance = {
            "doc_delivery_time_notice_to_vacate": string_to_date(
                instance.get("EVICTION_ARREARS_DOC_DELIVERY_TIME_NOTICE_TO_VACATE")
            ),
            "has_notice": instance.get("EVICTION_ARREARS_HAS_NOTICE"),
            "is_already_removed": instance.get("EVICTION_ARREARS_IS_ALREADY_REMOVED"),
            "is_unpaid_rent": instance.get("EVICTION_ARREARS_IS_UNPAID_RENT"),
            "is_vcat_date": instance.get("EVICTION_ARREARS_IS_VCAT_DATE"),
            "notice_send_date": string_to_date(
                instance.get("EVICTION_ARREARS_NOTICE_SEND_DATE")
            ),
            "notice_vacate_date": string_to_date(
                instance.get("EVICTION_ARREARS_NOTICE_VACATE_DATE")
            ),
            "payment_fail_description": instance.get(
                "EVICTION_ARREARS_PAYMENT_FAIL_DESCRIPTION"
            ),
            "payment_fail_reason": instance.get("EVICTION_ARREARS_PAYMENT_FAIL_REASON"),
            "vcat_date": string_to_date(instance.get("EVICTION_ARREARS_VCAT_DATE")),
            "documents": instance.get("EVICTION_ARREARS_DOCUMENTS_UPLOAD"),
            # NOTE: All below here are legacy values.
            "can_afford_payment_plan": instance.get(
                "EVICTION_ARREARS_CAN_AFFORD_PAYMENT_PLAN"
            ),
            "documents_provided": instance.get("EVICTION_ARREARS_DOCUMENTS_PROVIDED"),
            "delivery_method_notice_to_vacate": instance.get(
                "EVICTION_ARREARS_DOC_DELIVERY_METHOD_NOTICE_TO_VACATE"
            ),
            "delivery_method_other_docs": instance.get(
                "EVICTION_ARREARS_DOC_DELIVERY_METHOD_OTHER_DOCS"
            ),
            "delivery_method_possession_order": instance.get(
                "EVICTION_ARREARS_DOC_DELIVERY_METHOD_POSSESSION_ORDER"
            ),
            "doc_delivery_time_other_docs": string_to_date(
                instance.get("EVICTION_ARREARS_DOC_DELIVERY_TIME_OTHER_DOCS")
            ),
            "doc_delivery_time_possession_order": string_to_date(
                instance.get("EVICTION_ARREARS_DOC_DELIVERY_TIME_POSSESSION_ORDER")
            ),
            "is_on_payment_plan": instance.get("EVICTION_ARREARS_IS_ON_PAYMENT_PLAN"),
            "miscellaneous": instance.get("EVICTION_ARREARS_MISC"),
            "payment_amount": instance.get("EVICTION_ARREARS_PAYMENT_AMOUNT"),
            "payment_fail_change": instance.get("EVICTION_ARREARS_PAYMENT_FAIL_CHANGE"),
            "rent_cycle": instance.get("EVICTION_ARREARS_RENT_CYCLE"),
            "rent_unpaid": instance.get("EVICTION_ARREARS_RENT_UNPAID"),
        }
        instance = super().to_representation(instance)
        if all(value is None for value in instance.values()):
            return None
        return instance


class EvictionRetaliatorySpecificSerializer(serializers.Serializer):
    date_received_ntv = serializers.DateField(allow_null=True)
    has_notice = BooleanYesNoDisplayField(allow_null=True)
    is_already_removed = BooleanYesNoDisplayField(allow_null=True)
    ntv_type = serializers.CharField(allow_null=True)
    retaliatory_reason = serializers.ListField(
        allow_null=True, child=serializers.CharField()
    )
    retaliatory_reason_other = serializers.CharField(allow_null=True)
    termination_date = serializers.DateField(allow_null=True)
    vcat_hearing = BooleanYesNoDisplayField(allow_null=True)
    vcat_hearing_date = serializers.DateField(allow_null=True)
    documents = serializers.ListField(
        allow_null=True, child=FileUploadField(allow_null=True)
    )

    def to_representation(self, instance):  # pyright: ignore [reportIncompatibleMethodOverride]
        instance = {
            "date_received_ntv": string_to_date(
                instance.get("EVICTION_RETALIATORY_DATE_RECEIVED_NTV")
            ),
            "has_notice": instance.get("EVICTION_RETALIATORY_HAS_NOTICE"),
            "is_already_removed": instance.get(
                "EVICTION_RETALIATORY_IS_ALREADY_REMOVED"
            ),
            "ntv_type": instance.get("EVICTION_RETALIATORY_NTV_TYPE"),
            "retaliatory_reason": instance.get(
                "EVICTION_RETALIATORY_RETALIATORY_REASON"
            ),
            "retaliatory_reason_other": instance.get(
                "EVICTION_RETALIATORY_RETALIATORY_REASON_OTHER"
            ),
            "termination_date": string_to_date(
                instance.get("EVICTION_RETALIATORY_TERMINATION_DATE")
            ),
            "vcat_hearing": instance.get("EVICTION_RETALIATORY_VCAT_HEARING"),
            "vcat_hearing_date": string_to_date(
                instance.get("EVICTION_RETALIATORY_VCAT_HEARING_DATE")
            ),
            "documents": instance.get("EVICTION_RETALIATORY_DOCUMENTS_UPLOAD"),
        }
        instance = super().to_representation(instance)
        if all(value is None for value in instance.values()):
            return {}
        return instance


class RentReductionSpecificSerializer(serializers.Serializer):
    issues = serializers.ListField(allow_null=True, child=serializers.CharField())
    issue_description = serializers.CharField(allow_null=True)
    issue_start = serializers.DateField(allow_null=True)
    is_notice_to_vacate = BooleanYesNoDisplayField(allow_null=True)
    issue_photos = serializers.ListField(
        allow_null=True, child=FileUploadField(allow_null=True)
    )
    notice_to_vacate = serializers.ListField(
        allow_null=True, child=FileUploadField(allow_null=True)
    )

    def to_representation(self, instance):  # pyright: ignore [reportIncompatibleMethodOverride]
        instance = {
            "issues": instance.get("RENT_REDUCTION_ISSUES"),
            "issue_description": instance.get("RENT_REDUCTION_ISSUE_DESCRIPTION"),
            "issue_start": string_to_date(instance.get("RENT_REDUCTION_ISSUE_START")),
            "issue_photos": instance.get("RENT_REDUCTION_ISSUE_PHOTO"),
            "is_notice_to_vacate": instance.get("RENT_REDUCTION_IS_NOTICE_TO_VACATE"),
            "notice_to_vacate_documents": instance.get(
                "RENT_REDUCTION_NOTICE_TO_VACATE_DOCUMENT"
            ),
        }
        instance = super().to_representation(instance)
        if all(value is None for value in instance.values()):
            return {}
        return instance


class HealthCheckSpecificSerializer(serializers.Serializer):
    support_worker_authority = serializers.ListField(
        allow_null=True, child=FileUploadField(allow_null=True)
    )
    tenancy_documents = serializers.ListField(
        allow_null=True, child=FileUploadField(allow_null=True)
    )

    def to_representation(self, instance):  # pyright: ignore [reportIncompatibleMethodOverride]
        instance = {
            "support_worker_authority": instance.get("SUPPORT_WORKER_AUTHORITY_UPLOAD"),
            "tenancy_documents": instance.get("TENANCY_DOCUMENTS_UPLOAD"),
        }
        instance = super().to_representation(instance)
        if all(value is None for value in instance.values()):
            return {}
        return instance


class OtherSpecificSerializer(serializers.Serializer):
    issue_description = serializers.CharField(allow_null=True)

    def to_representation(self, instance):  # pyright: ignore [reportIncompatibleMethodOverride]
        instance = {
            "issue_description": instance.get("OTHER_ISSUE_DESCRIPTION"),
        }
        instance = super().to_representation(instance)
        if all(value is None for value in instance.values()):
            return {}
        return instance
