from django.core import mail
from django.test import override_settings

from .helpers import BaseTestCase
from msg.exceptions import MissingHandlerException
from msg.handlers import EmailHandler
from msg.handlers import Handler
from msg.handlers import MetaHandler
from msg.handlers import MsgCtx
from msg.models import Msg


class HandlersTestBase(BaseTestCase):

    def test_handler_class_cannot_be_created_without_name_attribute(self):
        with self.assertRaises(AssertionError):
            class TestHandler(Handler):
                def match(self, *args, **kwargs):
                    pass

                def parse(self, obj, extras):
                    pass

                def send(self, msg):
                    pass

    def test_handler_class_can_be_created_with_name_attribute(self):
        class TestHandler(Handler):
            name = 'test-handler-name'

            def match(self, *args, **kwargs):
                pass

            def parse(self, obj, extras):
                pass

            def send(self, msg):
                pass

    def test_abstract_handler_creation(self):
        # Just test if this class creation doesn't raise any error
        class AbsTestHandler(Handler):
            """
            This class doesn't implement necessary methods, so it's abstract
            """
            pass

    def test_non_abstract_handler_is_registered_by_its_meta(self):
        assert not MetaHandler.get_handlers()

        class TestHandler(Handler):
            name = 'test-handler-name'

            def match(self, *args, **kwargs):
                pass

            def parse(self, obj, extras):
                pass

            def send(self, msg):
                pass

        assert MetaHandler.get_handlers()
        assert MetaHandler.get_handler_cls('test-handler-name') is not None

    def test_abstract_handler_is_not_registered_by_its_meta(self):
        assert not MetaHandler.get_handlers()

        class TestHandler(Handler):
            pass

        assert not MetaHandler.get_handlers()


class EmailHandlerTestCase(BaseTestCase):

    def _create_test_handler(self):
        class TestHandler(EmailHandler):
            name = 'test'
            subject = 'test'
            template_text = 'tests/emails/test.txt'
            template_html = 'tests/emails/test.html'

            def match(self, *args, **kwargs):
                return True

            def parse(self, *args, **kwargs):
                return MsgCtx(
                    recipients=['test@test.test'],
                    context={}
                )

    def test_email_handler(self):
        self._create_test_handler()
        Msg.new(None, dispatch_now=True)
        self.assertEqual(len(mail.outbox), 1)

    def test_email_handler_not_found(self):
        with self.assertRaises(MissingHandlerException):
            Msg.new(None, dispatch_now=True)

    def test_email_not_sent_until_dispatched(self):
        self._create_test_handler()
        Msg.new(None, dispatch_now=False)

        self.assertEqual(len(mail.outbox), 0)


@override_settings(MSG_SKIP_SEND=True)
class SkipSettingTestCase(BaseTestCase):

    def _create_handler(self):
        class TestHandler(EmailHandler):
            name = 'test'
            subject = 'test'
            template_text = 'tests/emails/test.txt'
            template_html = 'tests/emails/test.html'

            def match(self, *args, **kwargs):
                return True

            def parse(self, *args, **kwargs):
                return MsgCtx(
                    recipients=['test@test.test'],
                    context={}
                )

    def test_email_is_not_send(self):
        self._create_handler()
        Msg.new(None, dispatch_now=True)
        self.assertEqual(len(mail.outbox), 0)

    def test_msg_status_is_done(self):
        self._create_handler()
        msg = Msg.new(None, dispatch_now=True)
        self.assertEqual(msg.status, Msg.Status.DONE.value)
