from django import forms
from django.conf import settings
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from .models import Msg
from .settings import msg_settings


def get_type_choices():
    return ((h.name, h.name) for h in msg_settings.handlers)


class MsgModelForm(forms.ModelForm):
    type = forms.ChoiceField(choices=get_type_choices())
    language = forms.ChoiceField(
        choices=settings.LANGUAGES,
        initial=msg_settings.default_lang,
    )

    class Meta:
        model = Msg
        fields = '__all__'


@admin.register(Msg)
class MsgModelAdmin(admin.ModelAdmin):
    _language_map = dict(settings.LANGUAGES)

    form = MsgModelForm
    search_fields = ['type', 'recipients']
    list_filter = ['type', 'status', 'language', 'created', 'modified']
    list_display = ['id', 'type', 'status', 'get_language', 'recipients',
                    'created', 'modified']

    actions = ['send_selected_messages']

    def get_language(self, obj):
        return self._language_map.get(obj.language, obj.language)

    get_language.short_description = _('language')

    def send_selected_messages(self, request, queryset):
        for instance in queryset:
            instance.dispatch()
