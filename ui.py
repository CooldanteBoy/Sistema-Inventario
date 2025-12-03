import tkinter as tk
from tkinter import ttk, messagebox

from database import Database
from models import User
from PIL import Image, ImageTk

def center_window(window, width, height):
    window.update_idletasks()
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()

    x = int((screen_width / 2) - (width / 2))
    y = int((screen_height / 2) - (height / 2))

    window.geometry(f"{width}x{height}+{x}+{y}")


# ==============================
#  VENTANA DE LOGIN BONITA
# ==============================

class LoginWindow(tk.Tk):
    def __init__(self, db: Database):
        super().__init__()
        self.db = db

        self.title("Inventario - Inicio de sesión")
        self.configure(bg="#015294")
        center_window(self, 700, 520)

        self.logo_img = None  # por si usas un logo en el login
        self._build_widgets()

    def _build_widgets(self):
        self.configure(bg="#015294")

        # ---------- TARJETA BLANCA ----------
        card = tk.Frame(
            self,
            bg="white",
            bd=0,
            relief="flat",
            highlightthickness=1,
            highlightbackground="#cccccc"
        )
        card.pack(expand=True, padx=40, pady=40, fill="both")

        content = tk.Frame(card, bg="white")
        content.place(relx=0.5, rely=0.5, anchor="center")

        # ---------- LOGO ARRIBA ----------
        try:
            img = Image.open("logo.png")
            w, h = img.size
            max_w = 850
            if w > max_w:
                ratio = max_w / w
                img = img.resize((int(w * ratio), int(h * ratio)))
            self.logo_img = ImageTk.PhotoImage(img)
            tk.Label(content, image=self.logo_img, bg="white").pack(pady=(0, 20))
        except Exception:
            tk.Label(
                content,
                text="SISTEMA DE INVENTARIO",
                font=("Arial", 16, "bold"),
                bg="white"
            ).pack(pady=(0, 20))

        # ---------- FORMULARIO (labels a la izquierda, cajas a la derecha) ----------
        form = tk.Frame(content, bg="white")
        form.pack(pady=10)

        # Usuario
        tk.Label(
            form, text="Usuario:", font=("Arial", 12), bg="white"
        ).grid(row=0, column=0, padx=10, pady=8, sticky="e")

        self.entry_user = ttk.Entry(form, width=28)
        self.entry_user.grid(row=0, column=1, padx=10, pady=8)

        # Contraseña
        tk.Label(
            form, text="Contraseña:", font=("Arial", 12), bg="white"
        ).grid(row=1, column=0, padx=10, pady=8, sticky="e")

        self.entry_pass = ttk.Entry(form, width=28, show="*")
        self.entry_pass.grid(row=1, column=1, padx=10, pady=8)

        form.columnconfigure(1, weight=1)

        tk.Button(
            content,
            text="Ingresar",
            bg="#d99e30",
            fg="black",
            relief="flat",
            activebackground="#c28a27",
            font=("Arial", 12, "bold"),
            width=20,
            command=self._on_login
        ).pack(pady=(20, 0))

    def _on_login(self):
        username = self.entry_user.get().strip()
        password = self.entry_pass.get()

        if not username or not password:
            messagebox.showwarning("Advertencia", "Ingrese usuario y contraseña.")
            return

        user = self.db.authenticate_user(username, password)
        if user is None:
            messagebox.showerror("Error", "Usuario o contraseña incorrectos.")
            return

        # Login correcto: cerrar ventana de login y abrir la principal
        self.destroy()
        main = MainWindow(self.db, user)
        main.mainloop()

# ==============================
#  VENTANA PRINCIPAL
# ==============================

