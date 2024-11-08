import math

def bitmask(bitfield:int, flag:int) -> bool:
    return (bitfield & flag) == flag

def normalizeNum(num:int|float) -> int|float:
    return num / math.sqrt(num*num)

def normalizeArr(arr:list) -> list:
    for i, num in enumerate(arr):
        arr[i] = normalizeNum(num)
    return arr
