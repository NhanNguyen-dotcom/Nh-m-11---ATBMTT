"""
thuattoanElgamal.py

Ví dụ quy tắc và thuật toán cho chữ ký số ElGamal.
File này chỉ chứa phần toán học + mã hóa, dùng làm minh họa.
"""

import hashlib
import random
import math
from dataclasses import dataclass
from typing import Tuple, Dict


def miller_rabin(n: int, k: int = 12) -> bool:
    if n < 2:
        return False
    small_primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31]
    if n in small_primes:
        return True
    if any(n % p == 0 for p in small_primes):
        return False

    r, d = 0, n - 1
    while d % 2 == 0:
        r += 1
        d //= 2

    for _ in range(k):
        a = random.randrange(2, n - 1)
        x = pow(a, d, n)
        if x == 1 or x == n - 1:
            continue
        for _ in range(r - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                break
        else:
            return False
    return True


def gen_prime(bits: int) -> int:
    while True:
        candidate = random.getrandbits(bits)
        candidate |= (1 << (bits - 1)) | 1
        if miller_rabin(candidate):
            return candidate


def ext_gcd(a: int, b: int) -> Tuple[int, int, int]:
    if a == 0:
        return b, 0, 1
    g, x1, y1 = ext_gcd(b % a, a)
    return g, y1 - (b // a) * x1, x1


def mod_inv(a: int, m: int) -> int:
    g, x, _ = ext_gcd(a % m, m)
    if g != 1:
        raise ValueError(f"Không tồn tại nghịch đảo modular của {a} mod {m}")
    return x % m


def prime_factors(n: int) -> set:
    factors = set()
    d = 2
    while d * d <= n:
        while n % d == 0:
            factors.add(d)
            n //= d
        d += 1 if d == 2 else 2
    if n > 1:
        factors.add(n)
    return factors


def find_generator(p: int) -> int:
    phi = p - 1
    factors = prime_factors(phi)
    for _ in range(2000):
        g = random.randrange(2, p - 1)
        if all(pow(g, phi // q, p) != 1 for q in factors):
            return g
    raise RuntimeError('Không tìm được generator phù hợp')


def hash_text(text: str) -> Tuple[int, str]:
    digest = hashlib.sha512(text.encode('utf-8')).hexdigest()
    return int(digest, 16), digest


def hash_file(path: str, chunk_size: int = 65536) -> Tuple[int, str]:
    h = hashlib.sha512()
    with open(path, 'rb') as f:
        while True:
            data = f.read(chunk_size)
            if not data:
                break
            h.update(data)
    digest = h.hexdigest()
    return int(digest, 16), digest


@dataclass
class KeyPair:
    p: int
    g: int
    y: int
    x: int

    @classmethod
    def generate(cls, bits: int = 256):
        p = gen_prime(bits)
        g = find_generator(p)
        x = random.randrange(2, p - 1)
        y = pow(g, x, p)
        return cls(p=p, g=g, y=y, x=x)

    def public(self) -> Dict[str, int]:
        return {'p': self.p, 'g': self.g, 'y': self.y}


def sign(message: str, keypair: KeyPair) -> Dict[str, int]:
    h_int, h_hex = hash_text(message)
    p, g, x = keypair.p, keypair.g, keypair.x
    h_mod = h_int % (p - 1) or 1

    while True:
        k = random.randrange(2, p - 1)
        if math.gcd(k, p - 1) != 1:
            continue
        r = pow(g, k, p)
        if r == 0:
            continue
        k_inv = mod_inv(k, p - 1)
        s = (k_inv * (h_mod - x * r)) % (p - 1)
        if s != 0:
            return {'r': r, 's': s, 'hash': h_hex}


def verify(message: str, signature: Dict[str, int], public_key: Dict[str, int]) -> bool:
    p = public_key['p']
    g = public_key['g']
    y = public_key['y']
    r = signature['r']
    s = signature['s']

    if not (1 <= r <= p - 1) or not (0 <= s <= p - 2):
        return False

    h_int, _ = hash_text(message)
    h_mod = h_int % (p - 1) or 1
    left = pow(g, h_mod, p)
    right = (pow(y, r, p) * pow(r, s, p)) % p
    return left == right


def demo():
    print('==== Demo ElGamal Digital Signature ====')
    keypair = KeyPair.generate(bits=256)
    print('Khóa công khai:')
    print(f'  p = {keypair.p}')
    print(f'  g = {keypair.g}')
    print(f'  y = {keypair.y}')
    print('Khóa bí mật:')
    print(f'  x = {keypair.x}\n')

    message = 'Đây là văn bản thử nghiệm cho chữ ký ElGamal.'
    print('Văn bản cần ký:')
    print(f'  {message}\n')

    signature = sign(message, keypair)
    print('Chữ ký tạo được:')
    print(f'  r = {signature["r"]}')
    print(f'  s = {signature["s"]}')
    print(f'  hash = {signature["hash"][:64]}...\n')

    valid = verify(message, signature, keypair.public())
    print('Xác minh chữ ký ban đầu:', 'Hợp lệ' if valid else 'Không hợp lệ')

    print('\nGiả mạo văn bản...')
    tampered = message + ' Sửa đổi.'
    valid = verify(tampered, signature, keypair.public())
    print('Xác minh văn bản giả mạo:', 'Hợp lệ' if valid else 'Không hợp lệ')

    print('\nGiả mạo chữ ký...')
    bad_signature = {'r': signature['r'] + 1, 's': signature['s'], 'hash': signature['hash']}
    valid = verify(message, bad_signature, keypair.public())
    print('Xác minh chữ ký giả mạo:', 'Hợp lệ' if valid else 'Không hợp lệ')


if __name__ == '__main__':
    demo()