class MainWindow(tk.Tk):
    def __init__(self, db: Database, user: User):
        super().__init__()
        self.db = db
        self.user = user

        self.title(f"Sistema de Inventario - {user.username} ({user.role})")
        self.configure(bg="#015294")
        center_window(self, 900, 550)

        self.current_view = None
        self._build_widgets()

    def _build_widgets(self):
        outer = tk.Frame(self, bg="#015294")
        outer.pack(fill="both", expand=True, padx=20, pady=20)

        card = tk.Frame(
            outer,
            bg="white",
            bd=0,
            relief="flat",
            highlightthickness=1,
            highlightbackground="#cccccc",
        )
        card.pack(fill="both", expand=True)

        self.content_frame = tk.Frame(card, bg="white")
        self.content_frame.pack(fill="both", expand=True, pady=(20, 10), padx=20)

        self.home_view = HomeView(self.content_frame)
        self.products_view = ProductsView(self.content_frame, self.db, self.user)
        self.warehouses_view = WarehousesView(self.content_frame, self.db, self.user)

        btn_frame = tk.Frame(card, bg="white")
        btn_frame.pack(side="bottom", pady=20)

        nav_frame = tk.Frame(btn_frame, bg="white")
        nav_frame.pack(side="left")

        logout_frame = tk.Frame(btn_frame, bg="white")
        logout_frame.pack(side="right")

        btn_style = {
            "font": ("Arial", 11, "bold"),
            "bg": "#f8bb00",
            "fg": "white",
            "activebackground": "#d9a100",
            "activeforeground": "white",
            "relief": "flat",
            "width": 12,
            "height": 1,
            "bd": 1,
        }

        tk.Button(btn_frame, text="Inicio", command=self.show_home, **btn_style).pack(side="left", padx=8)
        tk.Button(btn_frame, text="Productos", command=self.show_products, **btn_style).pack(side="left", padx=8)
        tk.Button(btn_frame, text="Almacenes", command=self.show_warehouses, **btn_style).pack(side="left", padx=8)
        tk.Button(logout_frame,text="Cerrar sesión",command=self.logout,**btn_style).pack(side="right", padx=8)

        self.show_home()

    def logout(self):
        self.destroy()
        login = LoginWindow(self.db)
        login.mainloop()

    def _switch_view(self, frame: tk.Frame):
        if self.current_view is not None:
            self.current_view.pack_forget()
        self.current_view = frame
        self.current_view.pack(fill="both", expand=True)

    def show_home(self):
        self._switch_view(self.home_view)

    def show_products(self):
        self._switch_view(self.products_view)

    def show_warehouses(self):
        self._switch_view(self.warehouses_view)

# ==============================
#  VISTA: HOME
# ==============================

class HomeView(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg="white")

        self.logo_img = None
        try:
            img = Image.open("logo.png")
            w, h = img.size

            max_width = 600
            if w > max_width:
                ratio = max_width / w
                new_size = (int(w * ratio), int(h * ratio))
                img = img.resize(new_size)

            self.logo_img = ImageTk.PhotoImage(img)
        except Exception:
            self.logo_img = None

        if self.logo_img:
            tk.Label(self, image=self.logo_img, bg="white").pack(pady=(10, 5))
        else:
            canvas = tk.Canvas(self, width=180, height=180, bg="white", highlightthickness=0)
            canvas.pack(pady=(15, 5))
            canvas.create_oval(10, 10, 170, 170, outline="#015294", width=2, fill="#e6f0fa")
            canvas.create_text(90, 90, text="LOGO", fill="#015294", font=("Arial", 12, "bold"))

        tk.Label(
            self,
            text="SISTEMA DE INVENTARIO",
            bg="white",
            fg="#333333",
            font=("Arial", 16, "bold"),
        ).pack(pady=(10, 2))

        tk.Label(
            self,
            text="Autor: Dante Durand Morales",
            bg="white",
            fg="#666666",
            font=("Arial", 11),
        ).pack(pady=(0, 10))

        tk.Label(
            self,
            text="Usa los botones de abajo para navegar entre\nInicio, Productos y Almacenes.",
            bg="white",
            fg="#555555",
            font=("Arial", 10),
            justify="center",
        ).pack(pady=10)


# ==============================
#  VISTA: PRODUCTOS
# ==============================

