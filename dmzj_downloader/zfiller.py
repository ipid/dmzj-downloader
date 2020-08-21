__all__ = (
    'Zfiller',
)


class Zfiller:

    def __init__(self, collection):
        self.len = len(str(len(collection))) + 1

    def zfill(self, s) -> str:
        return str(s).zfill(self.len)
