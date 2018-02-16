from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver

from msg.handlers import EmailHandler
from msg.handlers import MsgCtx
from msg.mixins import TypeMixin
from msg.models import Msg

User = get_user_model()


@receiver(post_save, sender=User)
def send_email(sender, instance, created, **kwargs):
    if not created:
        return

    Msg.new(instance, dispatch_now=True)


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
