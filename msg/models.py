from enum import Enum
from typing import Union

from django.db import models
from django.utils import translation
from django.utils.translation import ugettext_lazy as _
from jsonfield import JSONField

from .exceptions import MissingHandlerException
from .handlers import Handler
from .handlers import MetaHandler
from .settings import msg_settings


class MsgManager(models.Manager):

    def create_from_any(self, *args, **kwargs) -> 'Msg':

        handler: 'Union[Handler, None]' = None

        for handler_name, handler_cls in MetaHandler.get_handlers().items():
            h: 'Handler' = handler_cls()
            if h.match(*args, **kwargs):
                handler = h
                break

        if handler is None:
            raise MissingHandlerException(
                'No handler found for provided arguments '
                f'(args: {args!r}, kwargs: {kwargs!r}).'
            )

        msg_ctx = handler.parse(*args, **kwargs)

        obj: 'Msg' = self.model(
            type=handler.name,
            status=Msg.Status.NEW.value,
            language=msg_ctx.language,
            recipients=msg_ctx.recipients,
            context=msg_ctx.context,
        )
        obj.handler = handler

        self._for_write = True
        obj.save(force_insert=True, using=self.db)
        return obj


class Msg(models.Model):
    _handler: 'Handler'

    class Status(Enum):
        @classmethod
        def choices(cls):
            return tuple((member.value, name)
                         for name, member in cls.__members__.items())

        NEW = 1
        PENDING = 2
        DONE = 3
        ERROR = 4

    type = models.CharField(
        verbose_name=_('Type'),
        max_length=255,
    )
    status = models.PositiveSmallIntegerField(
        verbose_name=_('Status'),
        choices=Status.choices(),
        default=Status.NEW.value,
    )
    language = models.CharField(
        verbose_name=_('Language'),
        max_length=32,
    )
    recipients = JSONField(
        verbose_name=_('Recipients'),
    )
    context = JSONField(
        verbose_name=_('Context'),
        default={},
        blank=True,
    )
    created = models.DateTimeField(
        verbose_name=_('Created'),
        auto_now_add=True,
    )
    modified = models.DateTimeField(
        _('Modified'),
        auto_now=True,
    )

    objects = MsgManager()

    @staticmethod
    def new(*args, dispatch_now, async=msg_settings.async, **kwargs):
        msg = Msg.objects.create_from_any(*args, **kwargs)

        if dispatch_now:
            msg.dispatch(async=async)

        return msg

    def set_status(self, new_status: 'Status', save=False) -> 'None':
        self.status = Msg.Status(new_status).value

        if save:
            self.save()

    def dispatch(self, async=msg_settings.async):
        self.set_status(Msg.Status.PENDING, save=True)
        if async:
            self._dispatch_delay()
        else:
            self._dispatch()

    def _dispatch(self):
        cur_language = translation.get_language()
        try:
            translation.activate(self.language)
            self._send()
        except Exception as exc:
            self.set_status(Msg.Status.ERROR, save=True)
            raise exc
        finally:
            translation.activate(cur_language)

        self.set_status(Msg.Status.DONE, save=True)

    def _send(self):
        if not msg_settings.skip_send:
            self.handler.send(self)

    def _dispatch_delay(self):
        from .tasks import dispatch_msg
        dispatch_msg.delay(self.pk)

    @property
    def handler(self):
        if not hasattr(self, '_handler'):
            self._handler = self.get_handler()
        return self._handler

    @handler.setter
    def handler(self, handler):
        self._handler = handler

    def get_handler(self):
        handler_cls = MetaHandler.get_handler_cls(self.type)
        if handler_cls is None:
            raise MissingHandlerException(
                f'{self.type} - such message handler does not exist'
            )
        return handler_cls()
