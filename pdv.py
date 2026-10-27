from datetime import datetime
from decimal import Decimal, InvalidOperation
from tkinter import (
    END,
    BOTH,
    LEFT,
    RIGHT,
    X,
    Button,
    Entry,
    Frame,
    Label,
    LabelFrame,
    Menu,
    Spinbox,
    Tk,
    Toplevel,
    filedialog,
    messagebox,
)
from tkinter import ttk


DEFAULT_PRODUCTS = (
    ("whey", "Whey Protein", 850, 10),
    ("isolate", "Isolate Protein", 1100, 10),
    ("mass", "Mass Gainer", 750, 10),
    ("creatina", "Creatina", 600, 10),
    ("omega", "Omega-3", 350, 10),
    ("pre", "Pre-entreno", 500, 10),
    ("shaker", "Vaso Shaker", 150, 10),
)
IVA_RATE = 16


def calculate_iva_cents(subtotal_cents):
    return (subtotal_cents * IVA_RATE + 50) // 100


def parse_money_to_cents(value):
    text = value.strip().replace("$", "").replace(" ", "")
    if not text:
        raise ValueError("Escribe cuánto paga el cliente.")

    if "," in text and "." in text:
        if text.rfind(",") > text.rfind("."):
            text = text.replace(".", "").replace(",", ".")
        else:
            text = text.replace(",", "")
    elif "," in text:
        whole, separator, fraction = text.partition(",")
        if separator and len(fraction) == 3 and whole.isdigit():
            text = whole + fraction
        else:
            text = text.replace(",", ".")

    try:
        amount = Decimal(text)
        if not amount.is_finite() or amount < 0:
            raise ValueError("El monto debe ser un número positivo.")
        if amount != amount.quantize(Decimal("0.01")):
            raise ValueError("El monto puede tener como máximo dos decimales.")
        return int(amount * 100)
    except InvalidOperation as error:
        raise ValueError("Escribe un monto válido, por ejemplo 1000 o 1000.50.") from error


def format_money(cents):
    return f"${Decimal(cents) / Decimal(100):,.2f}"


class LocalStore:
    def __init__(self):
        self.products = {
            key: {
                "product_key": key,
                "name": name,
                "price": price,
                "quantity": quantity,
            }
            for key, name, price, quantity in DEFAULT_PRODUCTS
        }
        self.sales = []
        self.next_sale_id = 1

    def authenticate_admin(self, username, password):
        return username.strip() == "admin" and password == "admin"

    def get_inventory(self):
        return sorted(
            (product.copy() for product in self.products.values()),
            key=lambda product: product["name"],
        )

    def update_stock(self, product_key, quantity):
        if quantity < 0:
            raise ValueError("La existencia no puede ser negativa.")
        if product_key not in self.products:
            raise ValueError("No se encontró el producto seleccionado.")
        self.products[product_key]["quantity"] = quantity

    def record_sale(self, customer_name, cart, paid_cents):
        customer_name = customer_name.strip()
        if not customer_name:
            raise ValueError("Escribe el nombre del cliente.")
        if not cart:
            raise ValueError("Agrega al menos un producto a la venta.")

        items = []
        total = 0
        for product_key, quantity in cart.items():
            if quantity < 1:
                raise ValueError("La cantidad de cada producto debe ser mayor a cero.")
            product = self.products.get(product_key)
            if product is None:
                raise ValueError("Uno de los productos no está en el inventario.")
            if product["quantity"] < quantity:
                raise ValueError(
                    f"Existencias insuficientes para {product['name']}. "
                    f"Disponibles: {product['quantity']}."
                )
            subtotal = product["price"] * quantity
            total += subtotal
            items.append(
                {
                    "product_key": product_key,
                    "product_name": product["name"],
                    "quantity": quantity,
                    "unit_price": product["price"],
                    "subtotal": subtotal,
                }
            )

        subtotal_cents = total * 100
        iva_cents = calculate_iva_cents(subtotal_cents)
        total_cents = subtotal_cents + iva_cents
        if paid_cents < total_cents:
            raise ValueError(
                f"El pago ({format_money(paid_cents)}) no cubre el total "
                f"({format_money(total_cents)})."
            )

        for item in items:
            self.products[item["product_key"]]["quantity"] -= item["quantity"]

        sale = {
            "id": self.next_sale_id,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "customer_name": customer_name,
            "subtotal": total,
            "iva_cents": iva_cents,
            "total_cents": total_cents,
            "paid_cents": paid_cents,
            "change_cents": paid_cents - total_cents,
            "items": items,
        }
        self.sales.append(sale)
        self.next_sale_id += 1
        return sale.copy()

    def get_sales(self):
        return [sale.copy() for sale in reversed(self.sales)]

    def get_sale(self, sale_id):
        for sale in self.sales:
            if sale["id"] == sale_id:
                return sale.copy()
        raise ValueError("No se encontró la venta seleccionada.")


