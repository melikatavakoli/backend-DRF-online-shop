from persiantools.jdatetime import JalaliDateTime
from rest_framework import serializers

from invoice.serializers import InvoiceSerializer
from transaction.models import Transaction, PaymentReceipt


class PaymentReceiptSerializer(serializers.ModelSerializer):
    uploaded_at = serializers.SerializerMethodField(read_only=True)
    receipt_url = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = PaymentReceipt
        fields = [
            "user",
            "image",
            "description",
            "uploaded_at",
            "receipt_url",
        ]

    def get_uploaded_at(self, obj):
        return JalaliDateTime.to_jalali(obj.uploaded_at).strftime("%Y/%m/%d %H:%M")

    def get_receipt_url(self, obj):
        return obj.image.url if obj.image else None


class TransactionSerializer(serializers.ModelSerializer):
    payment_receipt = PaymentReceiptSerializer(read_only=True)
    invoice = InvoiceSerializer(read_only=True)
    user = serializers.SerializerMethodField()
    fee = serializers.SerializerMethodField()
    calculated_amount = serializers.SerializerMethodField()

    class Meta:
        model = Transaction
        fields = [
            "user",
            "order",
            "amount",
            "fee",
            "bank_name",
            "card_number",
            "ref_number",
            "track_id",
            "status",
            "gateway",
            "payment_receipt",
            "invoice",
            "description",
            "calculated_amount",
        ]

    def get_created_at(self, obj):
        return JalaliDateTime.to_jalali(obj.created_at).strftime("%Y/%m/%d %H:%M")

    def get_updated_at(self, obj):
        return (
            JalaliDateTime.to_jalali(obj.updated_at).strftime("%Y/%m/%d %H:%M")
            if obj.updated_at
            else None
        )

    def get_user(self, obj):
        if not obj.user:
            return None
        return {
            "id": str(obj.user.id),
            "first_name": obj.user.first_name,
            "last_name": obj.user.last_name,
            "mobile": obj.user.mobile,
            "email": obj.user.email,
            "full_name": getattr(obj.user, "full_name", ""),
        }

    def get_fee(self, obj):
        return obj.fee

    def get_calculated_amount(self, obj):
        return obj.calculated_amount


class TransactionAdminListSerializer(serializers.ModelSerializer):
    user_full_name = serializers.CharField(source="user.full_name", read_only=True)

    class Meta:
        model = Transaction
        fields = [
            "id",
            "user_full_name",
            "amount",
            "status",
            "description",
        ]
        read_only_fields = fields

    def get_user_full_name(self, obj):
        if not obj.user:
            return None
        return getattr(
            obj.user,
            "full_name",
            f"{obj.user.first_name} {obj.user.last_name}",
        )


class TransactionUserListSerializer(serializers.ModelSerializer):
    fee = serializers.SerializerMethodField()
    calculated_amount = serializers.SerializerMethodField()

    class Meta:
        model = Transaction
        fields = [
            "id",
            "description",
            "status",
            "amount",
            "calculated_amount",
            "fee",
        ]
        read_only_fields = fields

    def get_fee(self, obj):
        return obj.fee

    def get_calculated_amount(self, obj):
        return obj.calculated_amount


class AdminTransactionStatusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ["id", "status"]