class ProductsView(ttk.Frame):
    def __init__(self, parent, db: Database, user: User):
        super().__init__(parent)
        self.db = db
        self.user = user

        self._build_widgets()
        self.refresh_table()

    def _build_widgets(self):
        top = ttk.Frame(self)
        top.pack(side="top", fill="x", pady=5)

        buttons_frame = ttk.Frame(top)
        buttons_frame.pack(side="left")

        self.btn_add = ttk.Button(buttons_frame, text="Agregar", command=self.add_product)
        self.btn_edit = ttk.Button(buttons_frame, text="Modificar", command=self.edit_product)
        self.btn_delete = ttk.Button(buttons_frame, text="Eliminar", command=self.delete_product)
        self.btn_search = ttk.Button(buttons_frame, text="Buscar", command=self.open_search_dialog)
        self.btn_clear = ttk.Button(buttons_frame, text="Mostrar todo", command=self.refresh_table)

        self.btn_add.pack(side="left", padx=3)
        self.btn_edit.pack(side="left", padx=3)
        self.btn_delete.pack(side="left", padx=3)
        self.btn_search.pack(side="left", padx=3)
        self.btn_clear.pack(side="left", padx=3)

        # Tabla
        columns = ("id", "nombre", "descripcion", "precio", "existencias", "almacen")
        self.tree = ttk.Treeview(self, columns=columns, show="headings", height=14)
        for col in columns:
            heading = col.capitalize()
            if col == "almacen":
                heading = "Almacén"
            self.tree.heading(col, text=heading)
            self.tree.column(col, width=140, anchor="center")


        self.tree.pack(fill="both", expand=True, padx=5, pady=5)

        audit_frame = ttk.Frame(self)
        audit_frame.pack(fill="x", padx=5, pady=(0, 5))

        self.lbl_creacion = ttk.Label(audit_frame, text="Creado: -")
        self.lbl_ultima_mod = ttk.Label(audit_frame, text="Última modificación: -")
        self.lbl_ultimo_usuario = ttk.Label(audit_frame, text="Último usuario en modificar: -")

        self.lbl_creacion.pack(anchor="w")
        self.lbl_ultima_mod.pack(anchor="w")
        self.lbl_ultimo_usuario.pack(anchor="w")

        self.tree.bind("<<TreeviewSelect>>", self._on_select_product)

        # Permisos: solo ADMIN y PRODUCTOS pueden modificar
        if self.user.role not in ("ADMIN", "PRODUCTOS"):
            self.btn_add["state"] = "disabled"
            self.btn_edit["state"] = "disabled"
            self.btn_delete["state"] = "disabled"

    # --------- CARGA Y FILTRO ---------

    def refresh_table(self):
        self._load_products()

    def _load_products(self, filtros=None):
        if filtros is None:
            filtros = {}

        id_filter = filtros.get("id", "").strip()
        name_filter = filtros.get("name", "").lower()
        desc_filter = filtros.get("desc", "").lower()
        price_min_filter = filtros.get("price_min", "").strip()
        price_max_filter = filtros.get("price_max", "").strip()
        stock_min_filter = filtros.get("stock_min", "").strip()
        stock_max_filter = filtros.get("stock_max", "").strip()
        warehouse_filter = filtros.get("warehouse", "").lower()

        price_min_value = None
        price_max_value = None
        stock_min_value = None
        stock_max_value = None

        if price_min_filter:
            try:
                price_min_value = float(price_min_filter)
            except ValueError:
                messagebox.showerror("Error", "El precio mínimo debe ser numérico.")
                return

        if price_max_filter:
            try:
                price_max_value = float(price_max_filter)
            except ValueError:
                messagebox.showerror("Error", "El precio máximo debe ser numérico.")
                return

        if stock_min_filter:
            try:
                stock_min_value = int(stock_min_filter)
            except ValueError:
                messagebox.showerror("Error", "Las existencias mínimas deben ser numéricas.")
                return

        if stock_max_filter:
            try:
                stock_max_value = int(stock_max_filter)
            except ValueError:
                messagebox.showerror("Error", "Las existencias máximas deben ser numéricas.")
                return

        for row in self.tree.get_children():
            self.tree.delete(row)

        for p in self.db.list_products():
            if id_filter and str(p.id) != id_filter:
                continue
            if name_filter and name_filter not in p.name.lower():
                continue
            if desc_filter and desc_filter not in p.description.lower():
                continue
            if price_min_value is not None and p.price < price_min_value:
                continue
            if price_max_value is not None and p.price > price_max_value:
                continue
            if stock_min_value is not None and p.stock < stock_min_value:
                continue
            if stock_max_value is not None and p.stock > stock_max_value:
                continue
            if warehouse_filter and warehouse_filter not in (p.warehouse_name or "").lower():
                continue

            self.tree.insert(
                "",
                "end",
                values=(
                    p.id,
                    p.name,
                    p.description,
                    f"{p.price:.2f}",
                    p.stock,
                    p.warehouse_name or "",
                ),
            )

        self.lbl_creacion.config(text="Creado: -")
        self.lbl_ultima_mod.config(text="Última modificación: -")
        self.lbl_ultimo_usuario.config(text="Último usuario en modificar: -")

    def open_search_dialog(self):
        dlg = ProductSearchDialog(self)
        self.wait_window(dlg)
        if dlg.result is not None:
            self._load_products(dlg.result)

    # --------- AUDITORÍA ---------

    def _get_selected_product_id(self):
        sel = self.tree.selection()
        if not sel:
            return None
        values = self.tree.item(sel[0])["values"]
        return values[0]

    def _on_select_product(self, event=None):
        product_id = self._get_selected_product_id()
        if product_id is None:
            return

        row = self.db.get_product_audit(product_id)
        if not row:
            self.lbl_creacion.config(text="Creado: -")
            self.lbl_ultima_mod.config(text="Última modificación: -")
            self.lbl_ultimo_usuario.config(text="Último usuario en modificar: -")
            return

        creado = row["fecha_hora_creacion"] or "-"
        ultima = row["fecha_hora_ultima_modificacion"] or "-"
        usuario = row["ultimo_usuario_en_modificar"] or "-"

        self.lbl_creacion.config(text=f"Creado: {creado}")
        self.lbl_ultima_mod.config(text=f"Última modificación: {ultima}")
        self.lbl_ultimo_usuario.config(text=f"Último usuario en modificar: {usuario}")

    # --------- CRUD ---------

    def add_product(self):
        dialog = ProductDialog(self, self.db, "Agregar producto")
        self.wait_window(dialog)
        if dialog.result:
            name, desc, price, stock, warehouse_id = dialog.result
            try:
                price = float(price)
                stock = int(stock)
            except ValueError:
                messagebox.showerror("Error", "Precio o existencias inválidas.")
                return
            self.db.add_product(name, desc, price, stock, warehouse_id, self.user.username)
            self.refresh_table()

    def edit_product(self):
        product_id = self._get_selected_product_id()
        if product_id is None:
            messagebox.showwarning("Advertencia", "Seleccione un producto.")
            return

        product = None
        for p in self.db.list_products():
            if p.id == product_id:
                product = p
                break
        if not product:
            messagebox.showerror("Error", "Producto no encontrado.")
            return

        dialog = ProductDialog(
            self,
            self.db,
            "Modificar producto",
            initial_name=product.name,
            initial_desc=product.description,
            initial_price=str(product.price),
            initial_stock=str(product.stock),
            initial_warehouse_name=product.warehouse_name or "",
        )
        self.wait_window(dialog)
        if dialog.result:
            name, desc, price, stock, warehouse_id = dialog.result
            try:
                price = float(price)
                stock = int(stock)
            except ValueError:
                messagebox.showerror("Error", "Precio o existencias inválidas.")
                return
            self.db.update_product(product_id, name, desc, price, stock, warehouse_id, self.user.username)
            self.refresh_table()

    def delete_product(self):
        product_id = self._get_selected_product_id()
        if product_id is None:
            messagebox.showwarning("Advertencia", "Seleccione un producto.")
            return
        if messagebox.askyesno("Confirmar", "¿Seguro que desea eliminar este producto?"):
            self.db.delete_product(product_id)
            self.refresh_table()


