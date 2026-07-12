from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from .models import (
    Ingredient,
    Medicine,
    Nutrient,
    Prescription,
    PrescriptionItem,
)

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Public-safe representation of the authenticated user."""

    class Meta:
        model = User
        fields = ["id", "username"]


class RegisterSerializer(serializers.ModelSerializer):
    """Sign-up: create a user with a validated, hashed password."""

    password = serializers.CharField(
        write_only=True, style={"input_type": "password"}, min_length=8
    )

    class Meta:
        model = User
        fields = ["id", "username", "password"]

    def validate_password(self, value):
        validate_password(value)
        return value

    def create(self, validated_data):
        return User.objects.create_user(
            username=validated_data["username"],
            password=validated_data["password"],
        )


class NutrientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Nutrient
        fields = ["id", "name", "description"]


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ["id", "name", "description"]


class MedicineSerializer(serializers.ModelSerializer):
    ingredients = IngredientSerializer(many=True, read_only=True)

    class Meta:
        model = Medicine
        fields = ["id", "name", "manufacturer", "ingredients"]


class PrescriptionItemSerializer(serializers.ModelSerializer):
    medicine_name = serializers.CharField(source="medicine.name", read_only=True)

    class Meta:
        model = PrescriptionItem
        fields = ["id", "medicine", "medicine_name", "dosage_instruction"]


class PrescriptionSerializer(serializers.ModelSerializer):
    items = PrescriptionItemSerializer(many=True, required=False)

    class Meta:
        model = Prescription
        fields = ["id", "title", "issued_on", "created_at", "items"]
        read_only_fields = ["created_at"]

    def create(self, validated_data):
        items_data = validated_data.pop("items", [])
        prescription = Prescription.objects.create(**validated_data)
        for item in items_data:
            PrescriptionItem.objects.create(prescription=prescription, **item)
        return prescription


class NutrientRecommendationSerializer(serializers.Serializer):
    nutrient_id = serializers.IntegerField()
    nutrient_name = serializers.CharField()
    score = serializers.FloatField()
    # 이 영양소와 관련된 처방 약품명 목록 (성분명이 아님).
    medicines = serializers.ListField(child=serializers.CharField())


class NutrientConflictSerializer(serializers.Serializer):
    nutrient_id = serializers.IntegerField()
    nutrient_name = serializers.CharField()
    positive_medicines = serializers.ListField(child=serializers.CharField())
    caution_medicines = serializers.ListField(child=serializers.CharField())
    message = serializers.CharField()


class RecommendationResultSerializer(serializers.Serializer):
    needed = NutrientRecommendationSerializer(many=True)
    caution = NutrientRecommendationSerializer(many=True)
    conflicts = NutrientConflictSerializer(many=True)
