This example is almost the same as `ex1` but it uses AWS SES to send messages.
Before running the example please edit bottom part of `ex2/settings.py` file.
Make sure that those settings are correct for you:

```python
EMAIL_HOST_USER = '<EMAIL_HOST_USER>'
EMAIL_FROM = 'MySite'
AWS_SES_REGION_NAME = 'eu-west-1'

# If you have aws cli configured (~/.aws directory)
# or you are using roles these settings can be left commented out

# AWS_SES_ACCESS_KEY_ID = ''
# AWS_SES_SECRET_ACCESS_KEY = ''
```

You can check the implementation of the handler in `app/messages_handlers.py`.

To run an example follow commands below:

```bash
virtualenv -p python3.6 venv
source venv/bin/activate
pip install git+https://github.com/jroslaniec/django-msg#egg=msg[boto3]

python manage.py migrate
python manage.py createsuperuser

# Username:
# Email address: <enter your email address here>
# Password:
# Password (again):
# Superuser created successfully.
```

To receive email use your existing email address - email is sent just after
user creation.

Note that email address email that you provide has to be verified in AWS SES
if your account is in the sandbox mode.
