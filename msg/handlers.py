import abc
import inspect
from typing import ClassVar
from typing import Dict
from typing import List
from typing import NamedTuple
from typing import Set

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template

from .exceptions import AmbiguousMsgHandlerException
from .settings import msg_settings


class MsgCtx(NamedTuple):
    recipients: 'List[str]'
    context: 'dict'
    language: 'str' = msg_settings.default_lang


class BaseHandler:
    pass


class MetaHandler(abc.ABCMeta):
    _handlers_map: 'Dict[str, ClassVar[Handler]]' = {}

    @classmethod
    def get_handler_cls(mcs, handler_name: 'str') -> 'ClassVar[Handler]':
        return mcs._handlers_map.get(handler_name)

    @classmethod
    def get_handlers(mcs) -> 'Dict[str, ClassVar[Handler]]':
        return mcs._handlers_map

    @staticmethod
    def check_fields(handler_cls) -> 'None':
        """
        Check if required fields are defined on the class.
        This method is called during creation of the class, so as soon
        handler class is created (class itself, not its instance) this
        constraint is checked.

        :param handler_cls:
            Handler class

        :return:
            None

        :raise
            AssertionError is raised if any of the required field is not
            defined on the handler class.

        """
        fields: 'Set[str]' = set()

        for cls in handler_cls.__mro__:
            if issubclass(cls, BaseHandler) and hasattr(cls, 'Meta'):
                fields.update(getattr(cls.Meta, 'fields', set()))

        for field in fields:
            assert hasattr(handler_cls, field), (
                f'Class {handler_cls.__name__} is required to '
                f'define `{field}` attribute.'
            )

    @classmethod
    def check_for_collisions(mcs, klass: 'ClassVar[Handler]') -> 'None':
        """
        Check for collision of `name` attribute in the new handle.
        (`name` attribute has to be unique among all non-abstract handlers)

        :param klass:
            Handler class

        :return:
            None

        :raise
            AmbiguousMsgHandlerException  is raised if collision is found.
        """
        if klass.name in mcs._handlers_map.keys():
            raise AmbiguousMsgHandlerException(
                f'`{klass.__name__}` class has colliding `name` attribute. '
                'You cannot create non-abstract handler class '
                'with colliding names. '
                'If you inherit the handler, '
                'please make sure that the name attribute is different.'
            )

    def __new__(mcs, name, bases, namespace, **kwargs):
        """
        Override of creation of handler class introducing
        fields and name collision checks for non-abstract classes.
        New classes are also registered in this meta class
        (as entry in `self._handlers_map` dict).
        """
        klass = super().__new__(mcs, name, bases, namespace, **kwargs)
        if not inspect.isabstract(klass):
            mcs.check_fields(klass)
            mcs.check_for_collisions(klass)
            mcs._handlers_map[klass.name] = klass
        return klass


class Handler(BaseHandler, metaclass=MetaHandler):
    """
    Interface for creating new handlers.
    """
    name: 'str'

    class Meta:
        fields = ['name']

    @abc.abstractmethod
    def match(self, *args, **kwargs):
        pass

    @abc.abstractmethod
    def parse(self, *args, **kwargs) -> 'MsgCtx':
        pass

    @abc.abstractmethod
    def send(self, msg):
        pass


class EmailHandler(Handler):
    subject: 'str'
    template_text: 'str'
    template_html: 'str'

    class Meta:
        fields = ['subject', 'template_text', 'template_html']

    def send(self, msg):
        assert hasattr(settings, 'EMAIL_FROM'), (
            '`settings.EMAIL_FROM` is not set.'
        )

        body_text = get_template(self.template_text).render(msg.context)
        email = EmailMultiAlternatives(
            subject=self.subject,
            body=body_text,
            from_email=settings.EMAIL_FROM,
            to=msg.recipients,
        )

        if self.template_html:
            body_html = get_template(self.template_html).render(msg.context)
            email.attach_alternative(body_html, 'text/html')

        email.send()


class SESHandler(Handler):
    subject: 'str'
    template_text: 'str'
    template_html: 'str'

    class Meta:
        fields = ['subject', 'template_text', 'template_html']

    charset = 'utf-8'

    def send(self, msg):
        assert hasattr(settings, 'EMAIL_HOST_USER'), (
            '`settings.EMAIL_HOST_USER` is not set.'
        )
        assert hasattr(settings, 'EMAIL_FROM'), (
            '`settings.EMAIL_FROM` is not set.'

        )

        email_sender = f'{settings.EMAIL_FROM} <{settings.EMAIL_HOST_USER}>'

        body_txt = get_template(self.template_text).render(msg.context)
        body_html = get_template(self.template_html).render(msg.context)

        client = self._get_client()
        client.send_email(
            Source=email_sender,
            Destination={
                'ToAddresses': msg.recipients,
            },
            Message={
                'Subject': {
                    'Data': self.subject,
                    'Charset': self.charset,
                },
                'Body': {
                    'Text': {
                        'Data': body_txt,
                        'Charset': self.charset,
                    },
                    'Html': {
                        'Data': body_html,
                        'Charset': self.charset,
                    }
                }
            }
        )

    @staticmethod
    def _get_client():
        kwargs = {
            'region_name': getattr(settings, 'AWS_SES_REGION_NAME'),
        }
        if hasattr(settings, 'AWS_SES_ACCESS_KEY_ID'):
            kwargs['aws_access_key_id'] = settings.AWS_SES_ACCESS_KEY_ID

        if hasattr(settings, 'AWS_SES_SECRET_ACCESS_KEY'):
            kwargs['aws_secret_access_key'] = settings.AWS_SES_SECRET_ACCESS_KEY

        import boto3
        return boto3.client('ses', **kwargs)


class TwilioHandler(Handler):
    template_text: 'str'

    class Meta:
        fields = ['template_text']

    def send(self, msg):
        assert hasattr(settings, 'TWILIO_ACCOUNT_SID'), (
            '`settings.TWILIO_ACCOUNT_SID` is not set.'
        )
        assert hasattr(settings, 'TWILIO_AUTH_TOKEN'), (
            '`settings.TWILIO_AUTH_TOKEN` is not set.'
        )

        sid = settings.TWILIO_ACCOUNT_SID
        auth_token = settings.TWILIO_AUTH_TOKEN

        from twilio.rest import Client
        client = Client(sid, auth_token)
        body = get_template(self.template_text).render(msg.context)

        for recipient in msg.recipients:
            client.api.account.messages.create(
                to=recipient,
                from_=settings.TWILIO_FROM_PHONE_NUMBER,
                body=body,
            )
