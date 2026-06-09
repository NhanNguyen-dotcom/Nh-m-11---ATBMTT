"""
Module: Ứng dụng giao diện (GUI Application)
Mô tả: Giao diện người dùng cho hệ thống chữ ký số ElGamal
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import os
import json
import sys
from pathlib import Path

# Add parent directory and subdirectories to path for imports
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))
sys.path.insert(0, str(parent_dir / "1_Tao_khoa"))
sys.path.insert(0, str(parent_dir / "2_Tao_chu_ky"))
sys.path.insert(0, str(parent_dir / "shared"))

from elgamal import ElGamal
from signature import SignatureManager, SignatureChecker
from file_handler import FileHandler, BackupManager
from hash_function import HashFunction


class ElGamalSignatureGUI:
    """Lớp giao diện ứng dụng ElGamal"""
    
    def __init__(self, root):
        """
        Khởi tạo giao diện
        
        Args:
            root: Cửa sổ chính tkinter
        """
        self.root = root
        self.root.title("Hệ thống chữ ký số ElGamal")
        self.root.geometry("1400x800")
        
        # Tham số ElGamal
        self.p = None
        self.g = None
        self.sig_manager = None
        self.public_key = None
        self.skip_prime_validation = False  # Flag để bỏ qua kiểm tra nguyên tố cho khóa tự động sinh
        
        # Tạo giao diện
        self.create_widgets()
    
    def create_widgets(self):
        """Tạo các widget giao diện"""
        # Style
        style = ttk.Style()
        style.theme_use('clam')
        
        # Notebook (Tab)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Tab 1: Khóa
        self.tab_keys = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_keys, text="1. Sinh khóa")
        self.create_key_tab()
        
        # Tab 2: Ký
        self.tab_sign = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_sign, text="2. Tạo chữ ký")
        self.create_sign_tab()
        
        # Tab 3: Xác minh
        self.tab_verify = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_verify, text="3. Xác minh chữ ký")
        self.create_verify_tab()
    
    def create_key_tab(self):
        """Tạo tab Sinh khóa"""
        # Frame 1: Nhập tham số
        frame_input = ttk.LabelFrame(self.tab_keys, text="Nhập tham số ElGamal", padding=10)
        frame_input.pack(fill=tk.BOTH, expand=False, padx=5, pady=5)
        
        # Hàng 1: p và q
        ttk.Label(frame_input, text="p (số nguyên tố):").grid(row=0, column=0, sticky=tk.W)
        self.entry_p = ttk.Entry(frame_input, width=40)
        self.entry_p.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(frame_input, text="x (khóa bí mật):").grid(row=0, column=2, sticky=tk.W)
        self.entry_q = ttk.Entry(frame_input, width=40)
        self.entry_q.grid(row=0, column=3, padx=5, pady=5)
        
        # Hàng 2: g và y
        ttk.Label(frame_input, text="g (căn nguyên thủy):").grid(row=1, column=0, sticky=tk.W)
        self.entry_g = ttk.Entry(frame_input, width=40)
        self.entry_g.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(frame_input, text="y (khóa công khai):").grid(row=1, column=2, sticky=tk.W)
        self.entry_y = ttk.Entry(frame_input, width=40)
        self.entry_y.grid(row=1, column=3, padx=5, pady=5)
        
        # Nút tạo khóa
        btn_frame = ttk.Frame(frame_input)
        btn_frame.grid(row=2, column=0, columnspan=4, pady=10)
        
        ttk.Button(btn_frame, text="Tạo khóa", command=self.generate_keys).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Sinh khóa tự động", command=self.auto_generate_keys).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Lưu khóa", command=self.save_keys).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Tải khóa", command=self.load_keys).pack(side=tk.LEFT, padx=5)
        
        # Frame 2: Hiển thị khóa
        frame_display = ttk.LabelFrame(self.tab_keys, text="Thông tin khóa", padding=10)
        frame_display.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.text_keys = scrolledtext.ScrolledText(frame_display, height=20, width=100, font=("Courier New", 10))
        self.text_keys.pack(fill=tk.BOTH, expand=True)
    
    def create_sign_tab(self):
        """Tạo tab Tạo chữ ký"""
        # Frame 1: Nhập dữ liệu cần ký
        frame_input = ttk.LabelFrame(self.tab_sign, text="Nhập dữ liệu cần ký", padding=10)
        frame_input.pack(fill=tk.BOTH, expand=False, padx=5, pady=5)
        
        ttk.Label(frame_input, text="Tạo chữ kí số:").pack(anchor=tk.W)
        
        self.text_message = scrolledtext.ScrolledText(frame_input, height=6, width=100, font=("Courier New", 10))
        self.text_message.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        btn_frame = ttk.Frame(frame_input)
        btn_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(btn_frame, text="Tạo chữ ký", command=self.create_signature).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Xóa", command=lambda: self.text_message.delete("1.0", tk.END)).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Lưu dữ liệu", command=self.save_message).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Tải dữ liệu", command=self.load_message).pack(side=tk.LEFT, padx=5)
        
        # Frame 2: Hiển thị chữ ký
        frame_display = ttk.LabelFrame(self.tab_sign, text="Chữ kí số là:", padding=10)
        frame_display.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.text_signature = scrolledtext.ScrolledText(frame_display, height=15, width=100, font=("Courier New", 10))
        self.text_signature.pack(fill=tk.BOTH, expand=True)
        
        btn_frame2 = ttk.Frame(frame_display)
        btn_frame2.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(btn_frame2, text="Lưu chữ ký", command=self.save_signature).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame2, text="Sao chép chữ ký", command=self.copy_signature).pack(side=tk.LEFT, padx=5)
        
        # Frame 3: Lưu hash
        frame_hash = ttk.LabelFrame(self.tab_sign, text="Lưu hash SHA-256", padding=10)
        frame_hash.pack(fill=tk.BOTH, expand=False, padx=5, pady=5)
        
        self.text_hash_display = scrolledtext.ScrolledText(frame_hash, height=3, width=100, font=("Courier New", 10))
        self.text_hash_display.pack(fill=tk.X, padx=5, pady=5)
        
        btn_frame3 = ttk.Frame(frame_hash)
        btn_frame3.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(btn_frame3, text="Lưu hash", command=self.save_hash).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame3, text="Copy hash", command=self.copy_hash).pack(side=tk.LEFT, padx=5)
    
    def create_verify_tab(self):
        """Tạo tab Xác minh chữ ký"""
        # Frame 1: Nhập dữ liệu
        frame_input = ttk.LabelFrame(self.tab_verify, text="Xác nhận chữ kí số", padding=10)
        frame_input.pack(fill=tk.BOTH, expand=False, padx=5, pady=5)
        
        # Dữ liệu cần ký
        ttk.Label(frame_input, text="Dữ liệu cần ký:").pack(anchor=tk.W)
        self.text_verify_message = scrolledtext.ScrolledText(frame_input, height=3, width=100, font=("Courier New", 10))
        self.text_verify_message.pack(fill=tk.X, padx=5, pady=5)
        
        # Chữ ký
        ttk.Label(frame_input, text="Chữ ký (định dạng JSON):").pack(anchor=tk.W)
        self.text_verify_signature = scrolledtext.ScrolledText(frame_input, height=3, width=100, font=("Courier New", 10))
        self.text_verify_signature.pack(fill=tk.X, padx=5, pady=5)
        
        # Hash gốc (tùy chọn)
        ttk.Label(frame_input, text="Hash SHA-256 gốc (tùy chọn - để xác định chính xác loại sửa đổi):").pack(anchor=tk.W)
        self.text_verify_original_hash = scrolledtext.ScrolledText(frame_input, height=2, width=100, font=("Courier New", 10))
        self.text_verify_original_hash.pack(fill=tk.X, padx=5, pady=5)
        
        btn_frame = ttk.Frame(frame_input)
        btn_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(btn_frame, text="Xác minh", command=self.verify_signature).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Tải dữ liệu", command=self.load_message_for_verify).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Tải chữ ký", command=self.load_signature_for_verify).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Tải hash", command=self.load_hash_for_verify).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Xóa", command=self.clear_verify_fields).pack(side=tk.LEFT, padx=5)
        
        # Frame 2: Kết quả
        frame_result = ttk.LabelFrame(self.tab_verify, text="Kết quả xác minh", padding=10)
        frame_result.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.text_verify_result = scrolledtext.ScrolledText(frame_result, height=15, width=100, font=("Courier New", 10))
        self.text_verify_result.pack(fill=tk.BOTH, expand=True)
        
        ttk.Button(frame_result, text="Lưu báo cáo", command=self.save_verification_report).pack(fill=tk.X, padx=5, pady=5)

    
    def generate_keys(self):
        """Sinh cặp khóa"""
        try:
            self.p = int(self.entry_p.get())
            self.g = int(self.entry_g.get())
            x = int(self.entry_q.get())
            y = int(self.entry_y.get())
            
            # Kiểm tra giá trị
            if self.p <= 1:
                messagebox.showerror("Lỗi", "p phải > 1")
                return
            
            # Kiểm tra p có phải số nguyên tố không (bỏ qua nếu là khóa tự động sinh)
            if not self.skip_prime_validation:
                if not ElGamal.is_prime(self.p):
                    messagebox.showerror("Lỗi", f"p = {self.p} không phải số nguyên tố!\n\nVui lòng nhập một số nguyên tố khác.")
                    return
            else:
                self.skip_prime_validation = False  # Reset flag
            
            if self.g <= 0 or self.g >= self.p:
                messagebox.showerror("Lỗi", "g phải trong khoảng (0, p)")
                return
            
            if x <= 0 or x >= self.p:
                messagebox.showerror("Lỗi", "x phải trong khoảng (0, p)")
                return
            
            # Kiểm tra y = g^x mod p
            y_calc = pow(self.g, x, self.p)
            if y != y_calc:
                result = messagebox.askyesno(
                    "Cảnh báo",
                    f"y không bằng g^x mod p\n" +
                    f"g^x mod p = {y_calc}\n" +
                    f"Bạn nhập y = {y}\n\n" +
                    f"Sử dụng giá trị tính toán?"
                )
                if result:
                    self.entry_y.delete(0, tk.END)
                    self.entry_y.insert(0, str(y_calc))
                    y = y_calc
                else:
                    return
            
            # Sinh khóa
            self.sig_manager = SignatureManager(self.p, self.g)
            keys = self.sig_manager.generate_keys(x)
            
            self.public_key = self.sig_manager.get_public_key()
            
            # Hiển thị
            self.display_keys(keys)
            
            messagebox.showinfo("Thành công", "Đã sinh khóa thành công!")
        
        except ValueError:
            messagebox.showerror("Lỗi", "Nhập giá trị hợp lệ!")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi: {str(e)}")
    
    def display_keys(self, keys):
        """Hiển thị khóa"""
        self.text_keys.delete("1.0", tk.END)
        
        info = f"""
