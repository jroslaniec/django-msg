"""
source: https://github.com/ubernostrum/django-registration/blob/master/registration/runtests.py
A standalone test runner script, configuring the minimum settings
required for tests to execute.
Re-use at your own risk: many Django applications will require
different settings and/or templates to run their tests.
"""
import os
import sys

# Make sure the app is (at least temporarily) on the import path.
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, BASE_DIR)

SETTINGS = {
    'BASE_DIR': BASE_DIR,
    'INSTALLED_APPS': (
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.sites',

        'msg',
    ),
    # Test cases will override this liberally.
    # 'ROOT_URLCONF': 'registration.backends.hmac.urls',
    'DATABASES': {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
        },
    },
    'MIDDLEWARE': (
        'django.middleware.common.CommonMiddleware',
        'django.middleware.csrf.CsrfViewMiddleware',
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
    ),
    'SITE_ID': 1,
    'TEMPLATES': [{
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'tests', 'templates')],
        'OPTIONS': {
            'context_processors': [
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.debug',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    }],
    'MSG_SETTINGS': {
        'handlers': [],
    },
    'EMAIL_BACKEND': 'django.core.mail.backends.dummy.EmailBackend',
    'EMAIL_FROM': 'Test',
}


def run_tests():
    # Making Django run this way is a two-step process. First, call
    # config.configure() to give Django config to work with:
    from django.conf import settings
    settings.configure(**SETTINGS)

    # Then, call django.setup() to initialize the application cache
    # and other bits:
    import django
    if hasattr(django, 'setup'):
        django.setup()

    # Now we instantiate a test runner...
    from django.test.utils import get_runner
    TestRunner = get_runner(settings)

    # And then we run tests and return the results.
    test_runner = TestRunner(verbosity=2, interactive=True)
    failures = test_runner.run_tests(['tests'])
    sys.exit(bool(failures))


if __name__ == '__main__':
    run_tests()
