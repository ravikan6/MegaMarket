
class UnAuthorizedException(Exception):
    def __init__(self, message = "You are not authorized to perform this action"):
        self.message = message
        super().__init__(self.message)

class NotFoundException(Exception):
    def __init__(self, message = "Resource not found"):
        self.message = message
        super().__init__(self.message)

class InvalidModelIdException(Exception):
    def __init__(self, model):
        self.message = f"Invalid {model} id"
        super().__init__(self.message)

class InvalidImageException(Exception):
    def __init__(self, message = "Invalid image input"):
        self.message = message
        super().__init__(self.message)