from __future__ import annotations
from math import floor, ceil

from typing import TypeVar, Generic, Optional
from numpy import iterable


T = TypeVar('T')
T1 = TypeVar('T1')
class Vec(Generic[T]):
    def __init__(self, X: T, Y: T):
        self.X = X
        self.Y = Y

    def tp(self) -> tuple[T, T]:
        return (self.X, self.Y)

    def __iter__(self):
        return VecIterator(self)

    def __repr__(self) -> str:
        return f"Vec({self.X}, {self.Y})"
    
    def __getitem__(self, idx: int) -> T:
        if idx == 0:
            return self.X
        elif idx == 1:
            return self.Y
        else:
            raise IndexError(f"[Vec] Can only address indices 0 and 1; {idx} is out of range")
    
    def __setitem__(self, idx: int, val: T):
        if idx == 0:
            self.X = val
        elif idx == 1:
            self.Y = val
        else:
            raise IndexError(f"[Vec] Can only address indices 0 and 1; {idx} is out of range")

    def __abs__(self) -> Vec[T]:
        return Vec(abs(self.X), abs(self.Y))

    # Comparison operators

    def __eq__(self, v) -> bool:
        if isinstance(v, Vec):
            return self.X == v.X and self.Y == v.Y
        else:
            return False

    def __lt__(self, v) -> bool:
        if isinstance(v, Vec):
            return self.X < v.X and self.Y < v.Y
        else:
            return self.X < v and self.Y < v

    def __le__(self, v) -> bool:
        if isinstance(v, Vec):
            return self.X <= v.X and self.Y <= v.Y
        else:
            return self.X <= v and self.Y <= v

    def __gt__(self, v) -> bool:
        if isinstance(v, Vec):
            return self.X > v.X and self.Y > v.Y
        else:
            return self.X > v and self.Y > v

    def __ge__(self, v) -> bool:
        if isinstance(v, Vec):
            return self.X >= v.X and self.Y >= v.Y
        else:
            return self.X >= v and self.Y >= v

    # Arithmetic operators

    def __add__(self, v) -> Vec:
        if isinstance(v, Vec):
            return Vec(self.X + v.X, self.Y + v.Y)
        else:
            return Vec(self.X + v, self.Y + v)

    def __sub__(self, v) -> Vec:
        if isinstance(v, Vec):
            return Vec(self.X - v.X, self.Y - v.Y)
        else:
            return Vec(self.X - v, self.Y - v)
    
    def __mul__(self, v) -> Vec:
        if isinstance(v, Vec):
            return Vec(self.X * v.X, self.Y * v.Y)
        else:
            return Vec(self.X * v, self.Y * v)

    def __truediv__(self, v) -> Vec:
        if isinstance(v, Vec):
            return Vec(self.X / v.X, self.Y / v.Y)
        else:
            return Vec(self.X / v, self.Y / v)
    
    def __floordiv__(self, v) -> Vec:
        if isinstance(v, Vec):
            return Vec(self.X // v.X, self.Y // v.Y)
        else:
            return Vec(self.X // v, self.Y // v)

    # Other helpful functions

    def in_rect(self, corner_1: Vec, corner_2: Vec) -> bool:
        min, max = Vec.minmax(corner_1, corner_2)
        return self >= min and self <= max

    def floor(self) -> Vec[T]:
        return Vec(floor(self.X), floor(self.Y))

    def ceil(self) -> Vec[T]:
        return Vec(ceil(self.X), ceil(self.Y))

    def bound(self, min: Optional[T] = None, max: Optional[T] = None) -> Vec[T]:
        ret = self
        if min is not None:
            ret = ret.bound_min(min)
        if max is not None:
            ret = ret.bound_max(max)
        return ret

    def bound_min(self, min: T) -> Vec[T]:
        if type(min) == Vec:
            return Vec(max(self.X, min.X), max(self.Y, min.Y))
        else:
            return Vec(max(self.X, min), max(self.Y, min))

    def bound_max(self, max: T) -> Vec[T]:
        if type(max) == Vec:
            return Vec(min(self.X, max.X), min(self.Y, max.Y))
        else:
            return Vec(min(self.X, max), min(self.Y, max))

    def min(self) -> T:
        if self.X <= self.Y:
            return self.X
        else:
            return self.Y
    
    def max(self) -> T:
        if self.X < self.Y:
            return self.Y
        else:
            return self.X
    
    def astype(self, t: type[T1]) -> Vec[T1]:
        return Vec(t(self.X), t(self.Y))

    def minmax(vec1: Vec[T], vec2: Vec[T]) -> tuple[Vec[T], Vec[T]]:
        return (Vec(min(vec1.X, vec2.X), min(vec1.Y, vec2.Y)),
                Vec(max(vec1.X, vec2.X), max(vec1.Y, vec2.Y)))


class VecIterator(Generic[T]):
    def __init__(self, v: Vec[T]):
        self.v = v
        self.iter = -1
    
    def __next__(self) -> T:
        self.iter += 1

        if self.iter == 0:
            return self.v.X
        elif self.iter == 1:
            return self.v.Y
        else:
            raise StopIteration


class VecRange(Generic[T]):
    def __init__(self, start: Vec[T], dvec: Vec[T], max_iters: int):
        self.pos = start
        self.dvec = dvec
        self.max_iters = max_iters
        self.iter = 0

    def __iter__(self) -> VecRangeIterator[T]:
        return VecRangeIterator(self)


class VecRangeIterator(Generic[T]):
    def __init__(self, range: VecRange[T]):
        self.range = range

    def __next__(self) -> Vec[T]:
        if self.range.iter >= self.range.max_iters:
            raise StopIteration

        ret = self.range.pos
        self.range.pos += self.range.dvec
        self.range.iter += 1
        return ret
