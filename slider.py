class Slider:
    def __init__(self, name, min, max) -> None:
        self.label = str(name)
        self.min_value = int(min)
        self.max_value = int(max)
        self.value = int(min)
        self.step = 1
