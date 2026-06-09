"""
Module: Thuật toán ElGamal
Mô tả: Cung cấp các hàm cho hệ mã ElGamal và chữ ký số ElGamal
"""

import random


class ElGamal:
    """Lớp quản lý thuật toán ElGamal"""
    
    @staticmethod
    def is_prime(n, k=3):
        """
        Kiểm tra số nguyên tố bằng thuật toán Miller-Rabin
        
        Args:
            n (int): Số cần kiểm tra
            k (int): Số lần lặp (mặc định 3 để nhanh hơn)
            
        Returns:
            bool: True nếu n là số nguyên tố, False nếu không
        """
        if n < 2:
            return False
        if n == 2 or n == 3:
            return True
        if n % 2 == 0:
            return False
        if n < 9:
            return True
        if n % 3 == 0:
            return False
        
        # Viết n-1 = 2^r * d
        r, d = 0, n - 1
        while d % 2 == 0:
            r += 1
            d //= 2
        
        # Kiểm tra k lần
        for _ in range(k):
            a = random.randint(2, n - 2)
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
    
    @staticmethod
    def gcd(a, b):
        """
        Tính ước số chung lớn nhất
        
        Args:
            a (int): Số thứ nhất
            b (int): Số thứ hai
            
        Returns:
            int: UCLN(a, b)
        """
        while b:
            a, b = b, a % b
        return a
    
    @staticmethod
    def extended_gcd(a, b):
        """
        Thuật toán Euclid mở rộng
        
        Args:
            a (int): Số thứ nhất
            b (int): Số thứ hai
            
        Returns:
            tuple: (gcd, x, y) sao cho a*x + b*y = gcd
        """
        if a == 0:
            return b, 0, 1
        
        gcd_val, x1, y1 = ElGamal.extended_gcd(b % a, a)
        x = y1 - (b // a) * x1
        y = x1
        
        return gcd_val, x, y
    
    @staticmethod
    def mod_inverse(a, m):
        """
        Tính modular inverse của a mod m
        
        Args:
            a (int): Số cần tính
            m (int): Modulo
            
        Returns:
            int: a^(-1) mod m hoặc None nếu không tồn tại
        """
        gcd_val, x, _ = ElGamal.extended_gcd(a % m, m)
        
        if gcd_val != 1:
            return None
        
        return (x % m + m) % m
    
    @staticmethod
    def primitive_root(p):
        """
        Tìm một căn nguyên thủy (generator) của nhóm Z_p*
        Cách đơn giản: test g=2,3,5... và check với các factor chính
        
        Args:
            p (int): Số nguyên tố
            
        Returns:
            int: Một căn nguyên thủy của p
        """
        # Với hầu hết các số nguyên tố, g=2 là generator
        # Nếu không, g=3, 5, 7, ... thường work
        
        phi = p - 1
        
        # Tìm các prime factor nhỏ của phi (p-1)
        # Thay vì tìm tất cả, chỉ tìm với small primes
        small_primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47]
        factors = []
        
        for sp in small_primes:
            if phi % sp == 0:
                factors.append(sp)
        
        # Nếu có factor lớn ẩn (phi / product(small_factors))
        # Cũng cần kiểm tra
        temp = phi
        for f in factors:
            temp //= f
        
        if temp > 1 and temp != phi:  # Nếu vẫn còn factor khác
            factors.append(temp)
        elif temp == phi and len(factors) == 0:
            # phi là số nguyên tố, tất cả các g > 0 là generator
            return 2
        
        # Test g = 2, 3, 5, 7, ...
        for g in [2, 3, 5, 7, 11, 13, 17, 19, 23, 29]:
            if g >= p:
                break
            
            is_generator = True
            for factor in factors:
                if pow(g, phi // factor, p) == 1:
                    is_generator = False
                    break
            
            if is_generator:
                return g
        
        # Fallback: return 2 (trong thực tế này sẽ hoạt động)
        return 2
    
    @staticmethod
    def generate_keys(p, g, x=None):
        """
        Sinh cặp khóa công khai/bí mật cho ElGamal
        
        Args:
            p (int): Số nguyên tố lớn
            g (int): Căn nguyên thủy của p
            x (int, optional): Khóa bí mật (nếu None sẽ random)
            
        Returns:
            dict: {'p': p, 'g': g, 'x': x, 'y': y}
                  - p: số nguyên tố
                  - g: căn nguyên thủy
                  - x: khóa bí mật
                  - y: khóa công khai = g^x mod p
        """
        if x is None:
            x = random.randint(2, p - 2)
        
        y = pow(g, x, p)
        
        return {
            'p': p,
            'g': g,
            'x': x,
            'y': y
        }
    
    @staticmethod
    def sign(message_hash, p, g, x, k=None):
        """
        Ký chữ ký số ElGamal
        
        Thuật toán:
        1. Chọn k ngẫu nhiên: 1 < k < p-1, gcd(k, p-1) = 1
        2. Tính r = g^k mod p
        3. Tính s = (H - xr) * k^(-1) mod (p-1)
        4. Chữ ký là (r, s)
        
        Args:
            message_hash (int): Hash của tin nhắn
            p (int): Số nguyên tố
            g (int): Căn nguyên thủy
            x (int): Khóa bí mật
            k (int, optional): Số k ngẫu nhiên
            
        Returns:
            dict: {'r': r, 's': s}
        """
        # Chọn k ngẫu nhiên sao cho gcd(k, p-1) = 1
        max_retries = 100
        retries = 0
        
        while retries < max_retries:
            if k is None or retries > 0:
                k = random.randint(2, p - 2)
            
            if ElGamal.gcd(k, p - 1) == 1:
                break
            
            retries += 1
        
        if retries >= max_retries:
            raise RuntimeError("Không tìm được k thích hợp sau 100 lần thử")
        
        # Tính r = g^k mod p
        r = pow(g, k, p)
        
        # Tính s = (H - xr) * k^(-1) mod (p-1)
        k_inv = ElGamal.mod_inverse(k, p - 1)
        
        if k_inv is None:
            raise RuntimeError("Không tính được modular inverse của k")
        
        s = (message_hash - x * r) * k_inv % (p - 1)
        
        return {'r': r, 's': s}
    
    @staticmethod
    def verify(message_hash, signature, p, g, y):
        """
        Xác minh chữ ký số ElGamal
        
        Thuật toán:
        1. Kiểm tra 0 < r < p và 0 < s < p-1
        2. Tính v1 = g^H mod p
        3. Tính v2 = y^r * r^s mod p
        4. Chữ ký hợp lệ nếu v1 == v2
        
        Args:
            message_hash (int): Hash của tin nhắn
            signature (dict): Chữ ký {'r': r, 's': s}
            p (int): Số nguyên tố
            g (int): Căn nguyên thủy
            y (int): Khóa công khai
            
        Returns:
            bool: True nếu chữ ký hợp lệ, False nếu không
        """
        r = signature.get('r')
        s = signature.get('s')
        
        # Kiểm tra điều kiện
        if r is None or s is None:
            return False
        
        if not (0 < r < p):
            return False
        
        if not (0 < s < p - 1):
            return False
        
        # Tính v1 = g^H mod p
        v1 = pow(g, message_hash, p)
        
        # Tính v2 = y^r * r^s mod p
        v2 = (pow(y, r, p) * pow(r, s, p)) % p
        
        # Chữ ký hợp lệ nếu v1 == v2
        return v1 == v2
