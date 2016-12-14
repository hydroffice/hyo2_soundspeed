class UserError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return str(self.value)

class FatalUserError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return str(self.value)

class MetadataException(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return str(self.value)

class FormattingException(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return str(self.value)

class DataFileError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return str(self.value)
