# quanly_hopdong.py — PART 1/3
import os
import csv
import shutil
import re
import uuid
import datetime
import subprocess
import platform
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from docx import Document
from matplotlib import style

from option import Menu3Gach
from phongtro import QuanLyPhongTro
from nguoithue import QuanLyNguoiThue, NguoiThue

# =============================
# CẤU HÌNH
# =============================
CONTRACTS_DIR = "contracts"
CSV_FILE = "hopdong.csv"
TEMPLATE_CONFIG = "hopdong_template.txt"
# Default template: file bạn tải lên (đường dẫn local trong hệ thống)
DEFAULT_TEMPLATE_PATH = ""

os.makedirs(CONTRACTS_DIR, exist_ok=True)


# =============================
# HỖ TRỢ LƯU/LOAD TEMPLATE
# =============================
def load_template_path():
    if os.path.exists(TEMPLATE_CONFIG):
        try:
            with open(TEMPLATE_CONFIG, "r", encoding="utf-8") as f:
                p = f.readline().strip()
                if p:
                    return p
        except:
            pass
    if os.path.exists(DEFAULT_TEMPLATE_PATH):
        return DEFAULT_TEMPLATE_PATH
    return ""


def save_template_path(path: str):
    with open(TEMPLATE_CONFIG, "w", encoding="utf-8") as f:
        f.write(path or "")


def clear_template_path():
    if os.path.exists(TEMPLATE_CONFIG):
        try:
            os.remove(TEMPLATE_CONFIG)
        except:
            pass


# =============================
# MODEL HỢP ĐỒNG
# =============================
class HopDong:
    def __init__(self, ma_hop_dong, ten_nguoi_thue="", phong="",
                 ngay_bat_dau="", ngay_ket_thuc="", trang_thai="Chưa hợp đồng",
                 file_path=""):
        self.ma_hop_dong = ma_hop_dong
        self.ten_nguoi_thue = ten_nguoi_thue
        self.phong = phong
        self.ngay_bat_dau = ngay_bat_dau
        self.ngay_ket_thuc = ngay_ket_thuc
        self.trang_thai = trang_thai
        self.file_path = file_path


