"""
Module: Tạo chữ ký số ElGamal
Mô tả: Quản lý việc tạo chữ ký số cho tin nhắn
"""

import sys
import os

# Thêm thư mục parent vào path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shared.hash_function import HashFunction
from importlib import import_module

# Import ElGamal từ thư mục 1_Tao_khoa
elgamal_module = import_module('1_Tao_khoa.elgamal')
ElGamal = elgamal_module.ElGamal


class SignatureManager:
    """Lớp quản lý chữ ký số ElGamal - Phần tạo chữ ký"""
    
    def __init__(self, p, g):
        """
        Khởi tạo với các tham số ElGamal
        
        Args:
            p (int): Số nguyên tố
            g (int): Căn nguyên thủy
        """
        self.p = p
        self.g = g
        self.keys = None
    
    def generate_keys(self, x=None):
        """
        Sinh cặp khóa
        
        Args:
            x (int, optional): Khóa bí mật
            
        Returns:
            dict: Thông tin khóa
        """
        self.keys = ElGamal.generate_keys(self.p, self.g, x)
        return self.keys
    
    def get_public_key(self):
        """
        Lấy khóa công khai
        
        Returns:
            dict: {'p': p, 'g': g, 'y': y}
        """
        if self.keys is None:
            raise ValueError("Chưa sinh khóa. Hãy gọi generate_keys() trước.")
        
        return {
            'p': self.keys['p'],
            'g': self.keys['g'],
            'y': self.keys['y']
        }
    
    def sign_message(self, message, k=None):
        """
        Ký một tin nhắn
        
        Args:
            message (str): Tin nhắn cần ký
            k (int, optional): Số k ngẫu nhiên
            
        Returns:
            dict: {'message': message, 'hash': hash, 'signature': {...}, 'hash_hex': hash_hex}
        """
        if self.keys is None:
            raise ValueError("Chưa sinh khóa. Hãy gọi generate_keys() trước.")
        
        # Kiểm tra tin nhắn
        if not isinstance(message, str):
            raise TypeError("Tin nhắn phải là string")
        
        if not message:
            raise ValueError("Tin nhắn không được trống")
        
        # Tính hash của tin nhắn
        message_hash = HashFunction.sha256_to_int(message, self.p - 1)
        
        # Ký
        signature = ElGamal.sign(
            message_hash,
            self.keys['p'],
            self.keys['g'],
            self.keys['x'],
            k
        )
        
        return {
            'message': message,
            'hash': message_hash,
            'signature': signature,
            'hash_hex': HashFunction.sha256(message)
        }
