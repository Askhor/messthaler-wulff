class defaultlist[T]:
    """Essentially just a rewrite of defaultdict, specialized for consecutive int indices"""

    def __init__(self, default: T):
        self.default: T = default
        self.values: list[T] = list()

    def _ensure_capacity(self, key: int):
        l = self.values
        while len(l) <= key:
            l.append(self.default)

    def __len__(self):
        return len(self.values)

    def __getitem__(self, key: int) -> T:
        self._ensure_capacity(key)
        return self.values[key]

    def __setitem__(self, key: int, value: T) -> None:
        self._ensure_capacity(key)
        self.values[key] = value

    def __str__(self):
        return str(self.values)