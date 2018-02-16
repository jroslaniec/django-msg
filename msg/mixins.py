from typing import ClassVar


class TypeMixin:
    type: 'ClassVar'

    class Meta:
        fields = ['type']

    def match(self, *args, **kwargs):
        if not args:
            return False

        return isinstance(args[0], self.type)


class ExactTypeMixin:
    type: 'ClassVar'

    class Meta:
        fields = ['type']

    def match(self, *args, **kwargs):
        if not args:
            return False

        return args[0].__class__ is self.type
