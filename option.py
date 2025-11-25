import tkinter as tk

class Menu3Gach:
    def __init__(self, app, controller, active_menu="Trang chủ"):
        self.app = app
        self.controller = controller
        self.active_menu = active_menu
        self.menu_open = False
        self.menu_x = -200
        self.menu_buttons = {}

        self._tao_header()
        self._tao_side_menu()

        # 🔥 RẤT QUAN TRỌNG: luôn đưa menu lên trên UI
        self.menu_frame.lift()
        self.side_menu.lift()

    def _tao_header(self):
        self.menu_frame = tk.Frame(self.controller.root, bg="#1565C0", height=50)
        self.menu_frame.pack(fill="x", side="top")

        self.menu_button = tk.Button(
            self.menu_frame, text="☰", font=("Segoe UI", 16, "bold"),
            bg="#42A5F5", fg="white", bd=0, activebackground="#1E88E5",
            command=self.toggle_menu
        )
        self.menu_button.pack(side="left", padx=15)

        self.title_label = tk.Label(
            self.menu_frame, text=f"{self.active_menu}",
            font=("Segoe UI", 16, "bold"), bg="#1565C0", fg="white"
        )
        self.title_label.pack(side="left", padx=10)

    def _tao_side_menu(self):
        self.side_menu = tk.Frame(self.controller.root, bg="#E0E0E0", width=200, height=800)
        self.side_menu.place(x=self.menu_x, y=50)

        self._add_menu("Trang chủ", "🏡 Trang chủ")
        self._add_menu("Quản lý phòng trọ", "🏢 Quản lý phòng trọ")
        self._add_menu("Quản lý người thuê", "👤 Quản lý người thuê")
        self._add_menu("Quản lý hợp đồng", "📑 Quản lý hợp đồng")

    def _add_menu(self, name, text):
        active = (name == self.active_menu)
        btn = tk.Button(
            self.side_menu, text=text,
            font=("Segoe UI", 12, "bold" if active else "normal"),
            bg="#1565C0" if active else "#E0E0E0",
            fg="white" if active else "black",
            anchor="w", bd=0,
            command=lambda n=name: self._chon_menu(n)
        )
        btn.pack(fill="x", pady=5)
        self.menu_buttons[name] = btn

    # Animation mở / đóng
    def toggle_menu(self):
        target = 0 if not self.menu_open else -200
        self._animate_menu(target)
        self.menu_open = not self.menu_open

    def _animate_menu(self, target):
        step = 20 if target > self.menu_x else -20
        if (step > 0 and self.menu_x < target) or (step < 0 and self.menu_x > target):
            self.menu_x += step
            self.side_menu.place(x=self.menu_x, y=50)
            self.side_menu.lift()
            self.menu_frame.lift()
            self.controller.root.after(10, lambda: self._animate_menu(target))
        else:
            self.menu_x = target
            self.side_menu.place(x=self.menu_x, y=50)
            self.side_menu.lift()
            self.menu_frame.lift()

    def _chon_menu(self, ten_menu):
        for name, btn in self.menu_buttons.items():
            if name == ten_menu:
                btn.configure(bg="#1565C0", fg="white", font=("Segoe UI", 12, "bold"))
            else:
                btn.configure(bg="#E0E0E0", fg="black", font=("Segoe UI", 12))

        self.controller.switch_to(ten_menu)
