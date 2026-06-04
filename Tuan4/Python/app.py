import streamlit as st
import hashlib
import random
import math
# python -m streamlit run app.py
# ==========================================
# CÁC HÀM TOÁN HỌC ELGAMAL
# ==========================================
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

# ==========================================
# GIAO DIỆN WEB (STREAMLIT)
# ==========================================
st.set_page_config(page_title="Ứng dụng Chữ ký số ElGamal", layout="centered")
st.title("🔐 Ứng dụng Chữ ký số ElGamal")
st.markdown("---")

# --- PHẦN 1: TẠO KHÓA ---
st.header("1. Tạo khóa")
st.info("Gợi ý test: Nhập p = 10631, a = 11, x = 1831 (giống báo cáo). Hệ thống sẽ tự tính y.")

col1, col2, col3, col4 = st.columns(4)
with col1: p_val = st.text_input("Số nguyên tố p:", value="10631")
with col2: a_val = st.text_input("Căn nguyên thủy a:", value="11")
with col3: x_val = st.text_input("Khóa bí mật x:", value="1831")
with col4: y_val = st.text_input("Khóa công khai y:", value="", help="Sẽ tự động tính toán")

if st.button("Tạo Khóa", type="primary"):
    try:
        p, a, x = int(p_val), int(a_val), int(x_val)
        y = pow(a, x, p) # Công thức tính khóa công khai y = a^x mod p
        st.success("Tạo khóa thành công!")
        st.code(f"Khóa công khai: (p={p}, a={a}, y={y})\nKhóa bí mật: x={x}")
    except ValueError:
        st.error("Vui lòng nhập số nguyên hợp lệ vào các ô p, a, x.")

st.markdown("---")

# --- PHẦN 2: TẠO CHỮ KÝ SỐ ---
st.header("2. Tạo chữ ký số")
sign_mode = st.radio("Phương thức nhập văn bản:", ["Nhập trực tiếp", "Tải tệp lên (.txt)"], key="sign_mode")

message_to_sign = ""
if sign_mode == "Nhập trực tiếp":
    message_to_sign = st.text_area("Nhập thông điệp cần ký:", height=100)
else:
    uploaded_file_sign = st.file_uploader("Chọn tệp văn bản", type=["txt"], key="file_sign")
    if uploaded_file_sign is not None:
        message_to_sign = uploaded_file_sign.read().decode("utf-8")
        st.text_area("Nội dung tệp:", value=message_to_sign, height=100, disabled=True)

if st.button("Ký Văn Bản", type="primary", key="btn_sign"):
    if message_to_sign.strip() == "":
        st.warning("Vui lòng nhập văn bản hoặc tải tệp lên trước khi ký!")
    else:
        try:
            p, a, x = int(p_val), int(a_val), int(x_val)
            signature = sign_elgamal(message_to_sign, p, a, x)
            st.success("Tạo chữ ký thành công!")
            st.text_area("Chữ ký số của bạn (hãy copy đoạn này để test):", value=signature, height=100)
        except Exception as e:
            st.error(f"Lỗi: Hãy chắc chắn bạn đã nhập đúng các số p, a, x ở Phần 1.")

st.markdown("---")

# --- PHẦN 3: THẨM ĐỊNH CHỮ KÝ SỐ ---
st.header("3. Thẩm định chữ ký số")
col_msg, col_sig = st.columns(2)

with col_msg:
    st.subheader("Thông điệp/Tệp nhận được")
    verify_mode = st.radio("Phương thức:", ["Nhập trực tiếp", "Tải tệp lên"], key="verify_mode")
    message_to_verify = ""
    if verify_mode == "Nhập trực tiếp":
        message_to_verify = st.text_area("Nhập thông điệp:", height=150, key="msg_verify")
    else:
        uploaded_file_verify = st.file_uploader("Chọn tệp", type=["txt"], key="file_verify")
        if uploaded_file_verify is not None:
            message_to_verify = uploaded_file_verify.read().decode("utf-8")
            st.text_area("Nội dung tệp:", value=message_to_verify, height=100, disabled=True)

with col_sig:
    st.subheader("Chữ ký số đính kèm")
    signature_to_verify = st.text_area("Dán chữ ký số vào đây (định dạng r,s):", height=195)

if st.button("Xác Nhận Chữ Ký", type="primary", key="btn_verify"):
    if message_to_verify.strip() == "" or signature_to_verify.strip() == "":
        st.warning("Vui lòng nhập đủ thông điệp và chữ ký để kiểm tra!")
    else:
        try:
            p, a = int(p_val), int(a_val)
            # Nếu người dùng chưa nhập y ở phần 1, hệ thống tự tính lại y để xác thực
            y = int(y_val) if y_val.strip() != "" else pow(a, int(x_val), p)
            
            is_valid = verify_elgamal(message_to_verify, signature_to_verify, p, a, y)
            
            if is_valid:
                st.success("✅ Chữ ký CHÍNH XÁC. Thông điệp toàn vẹn!")
            else:
                st.error("❌ Chữ ký KHÔNG CHÍNH XÁC. Thông điệp đã bị thay đổi hoặc giả mạo!")
        except Exception as e:
             st.error("❌ Lỗi kiểm tra. Đảm bảo chữ ký đúng định dạng và các khóa p, a, y hợp lệ.")