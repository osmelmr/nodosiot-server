import uuid
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models


class UserManager(BaseUserManager):
    """
    Custom manager para usuarios que usan email en lugar de username.
    """

    use_in_migrations = True

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("El campo Email debe estar definido")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("El superusuario debe tener is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("El superusuario debe tener is_superuser=True.")

        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    """
    Modelo de usuario personalizado usando email como identificador principal
    y con UUID único.
    """

    class Roles(models.TextChoices):
        ADMIN = "admin", "Administrador"
        RESEARCHER = "researcher", "Investigador"
        FARMER = "farmer", "Agricultor"

    # Eliminamos el campo username
    username = None

    # UUID único para cada usuario
    uuid = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True
    )

    email = models.EmailField(
        unique=True,
        verbose_name="Correo electrónico"
    )

    role = models.CharField(
        max_length=20,
        choices=Roles.choices,
        default=Roles.FARMER,
        verbose_name="Rol del usuario"
    )

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []  # no se requiere ningún campo adicional

    objects = UserManager()

    def __str__(self):
        return f"{self.email} ({self.role})"