╔═══════════════════════════════════════════════════════════╗
║          THÔNG TIN KHÓA ELGAMAL                           ║
╚═══════════════════════════════════════════════════════════╝

【 THAM SỐ CHUNG 】
  • Số nguyên tố p:        {keys['p']}
  • Căn nguyên thủy g:     {keys['g']}

【 KHÓA BÍ MẬT (PRIVATE KEY) 】
  • x (khóa bí mật):       {keys['x']}
  
  ⚠️  CẢNH BÁO: Giữ bí mật khóa x!

【 KHÓA CÔNG KHAI (PUBLIC KEY) 】
  • y = g^x mod p:         {keys['y']}
  
  ℹ️  Khóa công khai có thể chia sẻ tự do

【 KIỂM CHỨNG 】
  • g^x mod p = {pow(keys['g'], keys['x'], keys['p'])} ✓

"""
        
        self.text_keys.insert(tk.END, info)
    
    def generate_large_prime(self, bit_length=256):
        """
        Sinh một số nguyên tố lớn có kích thước bit_length
        
        Args:
            bit_length (int): Kích thước bit của số nguyên tố
            
        Returns:
            int: Số nguyên tố lớn
        """
        import random
        
        # Nếu bit_length nhỏ, sinh số trong khoảng nhỏ
        if bit_length <= 14:  # 14 bit = 16384, nên 4 chữ số là 1000-9999
            # Sinh số nguyên tố từ 1000-9999
            while True:
                num = random.randint(1000, 9999)
                if ElGamal.is_prime(num):
                    return num
        
        # Với số lớn hơn
        while True:
            # Sinh một số ngẫu nhiên có kích thước bit_length
            num = random.getrandbits(bit_length)
            
            # Đảm bảo bit cao nhất là 1 (đảm bảo đúng kích thước)
            num |= (1 << (bit_length - 1)) | 1
            
            # Kiểm tra tính nguyên tố (sử dụng k=3 mặc định)
            if ElGamal.is_prime(num):
                return num
    
    def auto_generate_keys(self):
        """Sinh khóa tự động"""
        try:
            # Tạo cửa sổ dialog để chọn kích thước khoá
            dialog = tk.Toplevel(self.root)
            dialog.title("Sinh khóa tự động")
            dialog.geometry("500x380")
            dialog.resizable(False, False)
            
            # Căn giữa cửa sổ
            dialog.transient(self.root)
            dialog.grab_set()
            
            # Frame tiêu đề
            title_label = ttk.Label(dialog, text="Chọn kích thước số nguyên tố p (bit):", 
                                   font=("Arial", 11, "bold"))
            title_label.pack(pady=10)
            
            # Frame chọn kích thước
            frame_size = ttk.Frame(dialog)
            frame_size.pack(pady=10, padx=20)
            
            # Các tùy chọn kích thước
            size_var = tk.StringVar(value="14")
            
            ttk.Radiobutton(frame_size, text="🔹 4 chữ số (1000-9999 - MẶC ĐỊNH)", 
                           variable=size_var, value="14").pack(anchor=tk.W, pady=5)
            ttk.Radiobutton(frame_size, text="⚡ 64 bit (siêu nhanh - demo)", 
                           variable=size_var, value="64").pack(anchor=tk.W, pady=5)
            ttk.Radiobutton(frame_size, text="⚡ 80 bit (rất nhanh - demo)", 
                           variable=size_var, value="80").pack(anchor=tk.W, pady=5)
            ttk.Radiobutton(frame_size, text="⚡ 128 bit (nhanh - demo)", 
                           variable=size_var, value="128").pack(anchor=tk.W, pady=5)
            ttk.Radiobutton(frame_size, text="🚀 256 bit (nhanh - an toàn)", 
                           variable=size_var, value="256").pack(anchor=tk.W, pady=5)
            ttk.Radiobutton(frame_size, text="🔐 512 bit (trung bình)", 
                           variable=size_var, value="512").pack(anchor=tk.W, pady=5)
            ttk.Radiobutton(frame_size, text="🔐 1024 bit (lớn - rất an toàn)", 
                           variable=size_var, value="1024").pack(anchor=tk.W, pady=5)
            
            # Frame nút bấm
            btn_frame = ttk.Frame(dialog)
            btn_frame.pack(pady=20)
            
            def start_generation():
                try:
                    bit_size = int(size_var.get())
                    dialog.destroy()
                    self._perform_auto_key_generation(bit_size)
                except Exception as e:
                    messagebox.showerror("Lỗi", f"Lỗi: {str(e)}")
            
            def cancel():
                dialog.destroy()
            
            ttk.Button(btn_frame, text="Sinh khóa", command=start_generation).pack(side=tk.LEFT, padx=5)
            ttk.Button(btn_frame, text="Hủy", command=cancel).pack(side=tk.LEFT, padx=5)
            
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi: {str(e)}")
    
    def _perform_auto_key_generation(self, bit_size):
        """
        Thực hiện tự động sinh khóa (tối ưu hóa cho tốc độ)
        
        Args:
            bit_size (int): Kích thước bit của số nguyên tố
        """
        try:
            import time
            start_time = time.time()
            
            # Hiển thị thông báo tiến trình
            progress_window = tk.Toplevel(self.root)
            progress_window.title("Đang sinh khóa...")
            progress_window.geometry("400x150")
            progress_window.resizable(False, False)
            progress_window.transient(self.root)
            
            # Không cho phép đóng cửa sổ
            progress_window.protocol("WM_DELETE_WINDOW", lambda: None)
            
            # Căn giữa
            progress_window.grab_set()
            
            # Thông báo
            msg = ttk.Label(progress_window, text=f"⏳ Đang sinh số nguyên tố {bit_size} bit...", 
                           font=("Arial", 11))
            msg.pack(pady=20)
            
            progress_bar = ttk.Progressbar(progress_window, mode='indeterminate')
            progress_bar.pack(pady=10, padx=20, fill=tk.X)
            progress_bar.start()
            
            detail_label = ttk.Label(progress_window, text="", font=("Arial", 9))
            detail_label.pack(pady=5)
            
            # Cập nhật giao diện
            self.root.update()
            
            # Bước 1: Sinh số nguyên tố p
            step1_start = time.time()
            detail_label.config(text="Bước 1/3: Sinh số nguyên tố p...")
            self.root.update()
            p = self.generate_large_prime(bit_size)
            step1_time = time.time() - step1_start
            
            # Bước 2: Tìm căn nguyên thủy g
            step2_start = time.time()
            detail_label.config(text="Bước 2/3: Tìm căn nguyên thủy g...")
            self.root.update()
            g = ElGamal.primitive_root(p)
            step2_time = time.time() - step2_start
            
            # Bước 3: Sinh khóa bí mật x và tính khóa công khai y
            step3_start = time.time()
            detail_label.config(text="Bước 3/3: Tính khóa công khai...")
            self.root.update()
            
            x = None  # Để ElGamal.generate_keys tự động sinh
            keys = ElGamal.generate_keys(p, g, x)
            step3_time = time.time() - step3_start
            
            total_time = time.time() - start_time
            
            # Cập nhật trường nhập
            self.entry_p.delete(0, tk.END)
            self.entry_p.insert(0, str(keys['p']))
            
            self.entry_g.delete(0, tk.END)
            self.entry_g.insert(0, str(keys['g']))
            
            self.entry_q.delete(0, tk.END)
            self.entry_q.insert(0, str(keys['x']))
            
            self.entry_y.delete(0, tk.END)
            self.entry_y.insert(0, str(keys['y']))
            
            # Đóng cửa sổ tiến trình
            progress_window.destroy()
            
            # Sinh khóa (bỏ qua kiểm tra primality vì đã xác nhận)
            self.skip_prime_validation = True
            self.generate_keys()
            
            # Hiển thị thông báo thành công với thời gian
            time_msg = (f"✅ Đã sinh khóa tự động thành công!\n\n"
                       f"Kích thước: {bit_size} bit\n"
                       f"Thời gian sinh:\n"
                       f"  • Bước 1 (sinh p): {step1_time:.2f}s\n"
                       f"  • Bước 2 (tìm g): {step2_time:.2f}s\n"
                       f"  • Bước 3 (tính y): {step3_time:.2f}s\n"
                       f"  • Tổng: {total_time:.2f}s\n\n"
                       f"Số nguyên tố p: {str(keys['p'])[:40]}...\n"
                       f"Căn nguyên thủy g: {keys['g']}")
            messagebox.showinfo("Thành công", time_msg)
        
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi khi sinh khóa: {str(e)}")
    
    def create_signature(self):
        """Tạo chữ ký"""
        try:
            if self.sig_manager is None:
                messagebox.showerror("Lỗi", "Chưa sinh khóa. Hãy sinh khóa trước!")
                return
            
            message = self.text_message.get("1.0", tk.END).strip()
            
            if not message:
                messagebox.showerror("Lỗi", "Vui lòng nhập dữ liệu cần ký!")
                return
            
            # Kiểm tra dữ liệu
            if not isinstance(message, str):
                messagebox.showerror("Lỗi", "Dữ liệu phải là text!")
                return
            
            # Tạo chữ ký
            sig_data = self.sig_manager.sign_message(message)
            
            # Kiểm tra kết quả
            if sig_data is None or 'signature' not in sig_data:
                messagebox.showerror("Lỗi", "Lỗi tạo chữ ký!")
                return
            
            # Hiển thị
            self.display_signature(sig_data)
            
            # Hiển thị hash
            self.text_hash_display.delete("1.0", tk.END)
            self.text_hash_display.insert(tk.END, sig_data['hash_hex'])
            
            # Lưu dữ liệu để dùng sau
            self.current_message = message
            self.current_signature = sig_data
            
            messagebox.showinfo("Thành công", "Đã tạo chữ ký thành công!")
        
        except TypeError as e:
            messagebox.showerror("Lỗi kiểu dữ liệu", f"Lỗi: {str(e)}\n\nVui lòng kiểm tra các tham số!")
        except ValueError as e:
            messagebox.showerror("Lỗi giá trị", f"Lỗi: {str(e)}")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi: {str(e)}")
    
    def display_signature(self, sig_data):
        """Hiển thị chữ ký"""
        self.text_signature.delete("1.0", tk.END)
        
        sig = sig_data['signature']
        sig_dict = {"r": sig['r'], "s": sig['s']}
        sig_json = json.dumps(sig_dict, indent=2)
        
        info = f"""
