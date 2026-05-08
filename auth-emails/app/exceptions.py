class EmailAlreadyRegistered(Exception):
    pass


class InvalidCredentials(Exception):
    pass


class TokenInvalid(Exception):
    pass


class TokenExpired(Exception):
    pass


class AlreadyVerified(Exception):
    pass


class UserNotFound(Exception):
    pass


class NotAuthenticated(Exception):
    pass


class NotVerified(Exception):
    pass
