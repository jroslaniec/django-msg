from typing import NamedTuple

from django.contrib.auth.models import AbstractUser
from django.db import models

from msg.models import Msg


class User(AbstractUser):
    phone_number: 'str' = models.CharField(max_length=255,
                                           null=True, blank=True)

    class HelloSMSMessage(NamedTuple):
        phone_number: 'str'
        username: 'str'

    def send_hello_sms(self):
        if not self.phone_number:
            raise ValueError('User has to have a phone number'
                             'to send a sms message.')
        hello = self.HelloSMSMessage(
            username=self.username,
            phone_number=self.phone_number,
        )
        Msg.new(hello, dispatch_now=True)
