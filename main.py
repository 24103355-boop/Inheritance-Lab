import tkinter as tk
from phongtro import QuanLyPhongTroUI
from nguoithue import QuanLyNguoiThueUI
from hopdong import QuanLyHopDongUI

class AppController:
    def __init__(self):
        self.root = tk.Tk()
        self.current_ui = None

    def run(self):
        self.switch_to("Quản lý phòng trọ")
        self.root.mainloop()

    def switch_to(self, name):
        if self.current_ui:
            for widget in self.root.winfo_children():
                widget.destroy()

        if name == "Trang chủ":
            self.root.destroy()
            return

        if name == "Quản lý phòng trọ":
            self.current_ui = QuanLyPhongTroUI(self.root, controller=self)

        elif name == "Quản lý người thuê":
            self.current_ui = QuanLyNguoiThueUI(self.root, controller=self)

        elif name == "Quản lý hợp đồng":
            self.current_ui = QuanLyHopDongUI(self.root, controller=self)

if __name__ == "__main__":
   AppController().run()
