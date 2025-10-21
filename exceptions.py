class FullBitmap(Exception):
    def __init__(self, message):
        self.message = message

    def __repr__(self):
        return f'FullBitmap: {self.message}'

class FolderDontExist(Exception):
    def __init__(self, message):
        self.message = message

    def __repr__(self):
        return f'FolderDontExist: {self.message}'

class NotFolderINode(Exception):
    def __init__(self, message):
        self.message = message

    def __repr__(self):
        return f'NotFolderINode: {self.message}'

class FileAlreadyExists(Exception):
    def __init__(self, message):
        self.message = message

    def __repr__(self):
        return f'FileAlreadyExists: {self.message}'

class WrongInodeIndex(Exception):
    def __init__(self, message):
        self.message = message

    def __repr__(self):
        return f'WrongInodeIndex: {self.message}'

class WrongParameters(Exception):
    def __init__(self, message):
        self.message = message

    def __repr__(self):
        return f'WrongParameters: {self.message}'

class NotAcceptableDirName(Exception):
    def __init__(self, message):
        self.message = message

    def __repr__(self):
        return f'NotAcceptableDirName: {self.message}'

class NotAcceptableFileName(Exception):
    def __init__(self, message):
        self.message = message

    def __repr__(self):
        return f'NotAcceptableFileName: {self.message}'

class CantRemove(Exception):
    def __init__(self, message):
        self.message = message

    def __repr__(self):
        return f'CantRemove: {self.message}'

class CantMoveParent(Exception):
    def __init__(self, message):
        self.message = message

    def __repr__(self):
        return f'CantMoveParent: {self.message}'