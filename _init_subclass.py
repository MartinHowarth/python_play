class Person:
    height: int

    def __init_subclass__(cls, height=None, **kwargs):
        print(f"__init_subclass__, {cls} {kwargs}")
        cls.height = height


class Male(Person, height=6):
    pass


class Female(Person, height=5):
    pass


print(Male.height)
print(Female.height)
Person.height = 4
print(Male.height)  # Different id, so same as before