def format_ticket(sale):
    lines = [
        "IRON GYM - SUPLEMENTOS",
        "Punto de venta",
        "=" * 38,
        f"Venta: #{sale['id']}",
        f"Fecha: {sale['created_at']}",
        f"Cliente: {sale['customer_name']}",
        "-" * 38,
    ]
    for item in sale["items"]:
        lines.append(
            f"{item['product_name']} x{item['quantity']} "
            f"@ {format_money(item['unit_price'] * 100)} sin IVA "
            f"= {format_money(item['subtotal'] * 100)} sin IVA"
        )
    lines.extend(
        (
            "-" * 38,
            f"Subtotal sin IVA: {format_money(sale['subtotal'] * 100)}",
            f"IVA ({IVA_RATE}%): {format_money(sale['iva_cents'])}",
            f"TOTAL con IVA: {format_money(sale['total_cents'])}",
            f"Recibido: {format_money(sale['paid_cents'])}",
            f"Cambio: {format_money(sale['change_cents'])}",
            "=" * 38,
        )
    )
    return "\n".join(lines) + "\n"


class PuntoDeVenta:
    background = "#1e1e1e"
    panel = "#2b2b2b"
    accent = "#ff4500"
    foreground = "white"

    def __init__(self, root):
        self.root = root
        self.root.title("IronGym Supplements - Punto de Venta")
        self.root.geometry("1000x700")
        self.root.minsize(850, 620)
        self.root.configure(bg=self.background)
        self.store = LocalStore()
        self.cart = {}
        self.last_sale = None
        self.create_menu()
        self.show_login()

    def create_menu(self):
        menu_bar = Menu(self.root)
        options = Menu(menu_bar, tearoff=0)
        options.add_command(label="Cerrar sesión", command=self.logout)
        options.add_separator()
        options.add_command(label="Salir", command=self.root.destroy)
        menu_bar.add_cascade(label="Opciones", menu=options)
        self.root.config(menu=menu_bar)

    def clear_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def show_login(self):
        self.clear_window()
        self.root.title("IronGym - Inicio de sesión")
        frame = Frame(self.root, bg=self.background, padx=35, pady=35)
        frame.place(relx=0.5, rely=0.5, anchor="center")
        Label(
            frame,
            text="IRON GYM - SUPLEMENTOS",
            font=("Helvetica", 20, "bold"),
            bg=self.background,
            fg=self.accent,
        ).pack(pady=(0, 20))
        Label(
            frame,
            text="Inicia sesión como administrador",
            bg=self.background,
            fg=self.foreground,
        ).pack(pady=(0, 15))

        Label(frame, text="Usuario", bg=self.background, fg=self.foreground).pack(
            anchor="w"
        )
        username = Entry(frame, width=32)
        username.insert(0, "admin")
        username.pack(pady=(3, 10))
        Label(frame, text="Contraseña", bg=self.background, fg=self.foreground).pack(
            anchor="w"
        )
        password = Entry(frame, width=32, show="*")
        password.pack(pady=(3, 15))

        def login(event=None):
            if not self.store.authenticate_admin(username.get(), password.get()):
                messagebox.showerror(
                    "Acceso denegado", "El usuario o la contraseña son incorrectos."
                )
                password.delete(0, END)
                password.focus_set()
                return
            self.cart = {}
            self.show_main()

        Button(
            frame,
            text="Iniciar sesión",
            command=login,
            bg=self.accent,
            fg=self.foreground,
            width=24,
        ).pack()
        Label(
            frame,
            text="Acceso: admin / admin",
            bg=self.background,
            fg="#bdbdbd",
        ).pack(pady=(12, 0))
        password.bind("<Return>", login)
        username.focus_set()

    def show_main(self):
        self.clear_window()
        self.root.title("IronGym Supplements - Punto de Venta")
        header = Frame(self.root, bg=self.background, padx=15, pady=10)
        header.pack(fill=X)
        Label(
            header,
            text="IRON GYM - SUPLEMENTOS",
            font=("Helvetica", 18, "bold"),
            bg=self.background,
            fg=self.accent,
        ).pack(side=LEFT)
        Button(
            header,
            text="Cerrar sesión",
            command=self.logout,
            bg=self.panel,
            fg=self.foreground,
        ).pack(side=RIGHT)

        body = Frame(self.root, bg=self.background, padx=12, pady=5)
        body.pack(fill=BOTH, expand=True)
        body.columnconfigure(0, weight=1)
        body.columnconfigure(1, weight=1)
        body.rowconfigure(0, weight=1)

        inventory_frame = LabelFrame(
            body,
            text="Inventario",
            bg=self.panel,
            fg=self.foreground,
            padx=8,
            pady=8,
        )
        inventory_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 6))
        cart_frame = LabelFrame(
            body,
            text="Venta actual",
            bg=self.panel,
            fg=self.foreground,
            padx=8,
            pady=8,
        )
        cart_frame.grid(row=0, column=1, sticky="nsew", padx=(6, 0))

        self.inventory_tree = ttk.Treeview(
            inventory_frame,
            columns=("name", "price", "quantity"),
            show="headings",
            selectmode="browse",
            height=14,
        )
        for column, title, width in (
            ("name", "Producto", 155),
            ("price", "Precio s/IVA", 95),
            ("quantity", "Existencias", 85),
        ):
            self.inventory_tree.heading(column, text=title)
            self.inventory_tree.column(column, width=width, anchor="center")
        self.inventory_tree.pack(fill=BOTH, expand=True)
        self.inventory_tree.bind("<<TreeviewSelect>>", self.on_inventory_select)

        stock_controls = Frame(inventory_frame, bg=self.panel)
        stock_controls.pack(fill=X, pady=(8, 0))
        Label(
            stock_controls, text="Cantidad a vender:", bg=self.panel, fg=self.foreground
        ).pack(side=LEFT)
        self.quantity_to_add = Spinbox(stock_controls, from_=1, to=1000000, width=7)
        self.quantity_to_add.pack(side=LEFT, padx=6)
        Button(
            stock_controls,
            text="Agregar al carrito",
            command=self.add_to_cart,
            bg=self.accent,
            fg=self.foreground,
        ).pack(side=LEFT, padx=4)

        Label(
            inventory_frame,
            text="Existencia del producto seleccionado:",
            bg=self.panel,
            fg=self.foreground,
        ).pack(anchor="w", pady=(12, 3))
        stock_edit = Frame(inventory_frame, bg=self.panel)
        stock_edit.pack(fill=X)
        self.stock_value = Spinbox(stock_edit, from_=0, to=1000000, width=10)
        self.stock_value.pack(side=LEFT)
        Button(
            stock_edit,
            text="Actualizar inventario",
            command=self.update_stock,
            bg="#404040",
            fg=self.foreground,
        ).pack(side=LEFT, padx=7)

        self.cart_tree = ttk.Treeview(
            cart_frame,
            columns=("name", "quantity", "unit_price", "subtotal"),
            show="headings",
            selectmode="browse",
            height=14,
        )
        for column, title, width in (
            ("name", "Producto", 140),
            ("quantity", "Cant.", 50),
            ("unit_price", "Precio s/IVA", 90),
            ("subtotal", "Importe s/IVA", 100),
        ):
            self.cart_tree.heading(column, text=title)
            self.cart_tree.column(column, width=width, anchor="center")
        self.cart_tree.pack(fill=BOTH, expand=True)
        Button(
            cart_frame,
            text="Quitar producto seleccionado",
            command=self.remove_from_cart,
            bg="#404040",
            fg=self.foreground,
        ).pack(anchor="e", pady=(8, 12))

        Label(
            cart_frame, text="Nombre del cliente:", bg=self.panel, fg=self.foreground
        ).pack(anchor="w")
        self.customer_name = Entry(cart_frame)
        self.customer_name.pack(fill=X, pady=(3, 8))
        Label(
            cart_frame,
            text="¿Con cuánto paga?",
            bg=self.panel,
            fg=self.foreground,
        ).pack(anchor="w")
        self.payment_amount = Entry(cart_frame)
        self.payment_amount.pack(fill=X, pady=(3, 4))
        self.payment_amount.bind("<KeyRelease>", self.update_change_hint)
        self.subtotal_label = Label(
            cart_frame,
            text="Subtotal sin IVA: $0.00",
            bg=self.panel,
            fg=self.foreground,
        )
        self.subtotal_label.pack(anchor="e", pady=(7, 0))
        self.iva_label = Label(
            cart_frame,
            text=f"IVA ({IVA_RATE}%): $0.00",
            bg=self.panel,
            fg=self.foreground,
        )
        self.iva_label.pack(anchor="e", pady=(2, 0))
        self.total_label = Label(
            cart_frame,
            text="Total con IVA: $0.00",
            font=("Helvetica", 16, "bold"),
            bg=self.panel,
            fg=self.accent,
        )
        self.total_label.pack(anchor="e", pady=(2, 0))
        self.change_label = Label(
            cart_frame,
            text="Cambio: —",
            font=("Helvetica", 12, "bold"),
            bg=self.panel,
            fg=self.foreground,
        )
        self.change_label.pack(anchor="e", pady=(2, 5))
        Button(
            cart_frame,
            text="Cobrar venta",
            command=self.checkout,
            bg=self.accent,
            fg=self.foreground,
            width=22,
        ).pack(anchor="e", pady=(5, 5))

        footer = Frame(self.root, bg=self.background, padx=15, pady=10)
        footer.pack(fill=X)
        Button(
            footer,
            text="Historial de ventas",
            command=self.show_sales_history,
            bg=self.panel,
            fg=self.foreground,
        ).pack(side=LEFT)
        Button(
            footer,
            text="Guardar ticket de la última venta",
            command=self.save_last_ticket,
            bg=self.panel,
            fg=self.foreground,
        ).pack(side=LEFT, padx=8)
        self.refresh_inventory()
        self.refresh_cart()

    def selected_inventory_product(self):
        selected = self.inventory_tree.selection()
        if not selected:
            messagebox.showwarning("Selecciona un producto", "Elige un producto.")
            return None
        return selected[0]

    def on_inventory_select(self, event=None):
        product_key = self.selected_inventory_product()
        if product_key is None:
            return
        values = self.inventory_tree.item(product_key, "values")
        self.stock_value.delete(0, END)
        self.stock_value.insert(0, values[2])

    def refresh_inventory(self):
        for item in self.inventory_tree.get_children():
            self.inventory_tree.delete(item)
        for product in self.store.get_inventory():
            self.inventory_tree.insert(
                "",
                END,
                iid=product["product_key"],
                values=(
                    product["name"],
                    format_money(product["price"] * 100),
                    product["quantity"],
                ),
            )

    def add_to_cart(self):
        product_key = self.selected_inventory_product()
        if product_key is None:
            return
        try:
            quantity = int(self.quantity_to_add.get())
            if quantity < 1:
                raise ValueError
        except ValueError:
            messagebox.showerror("Cantidad inválida", "Escribe una cantidad mayor a cero.")
            return

        product = self.store.products.get(product_key)
        if product is None:
            messagebox.showerror("Producto no disponible", "Actualiza el inventario.")
            self.refresh_inventory()
            return
        new_quantity = self.cart.get(product_key, 0) + quantity
        if new_quantity > product["quantity"]:
            messagebox.showwarning(
                "Existencias insuficientes",
                f"Disponibles de {product['name']}: {product['quantity']}.",
            )
            return
        self.cart[product_key] = new_quantity
        self.refresh_cart()

    def refresh_cart(self):
        for item in self.cart_tree.get_children():
            self.cart_tree.delete(item)
        subtotal_total = 0
        for product_key, quantity in self.cart.items():
            product = self.store.products.get(product_key)
            if product is None:
                continue
            line_subtotal = product["price"] * quantity
            subtotal_total += line_subtotal
            self.cart_tree.insert(
                "",
                END,
                iid=product_key,
                values=(
                    product["name"],
                    quantity,
                    format_money(product["price"] * 100),
                    format_money(line_subtotal * 100),
                ),
            )
        subtotal_cents = subtotal_total * 100
        iva_cents = calculate_iva_cents(subtotal_cents)
        self.subtotal_label.config(
            text=f"Subtotal sin IVA: {format_money(subtotal_cents)}"
        )
        self.iva_label.config(text=f"IVA ({IVA_RATE}%): {format_money(iva_cents)}")
        self.total_label.config(
            text=f"Total con IVA: {format_money(subtotal_cents + iva_cents)}"
        )
        self.update_change_hint()

    def update_change_hint(self, event=None):
        try:
            paid_cents = parse_money_to_cents(self.payment_amount.get())
        except ValueError:
            self.change_label.config(text="Cambio: —")
            return
        total = sum(
            self.store.products[key]["price"] * quantity
            for key, quantity in self.cart.items()
            if key in self.store.products
        )
        subtotal_cents = total * 100
        total_cents = subtotal_cents + calculate_iva_cents(subtotal_cents)
        if paid_cents < total_cents:
            self.change_label.config(text="Cambio: pago insuficiente")
        else:
            self.change_label.config(
                text=f"Cambio: {format_money(paid_cents - total_cents)}"
            )

    def remove_from_cart(self):
        selected = self.cart_tree.selection()
        if not selected:
            messagebox.showwarning(
                "Selecciona un producto", "Elige un producto del carrito."
            )
            return
        self.cart.pop(selected[0], None)
        self.refresh_cart()

    def update_stock(self):
        product_key = self.selected_inventory_product()
        if product_key is None:
            return
        try:
            quantity = int(self.stock_value.get())
            self.store.update_stock(product_key, quantity)
        except ValueError as error:
            messagebox.showerror("Existencia inválida", str(error))
            return
        self.refresh_inventory()
        self.refresh_cart()
        messagebox.showinfo("Inventario actualizado", "Se actualizaron las existencias.")

    def checkout(self):
        try:
            paid_cents = parse_money_to_cents(self.payment_amount.get())
            sale = self.store.record_sale(
                self.customer_name.get(), self.cart, paid_cents
            )
        except ValueError as error:
            messagebox.showwarning("No se pudo cobrar", str(error))
            return

        self.last_sale = sale
        self.cart.clear()
        self.customer_name.delete(0, END)
        self.payment_amount.delete(0, END)
        self.refresh_inventory()
        self.refresh_cart()
        if messagebox.askyesno(
            "Venta registrada",
            f"Venta #{sale['id']} por {format_money(sale['total_cents'])} "
            "(con IVA).\n"
            f"Pagó: {format_money(sale['paid_cents'])}  |  "
            f"Cambio: {format_money(sale['change_cents'])}\n"
            "¿Quieres guardar el ticket como archivo TXT?",
        ):
            self.save_ticket(sale)

    def save_ticket(self, sale):
        path = filedialog.asksaveasfilename(
            title="Guardar ticket de venta",
            initialfile=f"ticket_{sale['id']}.txt",
            defaultextension=".txt",
            filetypes=(("Archivo de texto", "*.txt"), ("Todos los archivos", "*.*")),
        )
        if not path:
            return
        try:
            with open(path, "w", encoding="utf-8") as ticket:
                ticket.write(format_ticket(sale))
        except OSError as error:
            messagebox.showerror("Error al guardar ticket", str(error))
            return
        messagebox.showinfo("Ticket guardado", f"Se guardó el ticket en:\n{path}")

    def save_last_ticket(self):
        if self.last_sale is None:
            messagebox.showinfo(
                "Sin venta reciente",
                "Selecciona una venta del historial para guardar su ticket.",
            )
            self.show_sales_history()
            return
        self.save_ticket(self.last_sale)

    def show_sales_history(self):
        window = Toplevel(self.root)
        window.title("Historial de ventas de esta sesión")
        window.geometry("700x400")
        columns = ("id", "created_at", "customer", "total")
        tree = ttk.Treeview(window, columns=columns, show="headings")
        for column, title, width in (
            ("id", "Venta", 70),
            ("created_at", "Fecha", 170),
            ("customer", "Cliente", 250),
            ("total", "Total c/IVA", 120),
        ):
            tree.heading(column, text=title)
            tree.column(column, width=width, anchor="center")
        tree.pack(fill=BOTH, expand=True, padx=10, pady=10)
        for sale in self.store.get_sales():
            tree.insert(
                "",
                END,
                iid=str(sale["id"]),
                values=(
                    sale["id"],
                    sale["created_at"],
                    sale["customer_name"],
                    format_money(sale["total_cents"]),
                ),
            )

        def save_selected_ticket():
            selected = tree.selection()
            if not selected:
                messagebox.showwarning(
                    "Selecciona una venta", "Elige una venta del historial."
                )
                return
            try:
                sale = self.store.get_sale(int(selected[0]))
            except ValueError as error:
                messagebox.showerror("Error al cargar ticket", str(error))
                return
            self.save_ticket(sale)

        Button(
            window,
            text="Guardar ticket seleccionado como TXT",
            command=save_selected_ticket,
            bg=self.accent,
            fg=self.foreground,
        ).pack(pady=(0, 10))

    def logout(self):
        self.cart.clear()
        self.show_login()

#
if __name__ == "__main__":
    root = Tk()
    app = PuntoDeVenta(root)
    root.mainloop()
