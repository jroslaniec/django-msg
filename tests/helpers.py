from django.test import TestCase

from msg.handlers import MetaHandler


class BaseTestCase(TestCase):

    def setUp(self):
        # Unregister all handlers at the beginning of each test
        MetaHandler._handlers_map = {}
