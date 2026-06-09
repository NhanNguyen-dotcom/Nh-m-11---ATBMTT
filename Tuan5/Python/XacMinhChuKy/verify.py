"""
Module: Xác minh chữ ký số (Signature Verification)
Mô tả: Chuyên xử lý việc xác minh chữ ký và phát hiện các loại sửa đổi
"""

import sys
import json
from pathlib import Path
from enum import Enum

# Add parent directory and subdirectories to path
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))
sys.path.insert(0, str(parent_dir / "1_Tao_khoa"))
sys.path.insert(0, str(parent_dir / "2_Tao_chu_ky"))
sys.path.insert(0, str(parent_dir / "shared"))

from signature import SignatureManager, SignatureChecker
from hash_function import HashFunction
from file_handler import FileHandler


class TamperingType(Enum):
    """Enum các loại sửa đổi"""
    NONE = "none"
    TEXT_MODIFIED = "text_modified"
    SIGNATURE_MODIFIED = "signature_modified"
    BOTH_MODIFIED = "both_modified"
    UNKNOWN = "unknown"


class SignatureVerifier:
    """Lớp chuyên xử lý xác minh chữ ký"""
    
    def __init__(self, p, g, y):
        """
        Khởi tạo bộ xác minh
        
        Args:
            p (int): Số nguyên tố
            g (int): Căn nguyên thủy
            y (int): Khóa công khai
        """
        self.p = p
        self.g = g
        self.y = y
        self.public_key = {'p': p, 'g': g, 'y': y}
        
        # Tạo đối tượng để xác minh (không cần khóa bí mật)
        self.signature_manager = SignatureManager(p, g)
    
    def verify_message(self, message, signature, original_hash=None):
        """
        Xác minh chữ ký của một tin nhắn và phát hiện loại sửa đổi
        
        Args:
            message (str): Tin nhắn cần xác minh
            signature (dict): Chữ ký {'r': r, 's': s}
            original_hash (str, optional): Hash gốc (hex) để so sánh
            
        Returns:
            dict: {
                'valid': bool,
                'message': str,
                'signature': dict,
                'tampering_type': TamperingType,
                'details': str,
                'has_original_hash': bool
            }
        """
        # Xác minh chữ ký cơ bản
        result = self.signature_manager.verify_signature(message, signature, self.public_key)
        
        # Tính hash hiện tại
        current_hash = HashFunction.sha256(message)
        
        # Xác định loại sửa đổi
        tampering_type = self._detect_tampering_type(
            result['valid'],
            current_hash,
            original_hash,
            signature
        )
        
        # Tạo thông điệp chi tiết
        details = self._create_details_message(tampering_type, result['valid'], original_hash)
        
        return {
            'valid': result['valid'],
            'message': message,
            'signature': signature,
            'current_hash': current_hash,
            'original_hash': original_hash,
            'tampering_type': tampering_type,
            'details': details,
            'has_original_hash': original_hash is not None
        }
    
    def verify_with_file(self, message, signature_file_path):
        """
        Xác minh chữ ký bằng file chữ ký lưu trữ
        
        Args:
            message (str): Tin nhắn cần xác minh
            signature_file_path (str): Đường dẫn file chữ ký
            
        Returns:
            dict: Kết quả xác minh
        """
        try:
            # Tải file chữ ký
            file_handler = FileHandler()
            signature_data = file_handler.load_signature(signature_file_path)
            
            # Lấy thông tin
            signature = signature_data.get('signature', {})
            original_hash = signature_data.get('hash_hex')
            
            # Xác minh
            return self.verify_message(message, signature, original_hash)
        
        except Exception as e:
            return {
                'valid': False,
                'message': message,
                'error': str(e),
                'details': f'Lỗi khi tải file chữ ký: {e}'
            }
    
    def _detect_tampering_type(self, signature_valid, current_hash, original_hash, signature):
        """
        Phát hiện loại sửa đổi
        
        Args:
            signature_valid (bool): Chữ ký hợp lệ hay không
            current_hash (str): Hash hiện tại
            original_hash (str): Hash gốc
            signature (dict): Chữ ký
            
        Returns:
            TamperingType: Loại sửa đổi
        """
        # Nếu chữ ký hợp lệ và không có hash gốc
        if signature_valid and original_hash is None:
            return TamperingType.NONE
        
        # Nếu chữ ký hợp lệ nhưng có hash gốc
        if signature_valid and original_hash is not None:
            if current_hash == original_hash:
                return TamperingType.NONE
            else:
                # Hash khác nhưng chữ ký hợp lệ (không thể xảy ra trong trường hợp bình thường)
                return TamperingType.UNKNOWN
        
        # Nếu chữ ký không hợp lệ
        if not signature_valid:
            # Nếu có hash gốc để so sánh
            if original_hash is not None:
                if current_hash == original_hash:
                    # Hash giống nhưng chữ ký sai → chữ ký bị sửa
                    return TamperingType.SIGNATURE_MODIFIED
                else:
                    # Cần kiểm tra xem text hay chữ ký bị sửa
                    # Nếu cả hai thay đổi
                    return TamperingType.BOTH_MODIFIED
            else:
                # Không có hash gốc để so sánh
                return TamperingType.UNKNOWN
        
        return TamperingType.UNKNOWN
    
    def _create_details_message(self, tampering_type, signature_valid, original_hash):
        """
        Tạo thông điệp chi tiết dựa trên loại sửa đổi
        
        Args:
            tampering_type (TamperingType): Loại sửa đổi
            signature_valid (bool): Chữ ký hợp lệ hay không
            original_hash (str): Hash gốc
            
        Returns:
            str: Thông điệp chi tiết
        """
        messages = {
            TamperingType.NONE: "✓ Chữ ký hợp lệ - Tin nhắn toàn vẹn",
            TamperingType.TEXT_MODIFIED: "❌ LỖI: Tin nhắn bị sửa đổi",
            TamperingType.SIGNATURE_MODIFIED: "❌ LỖI: Chữ ký bị sửa đổi (tin nhắn toàn vẹn nhưng chữ ký không khớp)",
            TamperingType.BOTH_MODIFIED: "❌ LỖI: Tin nhắn và chữ ký bị sửa đổi",
            TamperingType.UNKNOWN: "❌ LỖI: Xác minh thất bại\n⚠ Cần tải hash gốc để xác định:\n  • Nếu tin nhắn bị sửa đổi\n  • Nếu chữ ký bị sửa đổi"
        }
        
        return messages.get(tampering_type, "Không xác định loại sửa đổi")
    
    def validate_signature_format(self, signature):
        """
        Kiểm tra định dạng chữ ký
        
        Args:
            signature (dict): Chữ ký {'r': r, 's': s}
            
        Returns:
            dict: {'valid': bool, 'issues': list}
        """
        issues = []
        
        # Kiểm tra cấu trúc
        if not isinstance(signature, dict):
            issues.append("Chữ ký phải là dictionary")
            return {'valid': False, 'issues': issues}
        
        # Kiểm tra r
        if 'r' not in signature:
            issues.append("Thiếu r trong chữ ký")
        elif not isinstance(signature['r'], int):
            issues.append("r phải là số nguyên")
        elif not (0 < signature['r'] < self.p):
            issues.append(f"r phải nằm trong khoảng (0, {self.p})")
        
        # Kiểm tra s
        if 's' not in signature:
            issues.append("Thiếu s trong chữ ký")
        elif not isinstance(signature['s'], int):
            issues.append("s phải là số nguyên")
        elif not (0 < signature['s'] < self.p - 1):
            issues.append(f"s phải nằm trong khoảng (0, {self.p - 1})")
        
        return {
            'valid': len(issues) == 0,
            'issues': issues
        }
    
    def generate_report(self, message, signature, original_hash=None):
        """
        Tạo báo cáo xác minh chi tiết
        
        Args:
            message (str): Tin nhắn
            signature (dict): Chữ ký
            original_hash (str, optional): Hash gốc
            
        Returns:
            str: Báo cáo
        """
        result = self.verify_message(message, signature, original_hash)
        
        report = f"""
{'='*70}
BÁO CÁO XÁC MINH CHỮ KÝ SỐ
{'='*70}

【 THÔNG TIN TIN NHẮN 】
  Nội dung: {message[:50]}...
  Hash hiện tại: {result['current_hash'][:32]}...

【 THÔNG TIN CHỮ KÝ 】
  r = {signature.get('r', 'N/A')}
  s = {signature.get('s', 'N/A')}

【 KẾT QUẢ XÁC MINH 】
  Loại sửa đổi: {result['tampering_type'].value.upper()}
  Kết luận: {result['details']}
  Trạng thái: {'✓ HỢP LỆ' if result['valid'] else '✗ KHÔNG HỢP LỆ'}

{'='*70}
"""
        if original_hash:
            report += f"\n【 HASH GỐC 】\n  {original_hash[:32]}...\n"
        
        return report


if __name__ == "__main__":
    # Ví dụ sử dụng
    p, g, x = 9973, 2, 123
    
    # Tạo chữ ký
    signer = SignatureManager(p, g)
    keys = signer.generate_keys(x)
    message = "Dữ liệu cần ký"
    signed = signer.sign_message(message)
    
    # Xác minh
    verifier = SignatureVerifier(p, g, keys['y'])
    
    print("Test 1: Xác minh tin nhắn gốc")
    result = verifier.verify_message(message, signed['signature'], signed['hash_hex'])
    print(f"Kết quả: {result['details']}")
    print(f"Hợp lệ: {result['valid']}")
    
    print("\nTest 2: Xác minh tin nhắn bị sửa")
    result = verifier.verify_message(message + " (sửa)", signed['signature'], signed['hash_hex'])
    print(f"Kết quả: {result['details']}")
    print(f"Hợp lệ: {result['valid']}")
    
    print("\nTest 3: Xác minh chữ ký bị sửa")
    tampered_sig = {'r': signed['signature']['r'] + 1, 's': signed['signature']['s']}
    result = verifier.verify_message(message, tampered_sig, signed['hash_hex'])
    print(f"Kết quả: {result['details']}")
    print(f"Hợp lệ: {result['valid']}")
