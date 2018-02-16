from typing import Union

from celery import shared_task

from .models import Msg


@shared_task
def dispatch_msg(msg_pk: 'Union[str, int]'):
    msg = Msg.objects.get(pk=msg_pk)
    msg.dispatch(async=False)
