import dataclasses


@dataclasses.dataclass()
class Point:
    x: int
    y: int
    z: float


p1 = Point(1, 2, 3)
p2 = Point(1, 2, 'asdf')  # No validation
print(p1)
print(p2)

print(p1 == p2)
