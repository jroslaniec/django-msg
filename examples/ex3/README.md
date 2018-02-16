In this example we will send "hello" sms message to a user.

For this example you will need a Twilio account.

Before running the example please edit bottom part of `ex2/settings.py` file.
Make sure that those settings are correct for you:

```python
TWILIO_FROM_PHONE_NUMBER = ''
TWILIO_ACCOUNT_SID = ''
TWILIO_AUTH_TOKEN = ''
```

Now you can enter following commands to send sms message.

```bash
$ python manage.py migrate
$ python manage.py createsuperuser
Username: Admin
Email address:
Password:
Password (again):
Superuser created successfully.

$ python manage.py shell
>>> from app.models import User
>>> u = User.objects.last()
>>> u.phone_number = '<YOUR PHONE NUMBER HERE>'
>>> u.save()
>>> u.send_hello_sms()
```

To see how its implemented look at `app/models.py` and `app/messages_handler.py`.
