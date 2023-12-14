class Exceptions:
    
    class ClientException(Exception):
        pass

    class InvalidAuth(ClientException):

        def __init__(self, message:str="The Auth entered is invalid!"):
            super().__init__(message)

    class NotRegistered(ClientException):

        def __init__(self, message:str="Method input is not registered!"):
            super().__init__(message)

    class InvalidInput(ClientException):

        def __init__(self, message:str="Invalid method input!"):
            super().__init__(message)

    class TooRequests(ClientException):

        def __init__(self, message:str="Too much request! Your account has been suspended."):
            super().__init__(message)