# Django-msg

Small Django package to help with notifying users via email or SMS.

Supported notification types:

- email
    - default django emails
    - Amazon Simple Email Service (SES)
- sms
    - Twilio

Celery support is also included.

##  Requirements:

- Python3.6.x, Python3.7.x
- Django 2.0.0+
- psycopg2
- Works only with Postgres

Optional requirements:

- celery 4.0.0+
- twilio 6.0.0+
- boto3  1.0.0+

# Installation

```bash
pip install git+https://github.com/jroslaniec/django-msg@0.1.2#egg=django-msg
```

To use asynchronous notification sending, AWS SES or Twilio you must
install additional dependencies.
For asynchronous task install celery, for AWS SES you need boto3 and for SMSes
you need twilio. You can install them independently or with one of the following commands:

```bash
pip install git+https://github.com/jroslaniec/django-msg@0.1.2#egg=django-msg[celery]
pip install git+https://github.com/jroslaniec/django-msg@0.1.2#egg=django-msg[boto3]
pip install git+https://github.com/jroslaniec/django-msg@0.1.2#egg=django-msg[twilio]
pip install git+https://github.com/jroslaniec/django-msg@0.1.2#egg=django-msg[all]
```

# Usage

To send notifications with django-msg you must define notification a handlers class.
This handler class has to inherit from `Handler` abstract class and
implement following methods:
- match
- parse
- send

When we create a message (with `Msg.new(*args, **kwargs)`) we try to match passed arguments
with a handler by iterating through all registered handlers. The first handler which return `True` on `match(*args, **kwargs)` will handle sending
the message.

Then, all arguments are passed to `parse(*args, **kwargs)` method of the matched handler.
This method has to return `MsgCtx` object.

And lastly MsgCtx object is passed to `send(msg_context)`. To send message use either

```python
Msg.new(*args, send_now=True, **kwargs)
```

or

```python
msg = Msg.new(*args, **kwargs)
# some code here
msg.dispatch() # or msg.dispatch(defer=True/False)
```

Handler example:

```python
from django.conf import settings
from django.contrib.auth import get_user_model

from msg.handlers import EmailHandler
from msg.handlers import MsgCtx
from msg.mixins import TypeMixin
from msg.models import Msg

User = get_user_model()


class AccountCreatedHandler(TypeMixin, EmailHandler):
    name = 'Account Created'
    type = User
    subject = 'Your new shiny account has been created!'
    template_text = 'app/emails/account-created.txt'
    template_html = 'app/emails/account-created.html'

    def parse(self, user) -> 'MsgCtx':
        recipients = [user.email]
        context = {
            'username': user.username,
            'login_url': settings.ADMIN_LOGIN_URL,
        }
        return MsgCtx(recipients=recipients, context=context)

# Sending a message
user = User.objects.last()
Msg.new(user, dispatch_now=True)
```

## Translation / i18n

A Basic form of internationalization is supported. You can
freely user `{% trans %}` blocks in your templates and translation
string in handler attributes.

You can specify language of the message by `language` argument in `MsgCtx`

```python
from django.utils.translation import ugettext_lazy as _

from msg.handlers import Handler
from msg.handlers import MsgCtx

class EnglishHandler(Handler):
    subject = _('Hello World')
    ...
    def parse(self, recipient):
        return MsgCtx(
            recipients=[recipient],
            context={},
            language='en'
        )
    ...
```

Default language can be set with `default_lang`. The default is set to`en`.

```python
MSG_SETTINGS = {
    'default_lang': 'en',
    ...
}
```

## Usage with celery

You should be able to send messages with celery without major problems.
The task in charge of sending messages is declared as celery's `shared_task`.
Make sure that you have celery appropriately configured for your Django project
and you should be ready to go.

If you want to send messages with celery by default you can set `defer` setting
to `True`.

```python
MSG_SETTINGS = {
    'defer': True,
    ...
}
```

Also, you can send message asynchornously with:

```python
Msg.new(*args, dispatch_now=True, defer=True, **kwrags)
```

or

```python
msg = Msg.new(*args, dispatch_now=False, **kwargs)
msg.send(defer=True)
```

## Default handlers base classes

### `Handler`

Base abstract class for defining user's handlers. For more information
see "Defining your own handler section".

### `EmailHandler`

Email handler base that requires default django settings to send an email.
Required methods to override:

- `match(*args, **kwargs) -> bool`
- `parse(*args, **kwargs) -> MsgCtx`

Attributes required to be defined:

- `name`
- `subject`
- `template_text`
- `template_html`


### `SESHandler`

Handler base for sending emails with AWS SES.

Required methods to override:

- `match(*args, **kwargs) -> bool`
- `parse(*args, **kwargs) -> MsgCtx`

Attributes required to be defined:

- `name`
- `subject`
- `template_text`
- `template_html`


### `TwilioHandler`

