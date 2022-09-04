"""Common calculation of the system"""
import math

# Calculate great circle distance
def gc_distance(long_1, lati_1, long_2, lati_2, math=math):
    ang = math.acos(
        math.cos(math.radians(lati_1))
        * math.cos(math.radians(lati_2))
        * math.cos(math.radians(long_2) - math.radians(long_1))
        + math.sin(math.radians(lati_1)) * math.sin(math.radians(lati_2))
    )
    return 6371 * ang

# Calculaate rate
def rate_cal(dividend, divisor):
    return dividend/divisor