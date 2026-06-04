import hashlib
import random
import math

def mod_inverse(a, m):
    m0, y, x = m, 0, 1
    if m == 1: return 0
    while a > 1:
        q = a // m
        t = m
        m = a % m
        a = t
        t = y
        y = x - q * y
        x = t
    if x < 0: x = x + m0
    return x

def hash_message(message):
    hash_hex = hashlib.sha256(message.encode('utf-8')).hexdigest()
    return int(hash_hex, 16)

def sign_elgamal(message, p, a, x):
    h = hash_message(message)
    while True:
        k = random.randint(2, p - 2)
        if math.gcd(k, p - 1) == 1:
            break
    r = pow(a, k, p)
    k_inv = mod_inverse(k, p - 1)
    s = (k_inv * (h - x * r)) % (p - 1)
    return f"{r},{s}"

def verify_elgamal(message, signature_str, p, a, y):
    try:
        r_str, s_str = signature_str.split(',')
        r, s = int(r_str), int(s_str)
        if not (0 < r < p) or not (0 < s < p - 1):
            return False
        h = hash_message(message)
        v1 = (pow(y, r, p) * pow(r, s, p)) % p
        v2 = pow(a, h, p)
        return v1 == v2
    except:
        return False