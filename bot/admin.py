from django.contrib import admin
from .models import Participant, Place, Event, Question, Donat


class ParticipantAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'subscriber',
        'organizer',
        'speaker',
        'tg_id'
    )
    list_filter = (
        'subscriber',
        'organizer',
        'speaker'
    )
    search_fields = ['tg_id']


class DonatAdmin(admin.ModelAdmin):
    list_display = (
        'donater',
        'size'
    )
    search_fields = [
        'donater'
    ]


class EventAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'speaker',
        'place',
        'start',
        'finish',
        'active'
    )
    search_fields = [
        'name',
    ]
    list_filter = (
        'name',
        'speaker',
        'place',
        'start',
        'active'
    )


class QuestionAdmin(admin.ModelAdmin):
    list_display = (
        'author',
        'question',
        'event',
        'tg_chat_id'
    )
    search_fields = [
        'event',
    ]
    list_filter = (
        'event',
    )


admin.site.register(Participant, ParticipantAdmin)
admin.site.register(Place)
admin.site.register(Event, EventAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(Donat, DonatAdmin)



# Register your models here.
