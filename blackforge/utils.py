import math

def bitmask(bitfield:int, flag:int) -> bool:
    return (bitfield & flag) == flag

def normalizeNum(num:int|float) -> int|float:
    return num / math.sqrt(num*num)

def normalizeArr(arr:list) -> list:
    for i, num in enumerate(arr):
        arr[i] = normalizeNum(num)
    return arr

def distTo(point1:list, point2:list) -> list[float]:
    return [
        point1[0] - point2[0],
        point1[1] - point2[1]
    ]

def distToNorm(point1:list, point2:list) -> list[int]:
    return [
        normalizeNum(point1[0] - point2[0] + 0.001),
        normalizeNum(point1[1] - point2[1] + 0.001)
    ]
