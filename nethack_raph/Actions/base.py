class BaseAction:
    def __init__(self, kernel):
        self.kernel = kernel

    def log(self, message):
        self.kernel().log(message)

    def draw_path(self, path, color=41):
        self.kernel().draw_path(path, color=color)

    @property
    def hero(self):
        return self.kernel().hero

    def can(self, level):
        return False, None

    def after_search(self, targets, path):
        pass

    def execute(self, path):
        raise NotImplementedError