Handler base for sending SMS messages with Twilio.

Required methods to override:

- `match(*args, **kwargs) -> bool`
- `parse(*args, **kwargs) -> MsgCtx`

Attributes required to be defined:

- `name`
- `template_text`

## Defining your own handler

New handler has to inherit `Handler` class and override
its all abstract methods.

These methods are:

- `match(*args, **kwargs) -> bool`
- `parse(*args, **kwargs) -> MsgCtx`
- `send(MsgCts) -> None`

Also, `Handler` requires that `name` attribute is defined
on the derived class. `name` attribute has to be unique
across all defined handlers.
If you are writing another base class or mixin you may want
to require additional attributes on derived classes. You can
force that with field list in `Meta` subclass.

```python
from msg.handlers import Handler


class NewHandler(Handler):
    class Meta:
        fields = ['version']
```

This way will ensure that instantiable (non-abstract) class that inherits from
`NewHandler` will have to define `version` attribute.

## Settings

Main django-msg settings are defined in `MSG_SETTINGS` and it has following keys
(defaults are as follow):

- `defer=False`
- `handlers=[]`
- `default_lang='en'`

If `defer` is set to `True` then celery will handle sending a notification.
`handlers` is a list of string to handler classes (see example below).

Support for emails, SES emails and Twilio requires additional settings.
These are defined outside of `MSG_SETTINGS`.

Also, there is a special setting `MSG_SKIP_MESSAGE`. See Testing section for
more information.

### Emails

Required settings:

- `EMAIL_USE_TLS`
- `EMAIL_HOST`
- `EMAIL_PORT`
- `EMAIL_HOST_USER`
- `EMAIL_HOST_PASSWORD`
- `EMAIL_FROM`

### SES Emails

Required settings:

- `EMAIL_HOST_USER`
- `EMAIL_FROM`
- `AWS_SES_REGION_NAME`

If you are using proper roles you should omit following settings,
otherwise they are necessary.

- `AWS_SES_ACCESS_KEY_ID`
- `AWS_SES_SECRET_ACCESS_KEY`

### SMS with Twilio

Required settings:

- `TWILIO_FROM_PHONE_NUMBER`
- `TWILIO_ACCOUNT_SID`
- `TWILIO_AUTH_TOKEN`

### Configuration example

```python
# settings.py
...

### Configuration for basic emails
EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'example@gmail.com'
EMAIL_HOST_PASSWORD = 'top-secret-123'
EMAIL_FROM = 'MySite'

### Configuration for SES
EMAIL_HOST_USER = 'example@gmail.com'
EMAIL_FROM = 'MySite'

AWS_SES_REGION_NAME = 'eu-central-1'

# You should omit those if you are using AWS roles...
AWS_SES_ACCESS_KEY_ID = '1234567890'
AWS_SES_SECRET_ACCESS_KEY = '1234567890'

### Configuration for Twilio
TWILIO_FROM_PHONE_NUMBER = '+12123123123'
TWILIO_ACCOUNT_SID = '1234567890'
TWILIO_AUTH_TOKEN= '1234567890'

MSG_SETTINGS = {
    'defer': True,  # Celery will dispatch messages.
    'handlers': [
        'app.messages_handlers.AccountCreatedHandler',
        'app.messages_handlers.TransactionStartedHandler',
    ]
}

...
```

## Testing

When you are testing your application you (probably) don't want to send any emails or
other messages. The easies way to prevent this is to
set `MSG_SKIP_MESSAGE` settings. Overriding this settings on TestCase class is
a good idea.

```python
from django.test import TestCase
from django.test import override_settings


@override_settings(MSG_SKIP_SEND=True)
class BaseTestCase(TestCase):
    pass
```

This method will skip sending message completely and automatically set status to `Done`.

Another possibility is to mock `Msg._dispatch()` or `Msg._send()` method.

Tip: If you are using Django's build-in emails (Msg's `EmailHandler`), you can change `EMAIL_BACKEND`
to `django.core.mail.backends.dummy.EmailBackend`.

```python
from django.test import TestCase
from django.test import override_settings


@override_settings(EMAIL_BACKEND='django.core.mail.backends.dummy.EmailBackend')
class BaseTestCase(TestCase):
    pass
```

# Examples

See [examples](examples) director for simple examples.

# Package tests

Sadly, tests are a little bit lacking at the moment.
Anyway, if you want to run them, you can do that with:

```bash
python tests/runtests.py
```

\* (todo) Tests no longer pass due to no support for other DBs than postgres.

# Changelog

## 0.2.2

Set proper Msg.context default

## 0.2.1

Drop previous migrations

## 0.2.0

Replace django-jsonfield with Django's built-in JSONfield for Postgres.

## 0.1.2

Add support for Python3.7.x - rename `MSG_SETTINGS` `async` option to `defer` to fix compatibility issue
(`async` keyword is reserved since Python3.7).