# =============================
# QUẢN LÝ HỢP ĐỒNG (CSV)
# =============================
class QuanLyHopDong:
    def __init__(self):
        self.ds_hop_dong = []
        self.tao_file_csv_neu_chua_co()
        self.doc_file_csv()

    def tao_file_csv_neu_chua_co(self):
        if not os.path.exists(CSV_FILE):
            with open(CSV_FILE, "w", encoding="utf-8", newline="") as f:
                csv.writer(f).writerow([
                    "Mã hợp đồng", "Người thuê", "Phòng",
                    "Ngày bắt đầu", "Ngày kết thúc", "Trạng thái", "File"
                ])

    def ghi_file_csv(self):
        with open(CSV_FILE, "w", encoding="utf-8", newline="") as f:
            w = csv.writer(f)
            w.writerow([
                "Mã hợp đồng", "Người thuê", "Phòng",
                "Ngày bắt đầu", "Ngày kết thúc", "Trạng thái", "File"
            ])
            for hd in self.ds_hop_dong:
                w.writerow([
                    hd.ma_hop_dong, hd.ten_nguoi_thue, hd.phong,
                    hd.ngay_bat_dau, hd.ngay_ket_thuc,
                    hd.trang_thai, hd.file_path
                ])

    def doc_file_csv(self):
        if not os.path.exists(CSV_FILE):
            return
        with open(CSV_FILE, "r", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                self.ds_hop_dong.append(
                    HopDong(
                        ma_hop_dong=row.get("Mã hợp đồng", ""),
                        ten_nguoi_thue=row.get("Người thuê", ""),
                        phong=row.get("Phòng", ""),
                        ngay_bat_dau=row.get("Ngày bắt đầu", ""),
                        ngay_ket_thuc=row.get("Ngày kết thúc", ""),
                        trang_thai=row.get("Trạng thái", ""),
                        file_path=row.get("File", "")
                    )
                )

    def them_hop_dong(self, hd: HopDong):
        if any(x.ma_hop_dong == hd.ma_hop_dong for x in self.ds_hop_dong):
            return False
        self.ds_hop_dong.append(hd)
        self.ghi_file_csv()
        return True

    def lay_ds_hop_dong(self):
        return self.ds_hop_dong

    def tim_hop_dong(self, ma):
        return next((h for h in self.ds_hop_dong if h.ma_hop_dong == ma), None)

    def xoa_hop_dong(self, ma):
        h = self.tim_hop_dong(ma)
        if not h:
            return False
        try:
            if h.file_path and os.path.exists(h.file_path):
                os.remove(h.file_path)
        except:
            pass
        self.ds_hop_dong.remove(h)
        self.ghi_file_csv()
        return True

    def cap_nhat_hop_dong(self, ma, **kwargs):
        h = self.tim_hop_dong(ma)
        if not h:
            return False
        for k, v in kwargs.items():
            if v is not None and hasattr(h, k):
                setattr(h, k, v)
        self.ghi_file_csv()
        return True


# =============================
# HỖ TRỢ: sanitize tên file
# =============================
def sanitize_for_filename(s: str):
    if not s:
        return ""
    # loại ký tự lạ, giữ chữ/số/unicode tiếng Việt
    s = re.sub(r"[^\w\d\u00C0-\u017F]+", "", s)
    return s


# =============================
# HÀM EXTRACT (đã sửa để đọc chính xác)
# =============================
def extract_info_from_docx(path_docx):
    """
    Trích xuất: tên người thuê, phòng, ngày bắt đầu, ngày kết thúc
    Hoạt động tốt với file hợp đồng thực tế.
    """
    info = {"ten_nguoi_thue": "", "phong": "", "ngay_bat_dau": "", "ngay_ket_thuc": ""}

    def try_parse(d, m, y):
        try:
            return datetime.date(int(y), int(m), int(d)).isoformat()
        except:
            return ""

    import re
    from docx import Document

    try:
        doc = Document(path_docx)

        # Gộp toàn bộ văn bản, tránh mất dòng
        lines = [p.text.strip() for p in doc.paragraphs]
        full = "\n".join(lines).replace("\xa0", " ")

        # ==============================
        # 1) TÊN NGƯỜI THUÊ (Ông/bà)
        # ==============================
        m_name = re.search(r"Bên B.*?(?:Ông\/?bà|Ông|Bà)\s*[:\- ]*\s*([^\n\r]+)", full, flags=re.I | re.S)
        if m_name:
            raw = m_name.group(1).strip()
            clean = re.split(r"Sinh ngày|Số|Nơi đăng ký", raw, flags=re.I)[0].strip()
            info["ten_nguoi_thue"] = clean

        # ==============================
        # 2) PHÒNG – ví dụ: "Tên Phòng: P104;"
        # ==============================
        m_room = re.search(r"Tên\s*Phòng\s*[:\- ]+\s*([A-Za-z0-9\-_/]+)", full, flags=re.I)
        if m_room:
            info["phong"] = m_room.group(1).replace(";", "").strip()
        else:
            # fallback
            m2 = re.search(r"\bPhòng\s*[:\- ]+\s*([A-Za-z0-9\-_/]+)", full, flags=re.I)
            if m2:
                info["phong"] = m2.group(1).replace(";", "").strip()

        # ==============================
        # 3) NGÀY BẮT ĐẦU – ví dụ: 24 tháng 11 năm 2025
        # ==============================
        m_start = re.search(
            r"kể từ ngày\s*([0-9]{1,2})\s*tháng\s*([0-9]{1,2})\s*năm\s*([0-9]{4})",
            full, flags=re.I)
        if m_start:
            d, m, y = m_start.groups()
            info["ngay_bat_dau"] = try_parse(d, m, y)

        # ==============================
        # 4) NGÀY KẾT THÚC – dòng riêng biệt
        # "... đến 23h59 ngày 24 tháng 11 năm 2026"
        # ==============================
        m_end = re.search(
            r"đến\s*23h?59.*?ngày\s*([0-9]{1,2})\s*tháng\s*([0-9]{1,2})\s*năm\s*([0-9]{4})",
            full, flags=re.I | re.S)
        if m_end:
            d, m, y = m_end.groups()
            info["ngay_ket_thuc"] = try_parse(d, m, y)

    except Exception as e:
        print("Lỗi đọc file:", e)

    return info

# quanly_hopdong.py — PART 2/3

# =============================
# Helper mở file bằng app mặc định
# =============================
def open_file_with_default_app(path):
    path = os.path.abspath(path)
    if platform.system() == "Windows":
        os.startfile(path)
    elif platform.system() == "Darwin":
        subprocess.call(["open", path])
    else:
        subprocess.call(["xdg-open", path])


# =============================
# CỬA SỔ HỢP ĐỒNG MẪU
# =============================
class TemplateHopDongWindow:
    def __init__(self, parent_ui):
        self.parent_ui = parent_ui
        self.template_path = parent_ui.template_path

        self.win = tk.Toplevel(parent_ui.root)
        self.win.title("Hợp đồng mẫu")
        self.win.geometry("900x260")
        self.win.configure(bg="#f3f3f7")
        self.win.grab_set()

        frame = tk.LabelFrame(self.win, text="Hợp đồng mẫu", font=("Segoe UI", 12, "bold"),
                              bg="white", padx=10, pady=10)
        frame.pack(fill="both", expand=True, padx=12, pady=10)

        self.status_var = tk.StringVar()
        self.update_status_text()

        tk.Label(frame, textvariable=self.status_var, font=("Segoe UI", 10, "italic"),
                 bg="white").grid(row=0, column=0, columnspan=3, sticky="w", pady=(0, 6))

        tk.Label(frame, text="Đường dẫn file mẫu:", font=("Segoe UI", 11), bg="white").grid(row=1, column=0, sticky="e", padx=6, pady=6)
        self.path_var = tk.StringVar(value=self.template_path or "")
        tk.Entry(frame, textvariable=self.path_var, font=("Segoe UI", 10), width=72).grid(row=1, column=1, padx=6, pady=6, sticky="w")

        tk.Button(frame, text="Tải lên hợp đồng mẫu", font=("Segoe UI", 10, "bold"),
                  bg="#1565C0", fg="white", width=20, command=self.chon_file).grid(row=1, column=2, padx=6, pady=6)

        frame_btn = tk.Frame(self.win, bg="#f3f3f7")
        frame_btn.pack(pady=6)

        tk.Button(frame_btn, text="Lưu", font=("Segoe UI", 10, "bold"),
                  bg="#2e7d32", fg="white", width=12, command=self.luu).grid(row=0, column=0, padx=8)

        tk.Button(frame_btn, text="Xóa hợp đồng mẫu", font=("Segoe UI", 10, "bold"),
                  bg="#c62828", fg="white", width=14, command=self.xoa).grid(row=0, column=1, padx=8)

        tk.Button(frame_btn, text="Đóng", font=("Segoe UI", 10, "bold"),
                  bg="#616161", fg="white", width=10, command=self.win.destroy).grid(row=0, column=2, padx=8)

        tk.Button(frame_btn, text="Tải mẫu", font=("Segoe UI", 10, "bold"),
                  bg="#0277BD", fg="white", width=12, command=self.tai_xuong_mau).grid(row=0, column=3, padx=8)

    def update_status_text(self):
        if self.template_path:
            self.status_var.set(f"Đang dùng mẫu: {self.template_path}")
        else:
            self.status_var.set("Chưa có hợp đồng mẫu. Hãy tải lên một file .docx hoặc dán đường dẫn vào ô bên dưới.")

    def chon_file(self):
        fpath = filedialog.askopenfilename(title="Chọn file hợp đồng mẫu", filetypes=[("Word file", "*.docx"), ("Tất cả", "*.*")])
        if not fpath:
            return
        self.template_path = os.path.abspath(fpath)
        self.path_var.set(self.template_path)
        self.update_status_text()

    def luu(self):
        path = self.path_var.get().strip()
        self.template_path = path
        self.parent_ui.template_path = path
        save_template_path(path)
        messagebox.showinfo("Lưu", "Đã lưu đường dẫn hợp đồng mẫu.")
        self.update_status_text()

    def xoa(self):
        if messagebox.askyesno("Xóa", "Bạn có chắc muốn xóa hợp đồng mẫu hiện tại?"):
            self.template_path = ""
            self.path_var.set("")
            self.parent_ui.template_path = ""
            clear_template_path()
            self.update_status_text()
            messagebox.showinfo("Xóa", "Đã xóa hợp đồng mẫu.")

    def tai_xuong_mau(self):
        if not self.template_path or not os.path.exists(self.template_path):
            messagebox.showerror("Lỗi", "Chưa có file hợp đồng mẫu để tải!")
            return
        dest = filedialog.asksaveasfilename(title="Lưu file hợp đồng mẫu", defaultextension=".docx", initialfile="Hop-dong-mau.docx", filetypes=[("Word file", "*.docx"), ("Tất cả", "*.*")])
        if not dest:
            return
        try:
            shutil.copyfile(self.template_path, dest)
            messagebox.showinfo("Thành công", "Đã tải xuống hợp đồng mẫu.")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể tải mẫu: {e}")


# =============================
# UI QUẢN LÝ HỢP ĐỒNG
# =============================
class QuanLyHopDongUI:
    def __init__(self, root, controller):
        self.root = root
        self.controller = controller
        self.root.title("📑 Quản Lý Hợp Đồng")
        self.root.geometry("1700x800")
        self.root.configure(bg="#eef2f7")

        # models
        self.ql_hd = QuanLyHopDong()
        self.ql_phong = QuanLyPhongTro()
        self.ql_nguoi = QuanLyNguoiThue()

        self.template_path = load_template_path()

        # style treeview
        style = ttk.Style()
        style.theme_use("default")

        # Màu ô bình thường
        style.configure(
            "Treeview",
            background="white",
            foreground="black",
            rowheight=28,
            fieldbackground="white",
            font=("Segoe UI", 11)
        )

        # Màu khi chọn dòng
        style.map(
            "Treeview",
            background=[("selected", "#F9FAFB")],
            foreground=[("selected", "black")]  # chữ không bị mờ
        )

        # Màu header
        style.configure(
            "Treeview.Heading",
            background="#F8FBFB",
            foreground="black",
            font=("Segoe UI", 12, "bold")
)
        self.build_ui()
        self.cleanup_hop_dong_qua_han()
    def cap_nhat_trang_thai_phong_theo_hop_dong(self):
        for hd in self.ql_hd.lay_ds_hop_dong():
            phong = hd.phong
            if not phong:
               continue

            # xử lý theo trạng thái hợp đồng
            for p in self.ql_phong.lay_ds_phong():
                if p.ten_phong == phong:

                        # 1. Nếu hợp đồng CHỜ XOÁ → phòng trống
                    if hd.trang_thai == "Chờ xoá":
                        self.ql_phong.cap_nhat_phong(p.ma_phong, trang_thai="Trống")

                        # 2. Các trạng thái khác → phòng vẫn bị chiếm
                    else:
                        self.ql_phong.cap_nhat_phong(p.ma_phong, trang_thai="Đang thuê")

                    break

# quanly_hopdong.py — PART 3/3
    def chon_menu(self, ten_menu):
        if ten_menu == "Trang chủ":
            self.root.destroy()
        elif ten_menu == "Quản lý phòng trọ":
            print("Chuyển sang quản lý phòng trọ")
        elif ten_menu == "Quản lý người thuê":
            print("Chuyển sang giao diện người thuê")
        elif ten_menu == "Quản lý hợp đồng":
            print("Đang ở giao diện hợp đồng")

    def build_ui(self):
        # menu
        self.menu = Menu3Gach(self, self.controller, active_menu="Quản lý hợp đồng")
        

        # form
        frame = tk.LabelFrame(self.root, text="🧾 Thông tin hợp đồng", bg="white", font=("Segoe UI", 13, "bold"), padx=15, pady=10)
        frame.pack(fill="x", padx=30, pady=15)

        # labels
        tk.Label(frame, text="Mã hợp đồng:", bg="white", font=("Segoe UI", 11)).grid(row=0, column=0, padx=8, pady=6, sticky="e")
        tk.Label(frame, text="Người thuê:", bg="white", font=("Segoe UI", 11)).grid(row=0, column=2, padx=8, pady=6, sticky="e")
        tk.Label(frame, text="Phòng:", bg="white", font=("Segoe UI", 11)).grid(row=0, column=4, padx=8, pady=6, sticky="e")
        tk.Label(frame, text="Ngày bắt đầu:", bg="white", font=("Segoe UI", 11)).grid(row=1, column=0, padx=8, pady=6, sticky="e")
        tk.Label(frame, text="Ngày kết thúc:", bg="white", font=("Segoe UI", 11)).grid(row=1, column=2, padx=8, pady=6, sticky="e")
        tk.Label(frame, text="Trạng thái:", bg="white", font=("Segoe UI", 11)).grid(row=1, column=4, padx=8, pady=6, sticky="e")
        tk.Label(frame, text="File:", bg="white", font=("Segoe UI", 11)).grid(row=2, column=0, padx=8, pady=6, sticky="e")

        # vars
        self.vars = {k: tk.StringVar() for k in ["Mã hợp đồng", "Người thuê", "Phòng", "Ngày bắt đầu", "Ngày kết thúc", "Trạng thái", "File"]}

        tk.Entry(frame, textvariable=self.vars["Mã hợp đồng"], font=("Segoe UI", 11), width=22).grid(row=0, column=1)
        tk.Entry(frame, textvariable=self.vars["Người thuê"], font=("Segoe UI", 11), width=22).grid(row=0, column=3)

        # combobox phòng hiển thị TÊN phòng
        self.vars["Phòng"] = tk.StringVar()
        self.cmb_phong = ttk.Combobox(frame, textvariable=self.vars["Phòng"], values=[p.ten_phong for p in self.ql_phong.lay_ds_phong()], font=("Segoe UI", 11), width=20, state="readonly")
        self.cmb_phong.grid(row=0, column=5)

        tk.Entry(frame, textvariable=self.vars["Ngày bắt đầu"], font=("Segoe UI", 11), width=22).grid(row=1, column=1)
        tk.Entry(frame, textvariable=self.vars["Ngày kết thúc"], font=("Segoe UI", 11), width=22).grid(row=1, column=3)

        ttk.Combobox(frame, textvariable=self.vars["Trạng thái"], values=["Chưa hợp đồng", "Đã hợp đồng", "Sắp hết hạn", "Hết hạn"], font=("Segoe UI", 11), width=20, state="readonly").grid(row=1, column=5)

        tk.Entry(frame, textvariable=self.vars["File"], font=("Segoe UI", 10), width=84, state="readonly").grid(row=2, column=1, columnspan=5, sticky="w")

        # buttons
        frame_btn = tk.Frame(self.root, bg="#eef2f7")
        frame_btn.pack(pady=10)

        btn_style = {"font": ("Segoe UI", 11, "bold"), "bg": "#1565C0", "fg": "white", "width": 18, "height": 1}

        tk.Button(frame_btn, text="⬆️ Tải lên hợp đồng", command=self.mo_cua_so_hop_dong_mau, **btn_style).grid(row=0, column=1, padx=10)
        tk.Button(frame_btn, text="🧾 Tạo hợp đồng", command=self.upload_hop_dong, **btn_style).grid(row=0, column=0, padx=10)
        tk.Button(frame_btn, text="📝 Cập nhật", command=self.cap_nhat_hop_dong_btn, **btn_style).grid(row=0, column=2, padx=10)
        tk.Button(frame_btn, text="🗑️ Xóa hợp đồng", command=self.xoa_hop_dong, **btn_style).grid(row=0, column=3, padx=10)
        tk.Button(frame_btn, text="📜 Làm mới", command=self.hien_thi_ds, **btn_style).grid(row=0, column=4, padx=10)
        tk.Button(frame_btn, text="📤 Xuất hợp đồng", command=self.xuat_hop_dong, **btn_style).grid(row=0, column=5, padx=10)

        # danh sách
        frame_list = tk.LabelFrame(self.root, text="📄 Danh sách hợp đồng", font=("Segoe UI", 13, "bold"), bg="white", padx=10, pady=10)
        frame_list.pack(fill="both", expand=True, padx=30, pady=12)

        columns = ["Mã hợp đồng", "Người thuê", "Phòng", "Ngày bắt đầu", "Ngày kết thúc", "Trạng thái", "File"]
        self.tree = ttk.Treeview(frame_list, columns=columns, show="headings", height=12)

        # set column widths để không bị tràn ngang
        column_widths = {
            "Mã hợp đồng": 140,
            "Người thuê": 180,
            "Phòng": 140,
            "Ngày bắt đầu": 150,
            "Ngày kết thúc": 150,
            "Trạng thái": 150,
            "File": 300
        }
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor="center", width=column_widths.get(col, 150), stretch=False)

        # enable horizontal scrollbar so columns are not clipped
        hbar = ttk.Scrollbar(frame_list, orient="horizontal", command=self.tree.xview)
        self.tree.configure(xscrollcommand=hbar.set)
        hbar.pack(side="bottom", fill="x")

        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)

        # show data
        self.hien_thi_ds()

    # helper cập nhật combobox phòng
    def refresh_phong_combobox(self):
        vals = [p.ten_phong for p in self.ql_phong.lay_ds_phong()]
        self.cmb_phong.config(values=vals)

    def mo_cua_so_hop_dong_mau(self):
        TemplateHopDongWindow(self)

    def on_tree_select(self, event):
        sel = self.tree.selection()
        if not sel:
            return
        vals = self.tree.item(sel[0])["values"]
        keys = ["Mã hợp đồng", "Người thuê", "Phòng", "Ngày bắt đầu", "Ngày kết thúc", "Trạng thái", "File"]
        for k, v in zip(keys, vals):
            self.vars[k].set(v)

    def hien_thi_ds(self):
        # cập nhật combobox phòng luôn (phòng có thể thay đổi)
        try:
            self.refresh_phong_combobox()
        except:
            pass

        for i in self.tree.get_children():
            self.tree.delete(i)
        for h in self.ql_hd.lay_ds_hop_dong():
            self.tree.insert("", "end", values=(h.ma_hop_dong, h.ten_nguoi_thue, h.phong, h.ngay_bat_dau, h.ngay_ket_thuc, h.trang_thai, h.file_path))


    # =============================
    # UPLOAD: đổi tên file theo định dạng yêu cầu
    # =============================
    def upload_hop_dong(self):
        fpath = filedialog.askopenfilename(
            title="Chọn file hợp đồng đã điền",
            filetypes=[("Word file", "*.docx"), ("Tất cả", "*.*")]
    )
        if not fpath:
          return

        try:
            # ===== LẤY THÔNG TIN TỪ FILE =====
            info = extract_info_from_docx(fpath)
            ten = info.get("ten_nguoi_thue", "") or self.vars["Người thuê"].get().strip()
            phong = info.get("phong", "") or self.vars["Phòng"].get().strip()
        # ===== TẠO SỐ THỨ TỰ =====
            existing_ids = [h.ma_hop_dong for h in self.ql_hd.lay_ds_hop_dong()]

            numbers = []
            for code in existing_ids:
            # dạng mã cũ / mới đều đọc số ở cuối
                match = re.search(r"HD(\d+)", code)
                if match:
                    numbers.append(int(match.group(1)))

            next_number = (max(numbers) + 1) if numbers else 1
            serial = str(next_number).zfill(3)  # 001, 002, 003...

        # ===== TẠO MÃ HỢP ĐỒNG MỚI =====
            phong_sach = sanitize_for_filename(phong) or "Phong"
            ma = f"HD{serial}_{phong_sach}"

        # ===== NGÀY BẮT ĐẦU / KẾT THÚC =====
            ngay_bd = info.get("ngay_bat_dau", "") or self.vars["Ngày bắt đầu"].get().strip()
            ngay_kt = info.get("ngay_ket_thuc", "") or self.vars["Ngày kết thúc"].get().strip()

        # ===== TÊN FILE LUU =====
            now = datetime.datetime.now().strftime("%d%m%Y")
            ten_sach = sanitize_for_filename(ten) or "Khach"

            newname = f"{ma}_{ten_sach}_{now}.docx"
            dest = os.path.join(CONTRACTS_DIR, newname)
            shutil.copyfile(fpath, dest)
            dest = os.path.abspath(dest)
            # ===== TÍNH TRẠNG THÁI HỢP ĐỒNG =====
            today = datetime.date.today()
            try:
                end_date = datetime.date.fromisoformat(ngay_kt)

                days_to_end = (end_date - today).days       # còn bao nhiêu ngày tới ngày hết hạn
                days_after_end = (today - end_date).days    # đã hết hạn bao nhiêu ngày

                # 1) Còn hạn → Sắp hết hạn nếu dưới 15 ngày
                if days_to_end > 15:
                    trang_thai = "Đã hợp đồng"
                elif 0 <= days_to_end <= 15:
                    trang_thai = "Sắp hết hạn"

                # 2) Đến ngày hết hợp đồng
                elif days_after_end == 0:
                    trang_thai = "Hết hạn"

                # 3) Sau khi hết hạn 1–15 ngày
                elif 1 <= days_after_end <= 15:
                    trang_thai = "Hết hạn"

                # 4) Sau 16–25 ngày → chưa hợp đồng
                elif 16 <= days_after_end <= 25:
                    trang_thai = "Chưa hợp đồng"

                # 5) Sau 25 ngày → chờ xoá
                else:
                    trang_thai = "Chờ xoá"

            except:
                trang_thai = "Đã hợp đồng"

            # ===== TẠO ĐỐI TƯỢNG HỢP ĐỒNG =====
            hd = HopDong(
                ma_hop_dong=ma,
                ten_nguoi_thue=ten,
                phong=phong,
                ngay_bat_dau=ngay_bd,
                ngay_ket_thuc=ngay_kt,
                trang_thai=trang_thai,
                file_path=dest
            )


            if not self.ql_hd.them_hop_dong(hd):
                messagebox.showwarning("Trùng mã", "Mã hợp đồng đã tồn tại, hãy đổi mã khác.")
                return

            # ===== CẬP NHẬT UI =====
            self.vars["Mã hợp đồng"].set(ma)
            self.vars["Người thuê"].set(ten)
            self.vars["Phòng"].set(phong)
            self.vars["Ngày bắt đầu"].set(ngay_bd)
            self.vars["Ngày kết thúc"].set(ngay_kt)
            self.vars["Trạng thái"].set("Đã hợp đồng")
            self.vars["File"].set(dest)

            # ===== CẬP NHẬT NGƯỜI THUÊ =====
            self.cap_nhat_nguoi_thue_tu_info(info, ma, phong)

            # ===== CẬP NHẬT TRẠNG THÁI PHÒNG =====
            if phong:
                for p in self.ql_phong.lay_ds_phong():
                    if p.ten_phong == phong:
                        self.ql_phong.cap_nhat_phong(p.ma_phong, trang_thai="Đang thuê")
                        break

            self.hien_thi_ds()
            messagebox.showinfo("Thành công", f"Đã tải lên và lưu hợp đồng {ma}.")

        except Exception as e:
            messagebox.showerror("Lỗi upload", f"Upload thất bại: {e}")
    def cleanup_hop_dong_qua_han(self):
        today = datetime.date.today()
        to_delete = []

        for hd in self.ql_hd.lay_ds_hop_dong():
            try:
                end_date = datetime.date.fromisoformat(hd.ngay_ket_thuc)
                diff = (today - end_date).days

                if diff > 25:
                    to_delete.append(hd.ma_hop_dong)
            except:
               pass

        for ma in to_delete:
            self.ql_hd.xoa_hop_dong(ma)

    def cap_nhat_nguoi_thue_tu_info(self, info, ma_hop_dong, phong):
        ten = info.get("ten_nguoi_thue", "")
        cmnd = info.get("cmnd", "")
        if not ten and not cmnd:
            return

        found = None
        if cmnd:
            for nt in self.ql_nguoi.lay_ds_nguoi_thue():
                if getattr(nt, "cccd", "") == cmnd:
                    found = nt
                    break
        if not found and ten:
            for nt in self.ql_nguoi.lay_ds_nguoi_thue():
                if getattr(nt, "ten", "") == ten:
                    found = nt
                    break

        if found:
            updates = {"hop_dong": ma_hop_dong}
            if phong:
                updates["phong_thue"] = phong
            self.ql_nguoi.cap_nhat_nguoi_thue(found.ma_nguoi_thue, **updates)
        else:
            ma_nt = f"NT-{uuid.uuid4().hex[:6].upper()}"
            new_nt = NguoiThue(ma_nguoi_thue=ma_nt, ten=ten, sdt="", cccd=cmnd or "", email="", phong_thue=phong or "", trang_thai="Đã thuê", tien_no=0, hop_dong=ma_hop_dong)
            self.ql_nguoi.them_nguoi_thue(new_nt)
            messagebox.showinfo("Cập nhật người thuê", f"Đã tạo mới người thuê: {ten} (Mã: {ma_nt})")

    def cap_nhat_hop_dong_btn(self):
        ma = self.vars["Mã hợp đồng"].get().strip()
        if not ma:
            messagebox.showerror("Lỗi", "Vui lòng nhập hoặc chọn mã hợp đồng cần cập nhật!")
            return

        updates = {
            "ten_nguoi_thue": self.vars["Người thuê"].get().strip() or None,
            "phong": self.vars["Phòng"].get().strip() or None,
            "ngay_bat_dau": self.vars["Ngày bắt đầu"].get().strip() or None,
            "ngay_ket_thuc": self.vars["Ngày kết thúc"].get().strip() or None,
            "trang_thai": self.vars["Trạng thái"].get().strip() or None,
            "file_path": self.vars["File"].get().strip() or None
        }
        if self.ql_hd.cap_nhat_hop_dong(ma, **updates):
            self.hien_thi_ds()
            messagebox.showinfo("Thành công", f"Đã cập nhật hợp đồng {ma}.")
        else:
            messagebox.showerror("Lỗi", "Không tìm thấy hợp đồng để cập nhật.")

    def xoa_hop_dong(self):
        ma = self.vars["Mã hợp đồng"].get().strip()
        if not ma:
            sel = self.tree.selection()
            if not sel:
                messagebox.showwarning("Chưa chọn", "Vui lòng chọn hợp đồng cần xóa.")
                return
            ma = self.tree.item(sel[0])["values"][0]

        if messagebox.askyesno("Xác nhận", f"Bạn có chắc muốn xóa hợp đồng {ma}?"):
            if self.ql_hd.xoa_hop_dong(ma):
                self.hien_thi_ds()
                messagebox.showinfo("Đã xóa", f"Hợp đồng {ma} đã được xóa.")
            else:
                messagebox.showerror("Lỗi", "Không tìm thấy hợp đồng cần xóa.")

    def xuat_hop_dong(self):
        ma = self.vars["Mã hợp đồng"].get().strip()
        h = None
        if ma:
            h = self.ql_hd.tim_hop_dong(ma)
        else:
            sel = self.tree.selection()
            if sel:
                ma_sel = self.tree.item(sel[0])["values"][0]
                h = self.ql_hd.tim_hop_dong(ma_sel)

        if not h:
            messagebox.showwarning("Chưa chọn", "Vui lòng chọn hợp đồng để xuất.")
            return

        if not h.file_path or not os.path.exists(h.file_path):
            messagebox.showerror("Lỗi", "File hợp đồng không tồn tại trên hệ thống.")
            return

        # tạo tên xuất: bỏ phần ngày
        ten_sach = sanitize_for_filename(h.ten_nguoi_thue) or "Khach"
        phong_sach = sanitize_for_filename(h.phong) or "Phong"
        export_name = f"HD{h.ma_hop_dong}_{ten_sach}_{phong_sach}.docx"

        dest = filedialog.asksaveasfilename(title="Chọn nơi lưu file hợp đồng", defaultextension=".docx", initialfile=export_name, filetypes=[("Word file", "*.docx"), ("Tất cả", "*.*")])
        if not dest:
            return
        try:
            shutil.copyfile(h.file_path, dest)
            messagebox.showinfo("Xuất thành công", f"Đã xuất hợp đồng tới:\n{dest}")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể xuất hợp đồng: {e}")


# =============================
# RUN
# =============================
#if __name__ == "__main__":
 #   root = tk.Tk()
  #  app = QuanLyHopDongUI(root)
   # root.mainloop()