# ==============================
#  VISTA: ALMACENES
# ==============================

class WarehousesView(ttk.Frame):
    def __init__(self, parent, db: Database, user: User):
        super().__init__(parent)
        self.db = db
        self.user = user

        self._build_widgets()
        self.refresh_table()

    def _build_widgets(self):
        top = ttk.Frame(self)
        top.pack(side="top", fill="x", pady=5)

        buttons_frame = ttk.Frame(top)
        buttons_frame.pack(side="left")

        self.btn_add = ttk.Button(buttons_frame, text="Agregar", command=self.add_warehouse)
        self.btn_edit = ttk.Button(buttons_frame, text="Modificar", command=self.edit_warehouse)
        self.btn_delete = ttk.Button(buttons_frame, text="Eliminar", command=self.delete_warehouse)
        self.btn_search = ttk.Button(buttons_frame, text="Buscar", command=self.open_search_dialog)
        self.btn_clear = ttk.Button(buttons_frame, text="Mostrar todo", command=self.refresh_table)

        self.btn_add.pack(side="left", padx=3)
        self.btn_edit.pack(side="left", padx=3)
        self.btn_delete.pack(side="left", padx=3)
        self.btn_search.pack(side="left", padx=3)
        self.btn_clear.pack(side="left", padx=3)

        columns = ("id", "nombre")
        self.tree = ttk.Treeview(self, columns=columns, show="headings", height=14)
        for col in columns:
            self.tree.heading(col, text=col.capitalize())
            self.tree.column(col, width=200, anchor="center")

        self.tree.pack(fill="both", expand=True, padx=5, pady=5)

        audit_frame = ttk.Frame(self)
        audit_frame.pack(fill="x", padx=5, pady=(0, 5))

        self.lbl_creacion = ttk.Label(audit_frame, text="Creado: -")
        self.lbl_ultima_mod = ttk.Label(audit_frame, text="Última modificación: -")
        self.lbl_ultimo_usuario = ttk.Label(audit_frame, text="Último usuario en modificar: -")

        self.lbl_creacion.pack(anchor="w")
        self.lbl_ultima_mod.pack(anchor="w")
        self.lbl_ultimo_usuario.pack(anchor="w")

        self.tree.bind("<<TreeviewSelect>>", self._on_select_warehouse)

        # Permisos: solo ADMIN y ALMACENES pueden modificar
        if self.user.role not in ("ADMIN", "ALMACENES"):
            self.btn_add["state"] = "disabled"
            self.btn_edit["state"] = "disabled"
            self.btn_delete["state"] = "disabled"

    # --------- CARGA Y FILTRO ---------

    def refresh_table(self):
        self._load_warehouses()

    def _load_warehouses(self, filtros=None):
        if filtros is None:
            filtros = {}

        id_filter = filtros.get("id", "").strip()
        name_filter = filtros.get("name", "").lower()

        for row in self.tree.get_children():
            self.tree.delete(row)

        for w in self.db.list_warehouses():
            if id_filter and str(w.id) != id_filter:
                continue
            if name_filter and name_filter not in w.name.lower():
                continue
            self.tree.insert("", "end", values=(w.id, w.name))

        self.lbl_creacion.config(text="Creado: -")
        self.lbl_ultima_mod.config(text="Última modificación: -")
        self.lbl_ultimo_usuario.config(text="Último usuario en modificar: -")

    def open_search_dialog(self):
        dlg = WarehouseSearchDialog(self)
        self.wait_window(dlg)
        if dlg.result is not None:
            self._load_warehouses(dlg.result)

    # --------- AUDITORÍA ---------

    def _get_selected_id(self):
        sel = self.tree.selection()
        if not sel:
            return None
        values = self.tree.item(sel[0])["values"]
        return values[0]

    def _on_select_warehouse(self, event=None):
        warehouse_id = self._get_selected_id()
        if warehouse_id is None:
            return

        row = self.db.get_warehouse_audit(warehouse_id)
        if not row:
            self.lbl_creacion.config(text="Creado: -")
            self.lbl_ultima_mod.config(text="Última modificación: -")
            self.lbl_ultimo_usuario.config(text="Último usuario en modificar: -")
            return

        creado = row["fecha_hora_creacion"] or "-"
        ultima = row["fecha_hora_ultima_modificacion"] or "-"
        usuario = row["ultimo_usuario_en_modificar"] or "-"

        self.lbl_creacion.config(text=f"Creado: {creado}")
        self.lbl_ultima_mod.config(text=f"Última modificación: {ultima}")
        self.lbl_ultimo_usuario.config(text=f"Último usuario en modificar: {usuario}")

    # --------- CRUD ---------

    def add_warehouse(self):
        dialog = WarehouseDialog(self, "Agregar almacén")
        self.wait_window(dialog)

        if dialog.result is None:
            return

        warehouse_id, name = dialog.result

        self.db.add_warehouse(warehouse_id, name, self.user.username)
        self.refresh_table()

    def edit_warehouse(self):
        warehouse_id = self._get_selected_id()
        if warehouse_id is None:
            messagebox.showwarning("Advertencia", "Seleccione un almacén.")
            return

        sel = self.tree.selection()[0]
        values = self.tree.item(sel)["values"]
        current_id = values[0]
        current_name = values[1]

        dialog = WarehouseDialog(
            self,
            "Modificar almacén",
            initial_id=current_id,
            initial_name=current_name,
            allow_edit_id=False  # no dejamos cambiar el ID
        )
        self.wait_window(dialog)

        if dialog.result is None:
            return

        _ignored_id, new_name = dialog.result
        self.db.update_warehouse(current_id, new_name, self.user.username)
        self.refresh_table()

    def delete_warehouse(self):
        warehouse_id = self._get_selected_id()
        if warehouse_id is None:
            messagebox.showwarning("Advertencia", "Seleccione un almacén.")
            return
        if messagebox.askyesno("Confirmar", "¿Seguro que desea eliminar este almacén?"):
            self.db.delete_warehouse(warehouse_id)
            self.refresh_table()

