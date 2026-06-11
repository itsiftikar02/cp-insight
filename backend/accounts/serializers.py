from django.contrib.auth.models import User
from rest_framework import serializers

from .models import Profile


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)
    name = serializers.CharField(write_only=True, required=False, allow_blank=True)

    class Meta:
        model = User
        fields = ("id", "username", "email", "password", "name")

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Username already taken.")
        return value

    def create(self, validated_data):
        name = validated_data.pop("name", "")
        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data.get("email", ""),
            password=validated_data["password"],
        )
        Profile.objects.create(user=user, name=name)
        return user


class ProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)
    email = serializers.EmailField(source="user.email", required=False)

    class Meta:
        model = Profile
        fields = (
            "username", "email", "name", "codeforces_handle",
            "current_rating", "max_rating", "last_synced_at",
        )
        read_only_fields = ("current_rating", "max_rating", "last_synced_at")

    def update(self, instance, validated_data):
        user_data = validated_data.pop("user", {})
        if "email" in user_data:
            instance.user.email = user_data["email"]
            instance.user.save()
        return super().update(instance, validated_data)
