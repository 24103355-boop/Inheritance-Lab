import tkinter as tk
from tkinter import ttk, messagebox
import csv, os
import re
from phongtro import QuanLyPhongTro
from option import Menu3Gach  # import module menu 3 gạch

# =============================
# 1️⃣ Lớp Người Thuê
# =============================
class NguoiThue:
    def __init__(self, ma_nguoi_thue, ten, sdt, cccd, email, phong_thue, trang_thai, tien_no=0, hop_dong="Chưa hợp đồng"):
        self.ma_nguoi_thue = ma_nguoi_thue
        self.ten = ten
        self.sdt = sdt
        self.cccd = cccd
        self.email = email
        self.phong_thue = phong_thue
        self.trang_thai = trang_thai
        self.tien_no = tien_no
        self.hop_dong = hop_dong

    def xem_thong_tin(self):
        return (f"Mã người thuê: {self.ma_nguoi_thue}\n"
                f"Họ tên: {self.ten}\n"
                f"SĐT: {self.sdt}\n"
                f"Email: {self.email}\n"
                f"CCCD: {self.cccd}\n"
                f"Phòng thuê: {self.phong_thue}\n"
                f"Trạng thái: {self.trang_thai}\n"
                f"Số tiền nợ: {self.tien_no} VNĐ\n"
                f"Hợp đồng: {self.hop_dong}")

    def cap_nhat_thong_tin(self, **kwargs):
        for k, v in kwargs.items():
            if v is not None and hasattr(self, k):
                setattr(self, k, v)