╔═══════════════════════════════════════════════════════════╗
║          CHỮ KÝ SỐ ELGAMAL                                ║
╚═══════════════════════════════════════════════════════════╝

【 DỮ LIỆU GỐC 】
{sig_data['message'][:200]}
{'...' if len(sig_data['message']) > 200 else ''}

【 HASH SHA-256 】
  {sig_data['hash_hex']}

【 CHỮ KÝ (r, s) 】
  • r = {sig['r']}
  • s = {sig['s']}

【 ĐỊNH DẠNG JSON 】
{sig_json}

"""
        
        self.text_signature.insert(tk.END, info)
    
    def verify_signature(self):
        """Xác minh chữ ký"""
        try:
            if self.sig_manager is None or self.public_key is None:
                messagebox.showerror("Lỗi", "Chưa sinh khóa. Hãy sinh khóa trước!")
                return
            
            message = self.text_verify_message.get("1.0", tk.END).strip()
            sig_text = self.text_verify_signature.get("1.0", tk.END).strip()
            original_hash_text = self.text_verify_original_hash.get("1.0", tk.END).strip()
            
            if not message or not sig_text:
                messagebox.showerror("Lỗi", "Vui lòng nhập dữ liệu cần ký và chữ ký!")
                return
            
            # Phân tích chữ ký
            try:
                sig_dict = json.loads(sig_text)
            except json.JSONDecodeError:
                messagebox.showerror("Lỗi", "Định dạng chữ ký không hợp lệ (phải là JSON)!")
                return
            
            # Xác minh - truyền hash gốc nếu có
            checker = SignatureChecker()
            original_hash = None
            
            # Ưu tiên: hash từ trường nhập > hash từ file chữ ký
            if original_hash_text:
                original_hash = original_hash_text
            elif isinstance(sig_dict, dict) and 'hash' in sig_dict:
                original_hash = sig_dict.get('hash')
                # Loại bỏ hash khỏi dict chữ ký để xác minh
                sig_dict = {'r': sig_dict.get('r'), 's': sig_dict.get('s')}
            
            result = checker.detailed_verification(message, sig_dict, self.public_key, original_hash)
            
            # Hiển thị
            self.display_verification_result(result)
        
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi: {str(e)}")

    
    def display_verification_result(self, result):
        """Hiển thị kết quả xác minh"""
        self.text_verify_result.delete("1.0", tk.END)
        
        status_color = "[HỢP LỆ]" if result['overall'] else "[KHÔNG HỢP LỆ]"
        
        # Xác định biểu tượng trạng thái dựa trên loại sửa đổi
        tampering_type = result.get('tampering_type', 'none')
        
        if tampering_type == 'none':
            status_symbol = "✓"
            status_text = "HỢP LỆ"
        elif tampering_type == 'text_modified':
            status_symbol = "✗"
            status_text = "VĂN BẢN BỊ SỬA ĐỔI"
        elif tampering_type == 'signature_modified':
            status_symbol = "✗"
            status_text = "CHỮ KÝ BỊ SỬA ĐỔI"
        elif tampering_type == 'both_modified':
            status_symbol = "✗"
            status_text = "CẢ VĂN BẢN VÀ CHỮ KÝ BỊ SỬA ĐỔI"
        else:
            status_symbol = "?"
            status_text = "KHÔNG THỂ XÁC ĐỊNH"
        
        info = f"""
