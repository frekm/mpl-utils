class AliasError(Exception):
    def __init__(self, keyword_arg: str, alias: str):
        self.keyword_arg = keyword_arg
        self.alias = alias

    def __str__(self):
        return (
            f"Both '{self.keyword_arg}' and '{self.alias}' have been "
            "provided, but they are aliases"
        )


class InvalidFigureError(Exception):
    def __init__(self, message: str):
        self.message = message

    def __str__(self) -> str:
        return self.message