# =============================
# 2️⃣ Quản lý danh sách người thuê
# =============================
class QuanLyNguoiThue:
    FILE_CSV = "nguoi_thue.csv"

    def __init__(self):
        self.ds_nguoi_thue = []
        self.tao_file_csv_neu_chua_co()
        self.doc_file_csv()

    def tao_file_csv_neu_chua_co(self):
        if not os.path.exists(self.FILE_CSV):
            with open(self.FILE_CSV, "w", encoding="utf-8", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["Mã người thuê", "Họ tên", "SĐT", "CCCD", "Email", "Phòng thuê", "Trạng thái", "Tiền nợ", "Hợp đồng"])

    def ghi_file_csv(self):
        with open(self.FILE_CSV, "w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Mã người thuê", "Họ tên", "SĐT", "CCCD", "Email", "Phòng thuê", "Trạng thái", "Tiền nợ", "Hợp đồng"])
            for n in self.ds_nguoi_thue:
                writer.writerow([n.ma_nguoi_thue, n.ten, n.sdt, n.cccd, n.email, n.phong_thue, n.trang_thai, n.tien_no, n.hop_dong])

    def doc_file_csv(self):
        try:
            with open(self.FILE_CSV, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    nguoi = NguoiThue(
                        ma_nguoi_thue=row["Mã người thuê"],
                        ten=row["Họ tên"],
                        sdt=row["SĐT"],
                        cccd=row["CCCD"],
                        email=row["Email"],
                        phong_thue=row["Phòng thuê"],
                        trang_thai=row["Trạng thái"],
                        tien_no=float(row["Tiền nợ"]),
                        hop_dong=row["Hợp đồng"]
                    )
                    self.ds_nguoi_thue.append(nguoi)
        except Exception as e:
            print("⚠️ Lỗi đọc file CSV:", e)

    def them_nguoi_thue(self, nguoi):
        for n in self.ds_nguoi_thue:
            if n.ma_nguoi_thue == nguoi.ma_nguoi_thue:
                return False
        self.ds_nguoi_thue.append(nguoi)
        self.ghi_file_csv()
        return True

    def tim_nguoi_thue(self, ma):
        for n in self.ds_nguoi_thue:
            if n.ma_nguoi_thue == ma:
                return n
        return None

    def xoa_nguoi_thue(self, ma):
        n = self.tim_nguoi_thue(ma)
        if n:
            self.ds_nguoi_thue.remove(n)
            self.ghi_file_csv()
            return True
        return False

    def cap_nhat_nguoi_thue(self, ma, **kwargs):
        n = self.tim_nguoi_thue(ma)
        if n:
            n.cap_nhat_thong_tin(**kwargs)
            self.ghi_file_csv()
            return True
        return False

    def lay_ds_nguoi_thue(self):
        return self.ds_nguoi_thue


# =============================
# 3️⃣ Giao diện người thuê
# =============================
class QuanLyNguoiThueUI:
    def __init__(self, root, controller):
        self.root = root
        self.controller = controller
        self.root.title("👥 Quản Lý Người Thuê")
        self.root.geometry("1000x700")
        self.root.configure(bg="#f3f3f3")

        self.ql = QuanLyNguoiThue()
        self.ql_phong = QuanLyPhongTro()

        # === Menu 3 gạch tái sử dụng ===
        self.menu = Menu3Gach(self, self.controller, active_menu="Quản lý người thuê")

        # === Form nhập liệu ===
        self.build_form()
        # === Danh sách ===
        self.build_tree()
        self.hien_thi_ds()

    def build_form(self):
        frame_input = tk.LabelFrame(self.root, text="📋 Thông tin người thuê", font=("Segoe UI", 12, "bold"),
                                    padx=10, pady=10, bg="white")
        frame_input.pack(fill="x", padx=20, pady=10)

        labels = ["Mã người thuê", "Họ tên", "SĐT", "CCCD", "Email", "Phòng thuê", "Trạng thái", "Tiền nợ", "Hợp đồng"]
        self.vars = {l: tk.StringVar() for l in labels}

        row = 0
        for i, l in enumerate(labels):
            tk.Label(frame_input, text=f"{l}:", font=("Segoe UI", 11), bg="white").grid(
                row=row, column=(i % 4) * 2, padx=5, pady=5, sticky="e")

            if l == "Phòng thuê":
                ttk.Combobox(frame_input, textvariable=self.vars[l],
                             values=[p.ten_phong for p in self.ql_phong.lay_ds_phong()],
                             font=("Segoe UI", 11), width=18,
                             state="readonly").grid(row=row, column=(i % 4) * 2 + 1, padx=5, pady=5)

            elif l == "Trạng thái":
                ttk.Combobox(frame_input, textvariable=self.vars[l],
                             values=["Chưa thuê", "Đã thuê"],
                             font=("Segoe UI", 11), width=18,
                             state="readonly").grid(row=row, column=(i % 4) * 2 + 1, padx=5, pady=5)

            elif l == "Hợp đồng":
                ttk.Combobox(
                    frame_input,
                    textvariable=self.vars[l],
                    values=["Đã hợp đồng", "Chưa hợp đồng", "Sắp hết hạn", "Hết hạn"],
                    font=("Segoe UI", 11),
                    width=18,
                    state="readonly"
                ).grid(row=row, column=(i % 4) * 2 + 1, padx=5, pady=5)

            else:
                tk.Entry(frame_input, textvariable=self.vars[l], font=("Segoe UI", 11),
                         width=20).grid(row=row, column=(i % 4) * 2 + 1, padx=5, pady=5)

            if i % 4 == 3:
                row += 1

        # Nút chức năng
        frame_btn = tk.Frame(self.root, bg="#f3f3f3")
        frame_btn.pack(pady=5)
        style = {"font": ("Segoe UI", 11, "bold"), "bg": "#1565C0", "fg": "white", "width": 15, "height": 1}
        tk.Button(frame_btn, text="➕ Thêm", command=self.them, **style).grid(row=0, column=0, padx=5)
        tk.Button(frame_btn, text="🔍 Tìm kiếm", command=self.tim, **style).grid(row=0, column=1, padx=5)
        tk.Button(frame_btn, text="📝 Cập nhật", command=self.cap_nhat, **style).grid(row=0, column=2, padx=5)
        tk.Button(frame_btn, text="🗑️ Xóa", command=self.xoa, **style).grid(row=0, column=3, padx=5)
        tk.Button(frame_btn, text="📜 Làm mới", command=self.hien_thi_ds, **style).grid(row=0, column=4, padx=5)

    def build_tree(self):
        frame_list = tk.LabelFrame(self.root, text="📄 Danh sách người thuê", font=("Segoe UI", 12, "bold"),
                                   padx=10, pady=10, bg="white")
        frame_list.pack(fill="both", expand=True, padx=20, pady=10)

        labels = ["Mã người thuê", "Họ tên", "SĐT", "CCCD", "Email", "Phòng thuê", "Trạng thái", "Tiền nợ", "Hợp đồng"]
        self.tree = ttk.Treeview(frame_list, columns=labels, show="headings", height=10)
        for col in labels:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor="center", width=100)
        self.tree.pack(fill="both", expand=True)

    # =============================
    # 🎛️ Callback menu
    # =============================
    def chon_menu(self, ten_menu):
        if ten_menu == "Trang chủ":
            self.root.destroy()
        elif ten_menu == "Quản lý phòng trọ":
            print("Chuyển sang quản lý phòng trọ")
        elif ten_menu == "Quản lý người thuê":
            print("Đang ở quản lý người thuê")
        elif ten_menu == "Quản lý hợp đồng":
            print("Chuyển sang quản lý hợp đồng")

    # =============================
    # CRUD
    # =============================
    def them(self):
        # Các trường bắt buộc
        required = ["Mã người thuê", "Họ tên", "SĐT", "CCCD", "Email", "Phòng thuê"]

        # Kiểm tra trống
        missing = [f for f in required if not self.vars[f].get().strip()]
        if missing:
            messagebox.showerror("Lỗi", f"Vui lòng nhập đầy đủ các trường: {', '.join(missing)}")
            return

        sdt = self.vars["SĐT"].get().strip()
        email = self.vars["Email"].get().strip()
        cccd = self.vars["CCCD"].get().strip()

        # Kiểm tra số điện thoại VN
        sdt_regex = r'^(03|05|07|08|09)\d{8}$'
        if not re.match(sdt_regex, sdt):
            messagebox.showerror("Lỗi", "Số điện thoại phải gồm 10 số và bắt đầu bằng 03,05,07,08,09.")
            return

        # Email
        email_regex = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        if not re.match(email_regex, email):
            messagebox.showerror("Lỗi", "Email không đúng định dạng.")
            return

        # CCCD
        if not (cccd.isdigit() and len(cccd) == 12):
            messagebox.showerror("Lỗi", "CCCD phải gồm đúng 12 chữ số.")
            return

        # Tiền nợ
        try:
            tien_no_val = float(self.vars["Tiền nợ"].get().strip() or 0)
        except ValueError:
            messagebox.showerror("Lỗi", "Tiền nợ phải là số.")
            return

        try:
            n = NguoiThue(
                ma_nguoi_thue=self.vars["Mã người thuê"].get().strip(),
                ten=self.vars["Họ tên"].get().strip(),
                sdt=sdt,
                cccd=cccd,
                email=email,
                phong_thue=self.vars["Phòng thuê"].get().strip(),
                trang_thai=self.vars["Trạng thái"].get().strip() or "Chưa thuê",
                tien_no=tien_no_val,
                hop_dong=self.vars["Hợp đồng"].get().strip() or "Chưa hợp đồng"
            )
            if self.ql.them_nguoi_thue(n):
                messagebox.showinfo("✅ Thành công", "Đã thêm người thuê")
                self.hien_thi_ds()
            else:
                messagebox.showwarning("⚠️", "Mã người thuê đã tồn tại!")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Dữ liệu không hợp lệ: {e}")

    def tim(self):
        ma = self.vars["Mã người thuê"].get().strip()
        if not ma:
            messagebox.showwarning("Lỗi", "Nhập mã người thuê để tìm!")
            return
        n = self.ql.tim_nguoi_thue(ma)
        if n:
            messagebox.showinfo("Thông tin", n.xem_thong_tin())
        else:
            messagebox.showerror("Không tìm thấy", "Không có người thuê này!")

    def cap_nhat(self):
        ma = self.vars["Mã người thuê"].get().strip()
        if not ma:
            messagebox.showerror("Lỗi", "Vui lòng nhập mã người thuê cần cập nhật!")
            return
        kwargs = {k.lower().replace(" ", "_"): v.get() or None for k, v in self.vars.items()}
        if self.ql.cap_nhat_nguoi_thue(ma, **kwargs):
            messagebox.showinfo("Thành công", "Đã cập nhật thông tin")
            self.hien_thi_ds()
        else:
            messagebox.showerror("Lỗi", "Không tìm thấy người thuê cần cập nhật!")

    def xoa(self):
        ma = self.vars["Mã người thuê"].get().strip()
        if self.ql.xoa_nguoi_thue(ma):
            messagebox.showinfo("Đã xóa", f"Người thuê {ma} đã được xóa")
            self.hien_thi_ds()
        else:
            messagebox.showerror("Lỗi", "Không tìm thấy người thuê!")

    def hien_thi_ds(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        for n in self.ql.lay_ds_nguoi_thue():
            self.tree.insert("", "end", values=(
                n.ma_nguoi_thue, n.ten, n.sdt, n.cccd, n.email,
                n.phong_thue, n.trang_thai, n.tien_no, n.hop_dong))


# =============================
# 🔰 Chạy chương trình
# =============================
#if __name__ == "__main__":
  #  root = tk.Tk()
   # app = QuanLyNguoiThueUI(root)
    #root.mainloop()
