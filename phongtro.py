import tkinter as tk
from tkinter import ttk, messagebox
from option import Menu3Gach
import csv, os

# =============================
# 1️⃣ Lớp Phòng trọ
# =============================
class PhongTro:
    def __init__(self, ma_phong, ten_phong, gia_thue, dien_tich, trang_thai="Trống", ghi_chu=""):
        self.ma_phong = ma_phong
        self.ten_phong = ten_phong
        self.gia_thue = gia_thue
        self.dien_tich = dien_tich
        self.trang_thai = trang_thai
        self.ghi_chu = ghi_chu

    def xem_thong_tin(self):
        return (
            f"Mã phòng: {self.ma_phong}\n"
            f"Tên phòng: {self.ten_phong}\n"
            f"Giá thuê: {self.gia_thue}\n"
            f"Diện tích: {self.dien_tich} m²\n"
            f"Trạng thái: {self.trang_thai}\n"
            f"Ghi chú: {self.ghi_chu}"
        )

    def cap_nhat_thong_tin(self, ten_phong=None, gia_thue=None, dien_tich=None, trang_thai=None, ghi_chu=None):
        if ten_phong:
            self.ten_phong = ten_phong
        if gia_thue:
            self.gia_thue = gia_thue
        if dien_tich:
            self.dien_tich = dien_tich
        if trang_thai:
            self.trang_thai = trang_thai
        if ghi_chu is not None:
            self.ghi_chu = ghi_chu


# =============================
# 2️⃣ Lớp Quản lý phòng trọ
# =============================
class QuanLyPhongTro:
    FILE_CSV = "danh_sach_phong.csv"

    def __init__(self):
        self.ds_phong = []
        self.tao_file_csv_neu_chua_co()
        self.doc_file_csv()

    def tao_file_csv_neu_chua_co(self):
        if not os.path.exists(self.FILE_CSV):
            with open(self.FILE_CSV, "w", encoding="utf-8", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["Mã phòng", "Tên phòng", "Giá thuê", "Diện tích", "Trạng thái", "Ghi chú"])

    def ghi_file_csv(self):
        with open(self.FILE_CSV, "w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Mã phòng", "Tên phòng", "Giá thuê", "Diện tích", "Trạng thái", "Ghi chú"])
            for p in self.ds_phong:
                writer.writerow([p.ma_phong, p.ten_phong, p.gia_thue, p.dien_tich, p.trang_thai, p.ghi_chu])

    def doc_file_csv(self):
        try:
            with open(self.FILE_CSV, mode="r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    phong = PhongTro(
                        ma_phong=row["Mã phòng"],
                        ten_phong=row["Tên phòng"],
                        gia_thue=float(row["Giá thuê"]),
                        dien_tich=row["Diện tích"],
                        trang_thai=row["Trạng thái"],
                        ghi_chu=row.get("Ghi chú", "")
                    )
                    self.ds_phong.append(phong)
        except Exception as e:
            print("⚠️ Lỗi đọc file CSV:", e)

    def them_phong(self, phong):
        for p in self.ds_phong:
            if p.ma_phong == phong.ma_phong:
                return False
        self.ds_phong.append(phong)
        self.ghi_file_csv()
        return True

    def tim_phong(self, ma_phong):
        for p in self.ds_phong:
            if p.ma_phong == ma_phong:
                return p
        return None

    def xoa_phong(self, ma_phong):
        phong = self.tim_phong(ma_phong)
        if phong:
            self.ds_phong.remove(phong)
            self.ghi_file_csv()
            return True
        return False

    def cap_nhat_phong(self, ma_phong, ten_phong=None, gia_thue=None, dien_tich=None, trang_thai=None, ghi_chu=None):
        phong = self.tim_phong(ma_phong)
        if phong:
            phong.cap_nhat_thong_tin(ten_phong, gia_thue, dien_tich, trang_thai, ghi_chu)
            self.ghi_file_csv()
            return True
        return False

    def lay_ds_phong(self):
        return self.ds_phong


