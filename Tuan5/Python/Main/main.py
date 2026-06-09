#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script: Khởi động ứng dụng (Startup Script)
Mô tả: Script để khởi động giao diện GUI hoặc chương trình test
"""

import sys
import os
from pathlib import Path
import subprocess

# Thêm thư mục parent vào path
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))
sys.path.insert(0, str(parent_dir / "1_Tao_khoa"))
sys.path.insert(0, str(parent_dir / "2_Tao_chu_ky"))
sys.path.insert(0, str(parent_dir / "shared"))
sys.path.insert(0, str(parent_dir / "4_Giao_dien"))

# Đảm bảo đầu ra console hỗ trợ UTF-8 trên Windows
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')


def check_dependencies():
    """Kiểm tra các dependency cần thiết"""
    missing_packages = []
    
    # Kiểm tra python-docx
    try:
        from docx import Document
    except ImportError:
        missing_packages.append('python-docx')
    
    # Kiểm tra reportlab
    try:
        from reportlab.lib.pagesizes import letter
    except ImportError:
        missing_packages.append('reportlab')
    
    if missing_packages:
        print("\nCảnh báo: Một số package không được cài đặt!")
        print("Các package bị thiếu:", ", ".join(missing_packages))
        print("\nChạy lệnh sau để cài đặt:")
        print(f"  pip install {' '.join(missing_packages)}")
        print("\nGhi chú: Các chức năng DOCX/PDF export sẽ không khả dụng.")
        print("Bạn vẫn có thể sử dụng các định dạng JSON và TXT.\n")


def run_gui():
    """Chạy giao diện GUI"""
    try:
        import tkinter as tk
        from main_app import ElGamalSignatureGUI
        
        print("Khởi động giao diện GUI...")
        root = tk.Tk()
        app = ElGamalSignatureGUI(root)
        root.mainloop()
    
    except ImportError as e:
        print(f"Lỗi: Không thể import các module cần thiết: {e}")
        print("Vui lòng kiểm tra cấu hình Python!")
        sys.exit(1)
    
    except Exception as e:
        print(f"Lỗi khi khởi động GUI: {e}")
        sys.exit(1)


def run_tests():
    """Chạy các test"""
    try:
        # Import từ thư mục test
        sys.path.insert(0, str(parent_dir / "test"))
        from test_examples import run_all_tests
        
        print("Chạy các test...")
        run_all_tests()
    
    except ImportError as e:
        print(f"Lỗi: Không thể import các module cần thiết: {e}")
        sys.exit(1)
    
    except Exception as e:
        print(f"Lỗi khi chạy test: {e}")
        sys.exit(1)


def show_menu():
    """Hiển thị menu"""
    print("\n" + "="*60)
    print("HỆ THỐNG CHỮ KÝ SỐ ELGAMAL")
    print("="*60)
    print("\n1. Chạy giao diện GUI (GUI Interface)")
    print("2. Chạy các test (Run Tests)")
    print("3. Hiển thị cấu hình (Show Configuration)")
    print("4. Thoát (Exit)")
    print("\n" + "="*60)


def main():
    """Hàm main"""
    if len(sys.argv) > 1:
        # Chế độ dòng lệnh
        if sys.argv[1] == "--gui":
            check_dependencies()
            run_gui()
        elif sys.argv[1] == "--test":
            run_tests()
        elif sys.argv[1] == "--config":
            from config import print_config
            print_config()
        else:
            print(f"Tùy chọn không hợp lệ: {sys.argv[1]}")
            print("\nCác tùy chọn:")
            print("  --gui     : Chạy giao diện GUI")
            print("  --test    : Chạy các test")
            print("  --config  : Hiển thị cấu hình")
    else:
        # Chế độ interactive
        check_dependencies()
        
        while True:
            show_menu()
            
            choice = input("\nChọn tùy chọn (1-4): ").strip()
            
            if choice == "1":
                run_gui()
                break
            elif choice == "2":
                run_tests()
                input("\nNhấp Enter để tiếp tục...")
            elif choice == "3":
                from config import print_config
                print_config()
                input("\nNhấp Enter để tiếp tục...")
            elif choice == "4":
                print("\nTạm biệt!")
                sys.exit(0)
            else:
                print("Tùy chọn không hợp lệ!")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nĐã hủy bỏi bởi người dùng.")
        sys.exit(0)
    except Exception as e:
        print(f"\nLỗi: {e}")
        sys.exit(1)
