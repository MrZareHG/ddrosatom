from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from django.contrib.contenttypes.models import ContentType
from .models import Event, EventParticipation

@receiver(post_save, sender=EventParticipation)
def update_event_participants(sender, instance, created, **kwargs):
    """Обновление счетчика участников при изменении участия"""
    if created:
        instance.event.current_participants += 1
        instance.event.save()
    elif instance.status == 'cancelled':
        instance.event.current_participants = max(0, instance.event.current_participants - 1)
        instance.event.save()

@receiver(pre_delete, sender=EventParticipation)
def decrease_event_participants(sender, instance, **kwargs):
    """Уменьшение счетчика участников при удалении участия"""
    if instance.status != 'cancelled':
        instance.event.current_participants = max(0, instance.event.current_participants - 1)
        instance.event.save()