╔═══════════════════════════════════════════════════════════╗
║                  KẾT QUẢ XÁC MINH CHỮ KÝ                  ║
╚═══════════════════════════════════════════════════════════╝

【 KẾT LUẬN CHUNG 】
  {status_symbol} {result['overall_message']}

【 KIỂM TRA CHI TIẾT 】
"""
        
        for check_name, check_result in result['checks'].items():
            status_sym = "✓" if check_result['status'] else "✗"
            info += f"  {status_sym} {check_result['message']}\n"
        
        # Nếu có hash gốc, hiển thị so sánh
        if result.get('original_message_hash'):
            info += f"""
【 KIỂM TRA TOÀN VẸN DỮ LIỆU 】
  • Hash gốc:     {result['original_message_hash']}
  • Hash hiện tại: {result.get('current_message_hash', 'N/A')}
  • Kết quả:      {'✓ Khớp' if result['original_message_hash'] == result.get('current_message_hash') else '✗ Không khớp'}
"""
        
        info += f"""
【 THÔNG TIN KHÓA CÔNG KHAI 】
  • p = {result['public_key_p']}
  • g = {result['public_key_g']}
  • y = {result['public_key_y']}

【 DỮ LIỆU 】
{result['message'][:200]}
{'...' if len(result['message']) > 200 else ''}