# =============================
# 3️⃣ Giao diện Tkinter
# =============================
class QuanLyPhongTroUI:
    def __init__(self, root, controller):
        self.root = root
        self.controller = controller
        self.root.title("🏠 Quản Lý Phòng Trọ")
        self.root.geometry("1700x800")
        self.root.configure(bg="#f3f3f3")

        self.ql = QuanLyPhongTro()
        self.build_ui()

    def build_ui(self):
        # === Menu 3 gạch tái sử dụng ===
        self.menu = Menu3Gach(self, self.controller, active_menu="Quản lý phòng trọ")

        # === FORM NHẬP THÔNG TIN ===
        frame_input = tk.LabelFrame(self.root, text="📋 Thông tin phòng", font=("Segoe UI", 12, "bold"),
                                    bg="#ffffff", padx=15, pady=10, labelanchor="n", fg="#444")
        frame_input.pack(fill="x", padx=30, pady=15)

        tk.Label(frame_input, text="Mã phòng:", font=("Segoe UI", 11), bg="white").grid(row=0, column=0, padx=10, pady=5, sticky="e")
        tk.Label(frame_input, text="Tên phòng:", font=("Segoe UI", 11), bg="white").grid(row=0, column=2, padx=10, pady=5, sticky="e")
        tk.Label(frame_input, text="Giá thuê (VNĐ):", font=("Segoe UI", 11), bg="white").grid(row=1, column=0, padx=10, pady=5, sticky="e")
        tk.Label(frame_input, text="Diện tích (m²):", font=("Segoe UI", 11), bg="white").grid(row=1, column=2, padx=10, pady=5, sticky="e")
        tk.Label(frame_input, text="Trạng thái:", font=("Segoe UI", 11), bg="white").grid(row=2, column=0, padx=10, pady=5, sticky="e")
        tk.Label(frame_input, text="Ghi chú:", font=("Segoe UI", 11), bg="white").grid(row=2, column=2, padx=10, pady=5, sticky="e")

        # Các biến
        self.ma_phong_var = tk.StringVar()
        self.ten_phong_var = tk.StringVar()
        self.gia_thue_var = tk.StringVar()
        self.dien_tich_var = tk.StringVar()
        self.trang_thai_var = tk.StringVar(value="Trống")
        self.ghi_chu_var = tk.StringVar()

        # Các ô nhập liệu
        entry_opts = {"font": ("Segoe UI", 11), "width": 20}
        tk.Entry(frame_input, textvariable=self.ma_phong_var, **entry_opts).grid(row=0, column=1, padx=10)
        tk.Entry(frame_input, textvariable=self.ten_phong_var, **entry_opts).grid(row=0, column=3, padx=10)
        tk.Entry(frame_input, textvariable=self.gia_thue_var, **entry_opts).grid(row=1, column=1, padx=10)
        tk.Entry(frame_input, textvariable=self.dien_tich_var, **entry_opts).grid(row=1, column=3, padx=10)
        ttk.Combobox(frame_input, textvariable=self.trang_thai_var,
                     values=["Trống", "Đang thuê", "Bảo trì"],
                     font=("Segoe UI", 11), width=18, state="readonly").grid(row=2, column=1, padx=10)
        tk.Entry(frame_input, textvariable=self.ghi_chu_var, **entry_opts).grid(row=2, column=3, padx=10)

        # === NÚT CHỨC NĂNG ===
        frame_btn = tk.Frame(self.root, bg="#f3f3f3")
        frame_btn.pack(pady=10)
        style = {"font": ("Segoe UI", 11, "bold"), "bg": "#1565C0", "fg": "white", "width": 15, "height": 1}
        tk.Button(frame_btn, text="➕ Thêm phòng", command=self.them_phong, **style).grid(row=0, column=0, padx=10)
        tk.Button(frame_btn, text="🔍 Tìm phòng", command=self.tim_phong, **style).grid(row=0, column=1, padx=10)
        tk.Button(frame_btn, text="📝 Cập nhật", command=self.cap_nhat_phong, **style).grid(row=0, column=2, padx=10)
        tk.Button(frame_btn, text="🗑️ Xóa phòng", command=self.xoa_phong, **style).grid(row=0, column=3, padx=10)
        tk.Button(frame_btn, text="📜 Làm mới", command=self.hien_thi_ds_phong, **style).grid(row=0, column=4, padx=10)

        # === DANH SÁCH PHÒNG ===
        frame_list = tk.LabelFrame(self.root, text="📄 Danh sách phòng trọ", font=("Segoe UI", 12, "bold"),
                                   bg="#ffffff", padx=10, pady=10, labelanchor="n", fg="#444")
        frame_list.pack(fill="both", expand=True, padx=30, pady=10)

        columns = ("Mã phòng", "Tên phòng", "Giá thuê", "Diện tích", "Trạng thái", "Ghi chú")
        self.tree = ttk.Treeview(frame_list, columns=columns, show="headings", height=10)

        # ✅ Tất cả cột cùng độ rộng 150, căn giữa
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor="center", width=245, stretch=False)

        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<Button-1>", self.disable_column_resize)
        self.hien_thi_ds_phong()

    # ============================
    # 🚀 Các hàm chức năng
    # ============================
    def chon_menu(self, ten_menu):
        if ten_menu == "Trang chủ":
            self.root.destroy()
        elif ten_menu == "Quản lý phòng trọ":
            print("Chuyển sang quản lý phòng trọ")
        elif ten_menu == "Quản lý người thuê":
            print("Đang ở quản lý người thuê")
        elif ten_menu == "Quản lý hợp đồng":
            print("Chuyển sang quản lý hợp đồng")
    def them_phong(self):
        ma = self.ma_phong_var.get().strip()
        ten = self.ten_phong_var.get().strip()
        gia = self.gia_thue_var.get().strip()
        dien_tich = self.dien_tich_var.get().strip()
        tt = self.trang_thai_var.get().strip()
        gc = self.ghi_chu_var.get().strip()

        if not ma or not ten or not gia or not dien_tich:
            messagebox.showerror("Lỗi", "Vui lòng nhập đầy đủ thông tin!")
            return
        try:
            gia = float(gia)
        except ValueError:
            messagebox.showerror("Lỗi", "Giá thuê phải là số!")
            return

        phong = PhongTro(ma, ten, gia, dien_tich, tt, gc)
        if self.ql.them_phong(phong):
            messagebox.showinfo("Thành công", f"Đã thêm phòng {ten}")
            self.hien_thi_ds_phong()
        else:
            messagebox.showwarning("Trùng mã", "Mã phòng đã tồn tại!")

    def tim_phong(self):
        ma = self.ma_phong_var.get().strip()
        phong = self.ql.tim_phong(ma)
        if phong:
            messagebox.showinfo("Thông tin phòng", phong.xem_thong_tin())
        else:
            messagebox.showerror("Không tìm thấy", "Không tồn tại phòng này!")

    def cap_nhat_phong(self):
        ma = self.ma_phong_var.get().strip()
        ten = self.ten_phong_var.get().strip()
        gia = self.gia_thue_var.get().strip()
        dien_tich = self.dien_tich_var.get().strip()
        tt = self.trang_thai_var.get().strip()
        gc = self.ghi_chu_var.get().strip()

        if not ma:
            messagebox.showerror("Lỗi", "Vui lòng nhập mã phòng cần cập nhật!")
            return
        if gia:
            try:
                gia = float(gia)
            except ValueError:
                messagebox.showerror("Lỗi", "Giá thuê phải là số!")
                return

        if self.ql.cap_nhat_phong(ma, ten_phong=ten or None, gia_thue=gia or None, dien_tich=dien_tich or None, trang_thai=tt or None, ghi_chu=gc):
            messagebox.showinfo("Thành công", "Đã cập nhật thông tin phòng.")
            self.hien_thi_ds_phong()
        else:
            messagebox.showerror("Lỗi", "Không tìm thấy phòng cần cập nhật!")

    def xoa_phong(self):
        ma = self.ma_phong_var.get().strip()
        if not ma:
            messagebox.showwarning("Lỗi", "Vui lòng nhập mã phòng cần xóa!")
            return
        if self.ql.xoa_phong(ma):
            messagebox.showinfo("Đã xóa", f"Đã xóa phòng {ma}")
            self.hien_thi_ds_phong()
        else:
            messagebox.showerror("Lỗi", "Không tìm thấy phòng cần xóa!")

    def hien_thi_ds_phong(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        for p in self.ql.lay_ds_phong():
            self.tree.insert("", "end", values=(p.ma_phong, p.ten_phong, p.gia_thue, p.dien_tich, p.trang_thai, p.ghi_chu))

    def disable_column_resize(self, event):
        region = self.tree.identify_region(event.x, event.y)
        if region == "separator":
            return "break"


#if __name__ == "__main__":
#    root = tk.Tk()
#    app = QuanLyPhongTroUI(root)
#    root.mainloop()