from django.db.models.signals import pre_delete
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import Node

User = get_user_model()

@receiver(pre_delete, sender=User)
def soft_delete_user_nodes(sender, instance, **kwargs):
    nodes = Node.objects.filter(user=instance, is_deleted=False)
    for node in nodes:
        node.delete()