【 CHỮ KÝ 】
  • r = {result['signature']['r']}
  • s = {result['signature']['s']}
"""
        
        self.text_verify_result.insert(tk.END, info)

    
    def save_keys(self):
        """Lưu khóa vào file với nhiều định dạng"""
        try:
            if self.sig_manager is None:
                messagebox.showerror("Lỗi", "Chưa sinh khóa!")
                return
            
            # Tạo dialog lựa chọn định dạng
            dialog = tk.Toplevel(self.root)
            dialog.title("Lựa chọn định dạng lưu file")
            dialog.geometry("400x300")
            dialog.resizable(False, False)
            dialog.transient(self.root)
            dialog.grab_set()
            
            # Tiêu đề
            title_label = ttk.Label(dialog, text="Chọn định dạng lưu file:", 
                                   font=("Arial", 11, "bold"))
            title_label.pack(pady=10)
            
            # Frame chọn định dạng
            frame_format = ttk.Frame(dialog)
            frame_format.pack(pady=10, padx=20, fill=tk.BOTH, expand=True)
            
            format_var = tk.StringVar(value="json")
            
            ttk.Radiobutton(frame_format, text="📄 JSON (.json) - Mặc định", 
                           variable=format_var, value="json").pack(anchor=tk.W, pady=8)
            ttk.Radiobutton(frame_format, text="📝 Text (.txt) - Dễ đọc", 
                           variable=format_var, value="txt").pack(anchor=tk.W, pady=8)
            ttk.Radiobutton(frame_format, text="📕 Word (.docx) - Chuyên nghiệp", 
                           variable=format_var, value="docx").pack(anchor=tk.W, pady=8)
            ttk.Radiobutton(frame_format, text="📕 PDF (.pdf) - Chính thức", 
                           variable=format_var, value="pdf").pack(anchor=tk.W, pady=8)
            
            # Frame nút bấm
            btn_frame = ttk.Frame(dialog)
            btn_frame.pack(pady=20)
            
            def save_file():
                selected_format = format_var.get()
                
                # Xác định phần mở rộng và loại tệp
                format_map = {
                    'json': ('.json', [("JSON files", "*.json"), ("All files", "*.*")]),
                    'txt': ('.txt', [("Text files", "*.txt"), ("All files", "*.*")]),
                    'docx': ('.docx', [("Word files", "*.docx"), ("All files", "*.*")]),
                    'pdf': ('.pdf', [("PDF files", "*.pdf"), ("All files", "*.*")])
                }
                
                ext, ftypes = format_map[selected_format]
                
                filepath = filedialog.asksaveasfilename(
                    defaultextension=ext,
                    filetypes=ftypes
                )
                
                if filepath:
                    success, message = FileHandler.save_keys_with_format(
                        self.sig_manager.keys, 
                        filepath, 
                        selected_format
                    )
                    
                    if success:
                        messagebox.showinfo("Thành công", f"Đã lưu tại:\n{filepath}")
                    else:
                        messagebox.showerror("Lỗi", message)
                
                dialog.destroy()
            
            def cancel():
                dialog.destroy()
            
            ttk.Button(btn_frame, text="Lưu", command=save_file).pack(side=tk.LEFT, padx=5)
            ttk.Button(btn_frame, text="Hủy", command=cancel).pack(side=tk.LEFT, padx=5)
        
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi: {str(e)}")
    
    def load_keys(self):
        """Tải khóa từ file"""
        try:
            filepath = filedialog.askopenfilename(
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
            )
            
            if filepath:
                keys = FileHandler.load_keys(filepath)
                
                if keys:
                    # Cập nhật trường nhập
                    self.entry_p.delete(0, tk.END)
                    self.entry_p.insert(0, str(keys['p']))
                    
                    self.entry_g.delete(0, tk.END)
                    self.entry_g.insert(0, str(keys['g']))
                    
                    self.entry_q.delete(0, tk.END)
                    self.entry_q.insert(0, str(keys['x']))
                    
                    self.entry_y.delete(0, tk.END)
                    self.entry_y.insert(0, str(keys['y']))
                    
                    # Sinh khóa
                    self.generate_keys()
                else:
                    messagebox.showerror("Lỗi", "Lỗi khi tải khóa!")
        
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi: {str(e)}")
    
    def save_message(self):
        """Lưu dữ liệu với nhiều định dạng"""
        try:
            message = self.text_message.get("1.0", tk.END).strip()
            
            if not message:
                messagebox.showerror("Lỗi", "Vui lòng nhập dữ liệu cần ký!")
                return
            
            # Tạo dialog lựa chọn định dạng
            dialog = tk.Toplevel(self.root)
            dialog.title("Lựa chọn định dạng lưu file")
            dialog.geometry("400x300")
            dialog.resizable(False, False)
            dialog.transient(self.root)
            dialog.grab_set()
            
            # Tiêu đề
            title_label = ttk.Label(dialog, text="Chọn định dạng lưu file:", 
                                   font=("Arial", 11, "bold"))
            title_label.pack(pady=10)
            
            # Frame chọn định dạng
            frame_format = ttk.Frame(dialog)
            frame_format.pack(pady=10, padx=20, fill=tk.BOTH, expand=True)
            
            format_var = tk.StringVar(value="txt")
            
            ttk.Radiobutton(frame_format, text="📝 Text (.txt) - Mặc định", 
                           variable=format_var, value="txt").pack(anchor=tk.W, pady=8)
            ttk.Radiobutton(frame_format, text="📕 Word (.docx) - Chuyên nghiệp", 
                           variable=format_var, value="docx").pack(anchor=tk.W, pady=8)
            ttk.Radiobutton(frame_format, text="📕 PDF (.pdf) - Chính thức", 
                           variable=format_var, value="pdf").pack(anchor=tk.W, pady=8)
            
            # Frame nút bấm
            btn_frame = ttk.Frame(dialog)
            btn_frame.pack(pady=20)
            
            def save_file():
                selected_format = format_var.get()
                
                # Xác định phần mở rộng và loại tệp
                format_map = {
                    'txt': ('.txt', [("Text files", "*.txt"), ("All files", "*.*")]),
                    'docx': ('.docx', [("Word files", "*.docx"), ("All files", "*.*")]),
                    'pdf': ('.pdf', [("PDF files", "*.pdf"), ("All files", "*.*")])
                }
                
                ext, ftypes = format_map[selected_format]
                
                filepath = filedialog.asksaveasfilename(
                    defaultextension=ext,
                    filetypes=ftypes
                )
                
                if filepath:
                    success, message = FileHandler.save_message_with_format(
                        message, 
                        filepath, 
                        selected_format
                    )
                    
                    if success:
                        messagebox.showinfo("Thành công", f"Đã lưu tại:\n{filepath}")
                    else:
                        messagebox.showerror("Lỗi", message)
                
                dialog.destroy()
            
            def cancel():
                dialog.destroy()
            
            ttk.Button(btn_frame, text="Lưu", command=save_file).pack(side=tk.LEFT, padx=5)
            ttk.Button(btn_frame, text="Hủy", command=cancel).pack(side=tk.LEFT, padx=5)
        
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi: {str(e)}")
    
    def load_message(self):
        """Tải dữ liệu"""
        try:
            filepath = filedialog.askopenfilename(
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
            )
            
            if filepath:
                message = FileHandler.load_message(filepath)
                
                if message:
                    self.text_message.delete("1.0", tk.END)
                    self.text_message.insert(tk.END, message)
                    messagebox.showinfo("Thành công", "Đã tải dữ liệu!")
                else:
                    messagebox.showerror("Lỗi", "Lỗi khi tải!")
        
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi: {str(e)}")
    
    def save_signature(self):
        """Lưu chữ ký với nhiều định dạng"""
        try:
            if not hasattr(self, 'current_signature'):
                messagebox.showerror("Lỗi", "Chưa tạo chữ ký!")
                return
            
            # Tạo dialog lựa chọn định dạng
            dialog = tk.Toplevel(self.root)
            dialog.title("Lựa chọn định dạng lưu file")
            dialog.geometry("400x300")
            dialog.resizable(False, False)
            dialog.transient(self.root)
            dialog.grab_set()
            
            # Tiêu đề
            title_label = ttk.Label(dialog, text="Chọn định dạng lưu file:", 
                                   font=("Arial", 11, "bold"))
            title_label.pack(pady=10)
            
            # Frame chọn định dạng
            frame_format = ttk.Frame(dialog)
            frame_format.pack(pady=10, padx=20, fill=tk.BOTH, expand=True)
            
            format_var = tk.StringVar(value="json")
            
            ttk.Radiobutton(frame_format, text="📄 JSON (.json) - Mặc định", 
                           variable=format_var, value="json").pack(anchor=tk.W, pady=8)
            ttk.Radiobutton(frame_format, text="📝 Text (.txt) - Dễ đọc", 
                           variable=format_var, value="txt").pack(anchor=tk.W, pady=8)
            ttk.Radiobutton(frame_format, text="📕 Word (.docx) - Chuyên nghiệp", 
                           variable=format_var, value="docx").pack(anchor=tk.W, pady=8)
            ttk.Radiobutton(frame_format, text="📕 PDF (.pdf) - Chính thức", 
                           variable=format_var, value="pdf").pack(anchor=tk.W, pady=8)
            
            # Frame nút bấm
            btn_frame = ttk.Frame(dialog)
            btn_frame.pack(pady=20)
            
            def save_file():
                selected_format = format_var.get()
                
                # Xác định phần mở rộng và loại tệp
                format_map = {
                    'json': ('.json', [("JSON files", "*.json"), ("All files", "*.*")]),
                    'txt': ('.txt', [("Text files", "*.txt"), ("All files", "*.*")]),
                    'docx': ('.docx', [("Word files", "*.docx"), ("All files", "*.*")]),
                    'pdf': ('.pdf', [("PDF files", "*.pdf"), ("All files", "*.*")])
                }
                
                ext, ftypes = format_map[selected_format]
                
                filepath = filedialog.asksaveasfilename(
                    defaultextension=ext,
                    filetypes=ftypes
                )
                
                if filepath:
                    success, message = FileHandler.save_signature_with_format(
                        self.current_signature, 
                        filepath, 
                        selected_format
                    )
                    
                    if success:
                        messagebox.showinfo("Thành công", f"Đã lưu tại:\n{filepath}")
                    else:
                        messagebox.showerror("Lỗi", message)
                
                dialog.destroy()
            
            def cancel():
                dialog.destroy()
            
            ttk.Button(btn_frame, text="Lưu", command=save_file).pack(side=tk.LEFT, padx=5)
            ttk.Button(btn_frame, text="Hủy", command=cancel).pack(side=tk.LEFT, padx=5)
        
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi: {str(e)}")

    
    def copy_signature(self):
        """Sao chép chữ ký"""
        try:
            if not hasattr(self, 'current_signature'):
                messagebox.showerror("Lỗi", "Chưa tạo chữ ký!")
                return
            
            sig_json = json.dumps({
                "r": self.current_signature['signature']['r'],
                "s": self.current_signature['signature']['s']
            })
            
            self.root.clipboard_clear()
            self.root.clipboard_append(sig_json)
            
            messagebox.showinfo("Thành công", "Đã sao chép chữ ký vào clipboard!")
        
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi: {str(e)}")
    
    def load_message_for_verify(self):
        """Tải dữ liệu để xác minh"""
        try:
            filepath = filedialog.askopenfilename(
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
            )
            
            if filepath:
                message = FileHandler.load_message(filepath)
                
                if message:
                    self.text_verify_message.delete("1.0", tk.END)
                    self.text_verify_message.insert(tk.END, message)
        
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi: {str(e)}")
    
    def load_signature_for_verify(self):
        """Tải chữ ký để xác minh"""
        try:
            filepath = filedialog.askopenfilename(
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
            )
            
            if filepath:
                sig_data = FileHandler.load_signature(filepath)
                
                if sig_data:
                    # Tạo dict chữ ký với hash nếu có
                    sig_dict = {
                        "r": sig_data.get('r'),
                        "s": sig_data.get('s')
                    }
                    
                    # Thêm hash nếu có (để sử dụng cho xác minh chi tiết)
                    if 'hash' in sig_data:
                        sig_dict['hash'] = sig_data['hash']
                    
                    sig_json = json.dumps(sig_dict, indent=2)
                    
                    self.text_verify_signature.delete("1.0", tk.END)
                    self.text_verify_signature.insert(tk.END, sig_json)
                    
                    # Hiển thị thông báo
                    if 'hash' in sig_data:
                        messagebox.showinfo("Thành công", 
                            "Đã tải chữ ký với hash gốc.\n\n"
                            "Khi xác minh, hệ thống sẽ so sánh\n"
                            "với hash hiện tại để phát hiện\n"
                            "nếu văn bản bị sửa đổi.")
                    else:
                        messagebox.showinfo("Thành công", "Đã tải chữ ký.")
        
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi: {str(e)}")
    
    def clear_verify_fields(self):
        """Xóa các trường xác minh"""
        self.text_verify_message.delete("1.0", tk.END)
        self.text_verify_signature.delete("1.0", tk.END)
        self.text_verify_original_hash.delete("1.0", tk.END)
        self.text_verify_result.delete("1.0", tk.END)
    
    def load_hash_for_verify(self):
        """Tải hash gốc từ file chữ ký"""
        try:
            filepath = filedialog.askopenfilename(
                filetypes=[("JSON files", "*.json"), ("Text files", "*.txt"), ("All files", "*.*")]
            )
            
            if filepath:
                # Thử tải như file JSON chữ ký
                try:
                    sig_data = FileHandler.load_signature(filepath)
                    if sig_data and 'hash' in sig_data:
                        hash_value = sig_data['hash']
                        self.text_verify_original_hash.delete("1.0", tk.END)
                        self.text_verify_original_hash.insert(tk.END, hash_value)
                        messagebox.showinfo("Thành công", 
                            "Đã tải hash gốc từ file chữ ký.\n\n"
                            "Hash sẽ được dùng để phát hiện\n"
                            "chính xác loại sửa đổi.")
                        return
                except:
                    pass
                
                # Thử tải từ file text (hash có thể ở dòng đầu tiên)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read().strip()
                        # Lấy dòng đầu tiên hoặc tìm hash hex
                        lines = content.split('\n')
                        for line in lines:
                            line = line.strip()
                            # Kiểm tra nếu là hash SHA-256 (64 ký tự hex)
                            if len(line) == 64 and all(c in '0123456789abcdefABCDEF' for c in line):
                                self.text_verify_original_hash.delete("1.0", tk.END)
                                self.text_verify_original_hash.insert(tk.END, line)
                                messagebox.showinfo("Thành công", "Đã tải hash gốc từ file.")
                                return
                        
                        # Nếu không tìm thấy, hiển thị lỗi
                        messagebox.showerror("Lỗi", "Không tìm thấy hash SHA-256 trong file.")
                except Exception as e:
                    messagebox.showerror("Lỗi", f"Lỗi khi đọc file: {e}")
        
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi: {str(e)}")
    
    def save_verification_report(self):
        """Lưu báo cáo xác minh với nhiều định dạng"""
        try:
            report_text = self.text_verify_result.get("1.0", tk.END).strip()
            
            if not report_text:
                messagebox.showerror("Lỗi", "Không có báo cáo để lưu!")
                return
            
            # Tạo dialog lựa chọn định dạng
            dialog = tk.Toplevel(self.root)
            dialog.title("Lựa chọn định dạng lưu file")
            dialog.geometry("400x300")
            dialog.resizable(False, False)
            dialog.transient(self.root)
            dialog.grab_set()
            
            # Tiêu đề
            title_label = ttk.Label(dialog, text="Chọn định dạng lưu file:", 
                                   font=("Arial", 11, "bold"))
            title_label.pack(pady=10)
            
            # Frame chọn định dạng
            frame_format = ttk.Frame(dialog)
            frame_format.pack(pady=10, padx=20, fill=tk.BOTH, expand=True)
            
            format_var = tk.StringVar(value="txt")
            
            ttk.Radiobutton(frame_format, text="📝 Text (.txt) - Mặc định", 
                           variable=format_var, value="txt").pack(anchor=tk.W, pady=8)
            ttk.Radiobutton(frame_format, text="📕 Word (.docx) - Chuyên nghiệp", 
                           variable=format_var, value="docx").pack(anchor=tk.W, pady=8)
            ttk.Radiobutton(frame_format, text="📕 PDF (.pdf) - Chính thức", 
                           variable=format_var, value="pdf").pack(anchor=tk.W, pady=8)
            
            # Frame nút bấm
            btn_frame = ttk.Frame(dialog)
            btn_frame.pack(pady=20)
            
            def save_file():
                selected_format = format_var.get()
                
                # Xác định phần mở rộng và loại tệp
                format_map = {
                    'txt': ('.txt', [("Text files", "*.txt"), ("All files", "*.*")]),
                    'docx': ('.docx', [("Word files", "*.docx"), ("All files", "*.*")]),
                    'pdf': ('.pdf', [("PDF files", "*.pdf"), ("All files", "*.*")])
                }
                
                ext, ftypes = format_map[selected_format]
                
                filepath = filedialog.asksaveasfilename(
                    defaultextension=ext,
                    filetypes=ftypes
                )
                
                if filepath:
                    success, message = FileHandler.save_report_with_format(
                        report_text, 
                        filepath, 
                        selected_format
                    )
                    
                    if success:
                        messagebox.showinfo("Thành công", f"Đã lưu tại:\n{filepath}")
                    else:
                        messagebox.showerror("Lỗi", message)
                
                dialog.destroy()
            
            def cancel():
                dialog.destroy()
            
            ttk.Button(btn_frame, text="Lưu", command=save_file).pack(side=tk.LEFT, padx=5)
            ttk.Button(btn_frame, text="Hủy", command=cancel).pack(side=tk.LEFT, padx=5)
        
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi: {str(e)}")
    
    def copy_hash(self):
        """Copy hash vào clipboard"""
        try:
            hash_text = self.text_hash_display.get("1.0", tk.END).strip()
            if not hash_text:
                messagebox.showwarning("Cảnh báo", "Không có hash để copy!")
                return
            
            self.root.clipboard_clear()
            self.root.clipboard_append(hash_text)
            messagebox.showinfo("Thành công", "Đã copy hash vào clipboard!")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi: {str(e)}")
    
    def save_hash(self):
        """Lưu hash vào file với nhiều định dạng"""
        try:
            hash_text = self.text_hash_display.get("1.0", tk.END).strip()
            if not hash_text:
                messagebox.showwarning("Cảnh báo", "Không có hash để lưu!")
                return
            
            # Tạo dialog lựa chọn định dạng
            dialog = tk.Toplevel(self.root)
            dialog.title("Lựa chọn định dạng lưu file")
            dialog.geometry("400x300")
            dialog.resizable(False, False)
            dialog.transient(self.root)
            dialog.grab_set()
            
            # Tiêu đề
            title_label = ttk.Label(dialog, text="Chọn định dạng lưu file:", 
                                   font=("Arial", 11, "bold"))
            title_label.pack(pady=10)
            
            # Frame chọn định dạng
            frame_format = ttk.Frame(dialog)
            frame_format.pack(pady=10, padx=20, fill=tk.BOTH, expand=True)
            
            format_var = tk.StringVar(value="txt")
            
            ttk.Radiobutton(frame_format, text="📝 Text (.txt) - Mặc định", 
                           variable=format_var, value="txt").pack(anchor=tk.W, pady=8)
            ttk.Radiobutton(frame_format, text="📕 Word (.docx) - Chuyên nghiệp", 
                           variable=format_var, value="docx").pack(anchor=tk.W, pady=8)
            ttk.Radiobutton(frame_format, text="📕 PDF (.pdf) - Chính thức", 
                           variable=format_var, value="pdf").pack(anchor=tk.W, pady=8)
            
            # Frame nút bấm
            btn_frame = ttk.Frame(dialog)
            btn_frame.pack(pady=20)
            
            def save_file():
                selected_format = format_var.get()
                
                # Xác định phần mở rộng và loại tệp
                format_map = {
                    'txt': ('.txt', [("Text files", "*.txt"), ("All files", "*.*")]),
                    'docx': ('.docx', [("Word files", "*.docx"), ("All files", "*.*")]),
                    'pdf': ('.pdf', [("PDF files", "*.pdf"), ("All files", "*.*")])
                }
                
                ext, ftypes = format_map[selected_format]
                
                filepath = filedialog.asksaveasfilename(
                    defaultextension=ext,
                    filetypes=ftypes
                )
                
                if filepath:
                    success, message = FileHandler.save_hash_with_format(
                        hash_text, 
                        filepath, 
                        selected_format
                    )
                    
                    if success:
                        messagebox.showinfo("Thành công", f"Đã lưu tại:\n{filepath}")
                    else:
                        messagebox.showerror("Lỗi", message)
                
                dialog.destroy()
            
            def cancel():
                dialog.destroy()
            
            ttk.Button(btn_frame, text="Lưu", command=save_file).pack(side=tk.LEFT, padx=5)
            ttk.Button(btn_frame, text="Hủy", command=cancel).pack(side=tk.LEFT, padx=5)
        
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi: {str(e)}")


if __name__ == "__main__":
    root = tk.Tk()
    app = ElGamalSignatureGUI(root)
    root.mainloop()
