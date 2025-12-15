from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        required=False,
    )

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "password",
            "role",
        )
        read_only_fields = (
            "id",
        )

    def create(self, validated_data):
        password = validated_data.pop("password", None)

        user = User.objects.create_user(
            password=password,
            **validated_data
        )

        # 🔒 Regla de negocio: superuser siempre es ADMIN
        if user.is_superuser:
            user.role = User.Roles.ADMIN
            user.save(update_fields=["role"])

        return user

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if password:
            instance.set_password(password)

        # 🔒 Regla de negocio: superuser siempre es ADMIN
        if instance.is_superuser:
            instance.role = User.Roles.ADMIN

        instance.save()
        return instance
