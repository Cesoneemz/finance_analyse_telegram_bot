class NotCorrectMessage(Exception):
    def __init__(self, message: str = "Message not correct"):
        super().__init__(message)