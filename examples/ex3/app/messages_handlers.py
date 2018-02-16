from .models import User
from msg.handlers import MsgCtx
from msg.handlers import TwilioHandler
from msg.mixins import TypeMixin


class HelloMessageHandler(TypeMixin, TwilioHandler):
    name = 'Account Created'
    type = User.HelloSMSMessage
    template_text = 'app/sms/account-created.txt'

    def parse(self, hello: 'User.HelloSMSMessage') -> 'MsgCtx':
        recipients = [hello.phone_number]
        context = {'username': hello.username}
        return MsgCtx(recipients=recipients, context=context)
