import django
from django.conf import settings
from django.core.management import call_command

settings.configure(
    DEBUG=True,
    INSTALLED_APPS=(
        'django.contrib.contenttypes',
        'msg',
    ),
    MSG_SETTINGS={
        'handlers': []
    }
)

django.setup()
call_command('makemigrations', 'msg')
