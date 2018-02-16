This is a basic example of the default email handler in django-mgs.
To run this simple example you must edit bottom section of `ex1/settings.py`.
Make sure that those settings are correct for you:

```python
EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = '<EMAIL_HOST_USER>'
EMAIL_HOST_PASSWORD = '<EMAIL_HOST_PASSWORD>'
```

You can check the implementation of the handler in `app/messages_handlers.py`.

To run an example follow commands below:

```bash
virtualenv -p python3.6 venv
source venv/bin/activate
pip install git+https://github.com/jroslaniec/django-msg#egg=msg

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
