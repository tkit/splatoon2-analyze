__all__ = ['SplatoonException', 'AuthenticationError', 'ValueError']


class SplatoonException(Exception):
    """
    base class
    """
    pass


class ValueError(SplatoonException):

    @property
    def parameter(self):
        return self.args[0]

    @property
    def value(self):
        return self.args[1]

    def __str__(self):
        return '{} {}:{}'.format(self.__class__.__name__, self.parameter, self.value)


class AuthenticationError(SplatoonException):

    @property
    def iksm_session(self):
        return self.args[0]

    def __str__(self):
        return '{} iksm_session:{}'.format(self.__class__.__name__, self.iksm_session)
