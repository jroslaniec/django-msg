This example is asynchronous version of the ex1.
Celery package is required to be installed. Also, running RabbitMQ is necessary.
The easies way to run RabbitMQ
for this example is to create docker container with:

```bash
docker run \
    -d \
    -p 5672:5672 \
    -e RABBITMQ_DEFAULT_USER=guest \
    -e RABBITMQ_DEFAULT_PASS=guest \
    --net host \
    --rm \
    rabbitmq
```

Note that 'async' setting is set to `True`

```python
# settings.py
MSG_SETTINGS = {
    ...
    'async': True,
    ...
}
```

Like with other examples, please check that this settings are correct for you:

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
pip install git+https://github.com/jroslaniec/django-msg#egg=msg[celery]

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