# ==============================
#  DIÁLOGOS
# ==============================

class ProductSearchDialog(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Buscar producto")
        self.geometry("420x350")
        self.resizable(False, False)
        self.result = None

        frm = ttk.Frame(self, padding=10)
        frm.pack(fill="both", expand=True)

        ttk.Label(frm, text="Id:").grid(row=0, column=0, sticky="e", pady=5)
        ttk.Label(frm, text="Nombre:").grid(row=1, column=0, sticky="e", pady=5)
        ttk.Label(frm, text="Descripción:").grid(row=2, column=0, sticky="e", pady=5)
        ttk.Label(frm, text="Almacén:").grid(row=3, column=0, sticky="e", pady=4)

        ttk.Label(frm, text="Precio Mínimo:").grid(row=5, column=0, sticky="e", pady=5)
        ttk.Label(frm, text="Precio Máximo:").grid(row=6, column=0, sticky="e", pady=5)
        ttk.Label(frm, text="Existencias Mínimas:").grid(row=7, column=0, sticky="e", pady=5)
        ttk.Label(frm, text="Existencias Máximas:").grid(row=8, column=0, sticky="e", pady=5)

        self.var_id = tk.StringVar()
        self.var_name = tk.StringVar()
        self.var_desc = tk.StringVar()
        self.var_warehouse = tk.StringVar()
        self.var_price_min = tk.StringVar()
        self.var_price_max = tk.StringVar()
        self.var_stock_min = tk.StringVar()
        self.var_stock_max = tk.StringVar()

        ttk.Entry(frm, textvariable=self.var_id).grid(row=0, column=1, sticky="we", pady=5)
        ttk.Entry(frm, textvariable=self.var_name).grid(row=1, column=1, sticky="we", pady=5)
        ttk.Entry(frm, textvariable=self.var_desc).grid(row=2, column=1, sticky="we", pady=5)
        ttk.Entry(frm, textvariable=self.var_warehouse).grid(row=3, column=1, sticky="we", pady=4)
        ttk.Entry(frm, textvariable=self.var_price_min).grid(row=5, column=1, sticky="we", pady=5)
        ttk.Entry(frm, textvariable=self.var_price_max).grid(row=6, column=1, sticky="we", pady=5)
        ttk.Entry(frm, textvariable=self.var_stock_min).grid(row=7, column=1, sticky="we", pady=5)
        ttk.Entry(frm, textvariable=self.var_stock_max).grid(row=8, column=1, sticky="we", pady=5)

        frm.columnconfigure(1, weight=1)

        btns = ttk.Frame(frm)
        btns.grid(row=10, column=0, columnspan=2, pady=18)

        ttk.Button(btns, text="Aplicar filtro", command=self._on_ok).pack(side="left", padx=8)
        ttk.Button(btns, text="Cancelar", command=self.destroy).pack(side="left", padx=8)

        self.transient(parent)
        self.grab_set()
        self.protocol("WM_DELETE_WINDOW", self.destroy)

        self._center_window()

    def _center_window(self):
        self.update_idletasks()
        w = self.winfo_width()
        h = self.winfo_height()
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        x = (sw // 2) - (w // 2)
        y = (sh // 2) - (h // 2)
        self.geometry(f"{w}x{h}+{x}+{y}")

    def _on_ok(self):
        self.result = {
            "id": self.var_id.get().strip(),
            "name": self.var_name.get().strip(),
            "desc": self.var_desc.get().strip(),
            "warehouse": self.var_warehouse.get().strip(),
            "price_min": self.var_price_min.get().strip(),
            "price_max": self.var_price_max.get().strip(),
            "stock_min": self.var_stock_min.get().strip(),
            "stock_max": self.var_stock_max.get().strip(),
        }
        self.destroy()

class WarehouseSearchDialog(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Buscar almacén")
        self.geometry("280x170")
        self.resizable(False, False)
        self.result = None

        frm = ttk.Frame(self, padding=10)
        frm.pack(fill="both", expand=True)

        ttk.Label(frm, text="Id:").grid(row=0, column=0, sticky="e", pady=5)
        ttk.Label(frm, text="Nombre:").grid(row=1, column=0, sticky="e", pady=5)

        self.var_id = tk.StringVar()
        self.var_name = tk.StringVar()

        ttk.Entry(frm, textvariable=self.var_id).grid(row=0, column=1, sticky="we", pady=5)
        ttk.Entry(frm, textvariable=self.var_name).grid(row=1, column=1, sticky="we", pady=5)

        frm.columnconfigure(1, weight=1)

        btns = ttk.Frame(frm)
        btns.grid(row=2, column=0, columnspan=2, pady=10)

        ttk.Button(btns, text="Aplicar filtro", command=self._on_ok).pack(side="left", padx=5)
        ttk.Button(btns, text="Cancelar", command=self.destroy).pack(side="left", padx=5)

        self.transient(parent)
        self.grab_set()
        self.protocol("WM_DELETE_WINDOW", self.destroy)

        self._center_window()

    def _center_window(self):
        self.update_idletasks()
        w = self.winfo_width()
        h = self.winfo_height()
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        x = (sw // 2) - (w // 2)
        y = (sh // 2) - (h // 2)
        self.geometry(f"{w}x{h}+{x}+{y}")

    def _on_ok(self):
        self.result = {
            "id": self.var_id.get().strip(),
            "name": self.var_name.get().strip(),
        }
        self.destroy()

class ProductDialog(tk.Toplevel):
    def __init__(
            self,
            parent,
            db: Database,
            title: str,
            initial_name: str = "",
            initial_desc: str = "",
            initial_price: str = "",
            initial_stock: str = "",
            initial_warehouse_name: str = "",
    ):
        super().__init__(parent)
        self.result = None
        self.db = db
        self.title(title)
        self.geometry("400x260")
        self.resizable(False, False)
        self._center_window()

        self.warehouses = self.db.list_warehouses()
        self.warehouse_name_to_id = {w.name: w.id for w in self.warehouses}

        frm = ttk.Frame(self, padding=10)
        frm.pack(fill="both", expand=True)

        ttk.Label(frm, text="Nombre:").grid(row=0, column=0, sticky="e", pady=5)
        ttk.Label(frm, text="Departamento:").grid(row=1, column=0, sticky="e", pady=5)
        ttk.Label(frm, text="Precio:").grid(row=2, column=0, sticky="e", pady=5)
        ttk.Label(frm, text="Cantidad:").grid(row=3, column=0, sticky="e", pady=5)
        ttk.Label(frm, text="Almacén:").grid(row=4, column=0, sticky="e", pady=5)

        self.var_name = tk.StringVar(value=initial_name)
        self.var_desc = tk.StringVar(value=initial_desc)
        self.var_price = tk.StringVar(value=initial_price)
        self.var_stock = tk.StringVar(value=initial_stock)
        self.var_warehouse_name = tk.StringVar(value=initial_warehouse_name)

        ttk.Entry(frm, textvariable=self.var_name).grid(row=0, column=1, sticky="we", pady=5)
        ttk.Entry(frm, textvariable=self.var_desc).grid(row=1, column=1, sticky="we", pady=5)
        ttk.Entry(frm, textvariable=self.var_price).grid(row=2, column=1, sticky="we", pady=5)
        ttk.Entry(frm, textvariable=self.var_stock).grid(row=3, column=1, sticky="we", pady=5)

        warehouse_names = [w.name for w in self.warehouses]
        self.combo_warehouse = ttk.Combobox(
        frm,
        textvariable=self.var_warehouse_name,
        values=warehouse_names,
        state="readonly"
        )
        self.combo_warehouse.grid(row=4, column=1, sticky="we", pady=5)

        frm.columnconfigure(1, weight=1)

        btns = ttk.Frame(frm)
        btns.grid(row=5, column=0, columnspan=2, pady=10)

        ttk.Button(btns, text="Aceptar", command=self._on_ok).pack(side="left", padx=5)
        ttk.Button(btns, text="Cancelar", command=self.destroy).pack(side="left", padx=5)

        self.transient(parent)
        self.grab_set()
        self.protocol("WM_DELETE_WINDOW", self.destroy)

    def _on_ok(self):
        name = self.var_name.get().strip()
        desc = self.var_desc.get().strip()
        price = self.var_price.get().strip()
        stock = self.var_stock.get().strip()
        warehouse_name = self.var_warehouse_name.get().strip()

        if not name or not price or not stock or not warehouse_name:
            messagebox.showwarning("Advertencia", "Nombre, precio, cantidad y almacen son obligatorios.")
            return

        try:
            float(price)
            int(stock)
        except ValueError:
            messagebox.showerror("Error", "Precio y cantidad deben ser números.")
            return

        if warehouse_name not in self.warehouse_name_to_id:
            messagebox.showerror("Error", "Almacén inválido.")
            return

        warehouse_id = self.warehouse_name_to_id[warehouse_name]

        self.result = (name, desc, price, stock, warehouse_id)
        self.destroy()

    def _center_window(self):
        self.update_idletasks()
        w = self.winfo_width()
        h = self.winfo_height()
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        x = (sw // 2) - (w // 2)
        y = (sh // 2) - (h // 2)
        self.geometry(f"{w}x{h}+{x}+{y}")

class WarehouseDialog(tk.Toplevel):
    def __init__(self, parent, title="Agregar almacén",
                 initial_id: int | None = None,
                 initial_name: str | None = None,
                 allow_edit_id: bool = True):
        super().__init__(parent)
        self.title(title)
        self.resizable(False, False)
        self.result = None

        frm = ttk.Frame(self, padding=15)
        frm.pack(fill="both", expand=True)

        # ----- ID -----
        ttk.Label(frm, text="ID:").grid(row=0, column=0, sticky="e", pady=5, padx=5)
        self.entry_id = ttk.Entry(frm, width=25)
        self.entry_id.grid(row=0, column=1, sticky="we", pady=5, padx=5)

        # ----- NOMBRE -----
        ttk.Label(frm, text="Nombre:").grid(row=1, column=0, sticky="e", pady=5, padx=5)
        self.entry_name = ttk.Entry(frm, width=25)
        self.entry_name.grid(row=1, column=1, sticky="we", pady=5, padx=5)

        frm.columnconfigure(1, weight=1)

        if initial_id is not None:
            self.entry_id.insert(0, str(initial_id))
        if initial_name is not None:
            self.entry_name.insert(0, initial_name)

        # Si no quieres que se modifique el ID al editar:
        if not allow_edit_id:
            self.entry_id.configure(state="disabled")

        # ----- BOTONES -----
        btns = ttk.Frame(frm)
        btns.grid(row=2, column=0, columnspan=2, pady=(10, 0))

        ttk.Button(btns, text="Aceptar", command=self._on_accept).pack(side="left", padx=5)
        ttk.Button(btns, text="Cancelar", command=self.destroy).pack(side="left", padx=5)

        self.transient(parent)
        self.grab_set()
        self.protocol("WM_DELETE_WINDOW", self.destroy)

        self._center_window()

    def _center_window(self):
        self.update_idletasks()
        w = self.winfo_width()
        h = self.winfo_height()
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        x = (sw // 2) - (w // 2)
        y = (sh // 2) - (h // 2)
        self.geometry(f"{w}x{h}+{x}+{y}")

    def _on_accept(self):
        id_text = self.entry_id.get().strip()
        name = self.entry_name.get().strip()

        if not id_text or not name:
            messagebox.showwarning("Advertencia", "Debe llenar ID y Nombre.")
            return

        try:
            warehouse_id = int(id_text)
        except ValueError:
            messagebox.showerror("Error", "El ID debe ser un número.")
            return

        self.result = (warehouse_id, name)
        self.destroy()