import os
from tkinter import *

#  Creación de la ventana principal 
raiz = Tk()

#  Asignar un título a la ventana
raiz.title("Ventana de pruebas")

#  Bloquear o permitir redimensión (ancho, alto)
raiz.resizable(True, False) 

#  Cambiar el icono de la ventana 
ruta_icono = os.path.join(os.path.dirname(__file__), "gato.ico")
raiz.iconbitmap(ruta_icono)

#  Definir las dimensiones iniciales from tkinter import *
from tkinter import messagebox, filedialog

# --- CONFIGURACIÓN DE LA VENTANA PRINCIPAL ---
root = Tk()
root.title("Punto de Venta - Sushi Nice")
root.geometry("450x450")
root.config(bd=15)

# --- VARIABLES DE CONTROL ---
tipo_platillo = IntVar()
extra_aguacate = IntVar()
extra_queso = IntVar()
extra_chiles = IntVar()
total_venta = StringVar()

# Inicializamos el total en $0.00
total_venta.set("$0.00")

# --- FUNCIONES LÓGICAS DEL PDV ---
def calcular_total():
    total = 0
    
    # Lógica de Radiobuttons (Platillo principal)
    if tipo_platillo.get() == 1:
        total += 80  # Rollo Tradicional
    elif tipo_platillo.get() == 2:
        total += 120 # Rollo Especial
    elif tipo_platillo.get() == 3:
        total += 150 # Charola Mixta
        
    # Lógica de Checkbuttons (Complementos)
    if extra_aguacate.get() == 1:
        total += 15
    if extra_queso.get() == 1:
        total += 15
    if extra_chiles.get() == 1:
        total += 10
        
    # Actualizar la pantalla
    total_venta.set(f"${total}.00")
    return total

def cobrar():
    total = calcular_total()
    if total == 0:
        messagebox.showwarning("Atención", "No hay artículos seleccionados para cobrar.")
    else:
        # Ventana de confirmación (Sí/No)
        respuesta = messagebox.askquestion("Confirmar Cobro", f"¿Desea registrar el cobro por ${total}.00?")
        if respuesta == "yes":
            messagebox.showinfo("Éxito", "Cobro registrado correctamente.")
            nuevo_pedido()

def nuevo_pedido():
    # Resetea todas las variables a su estado original
    tipo_platillo.set(0)
    extra_aguacate.set(0)
    extra_queso.set(0)
    extra_chiles.set(0)
    total_venta.set("$0.00")

def guardar_ticket():
    total = total_venta.get()
    # Abre ventana para guardar archivo
    archivo = filedialog.asksaveasfilename(
        title="Guardar Ticket",
        defaultextension=".txt",
        filetypes=(("Archivos de texto", "*.txt"), ("Todos los archivos", "*.*"))
    )
    if archivo:
        # Aquí iría la lógica en Python para escribir el archivo .txt con el desglose
        messagebox.showinfo("Guardado", f"Ticket guardado en:\n{archivo}")

def salir():
    if messagebox.askokcancel("Salir", "¿Seguro que deseas salir del sistema?"):
        root.destroy()

# --- BARRA DE MENÚS ---
barra_menu = Menu(root)
root.config(menu=barra_menu)

menu_archivo = Menu(barra_menu, tearoff=0)
menu_archivo.add_command(label="Nuevo Pedido", command=nuevo_pedido)
menu_archivo.add_command(label="Guardar Ticket", command=guardar_ticket)
menu_archivo.add_separator()
menu_archivo.add_command(label="Salir", command=salir)

barra_menu.add_cascade(label="Archivo", menu=menu_archivo)

# --- INTERFAZ GRÁFICA (UI) ---
# Título
Label(root, text="SISTEMA DE COBRO", font=("Arial", 16, "bold")).grid(row=0, column=0, columnspan=2, pady=10)

# Panel Izquierdo: Radiobuttons para Platillo Principal
frame_platillos = LabelFrame(root, text="Platillo Principal", font=("Arial", 10, "bold"), padx=10, pady=10)
frame_platillos.grid(row=1, column=0, padx=10, pady=10, sticky="nw")

Radiobutton(frame_platillos, text="Rollo Tradicional ($80)", variable=tipo_platillo, value=1, command=calcular_total).pack(anchor="w")
Radiobutton(frame_platillos, text="Rollo Especial ($120)", variable=tipo_platillo, value=2, command=calcular_total).pack(anchor="w")
Radiobutton(frame_platillos, text="Charola Mixta ($150)", variable=tipo_platillo, value=3, command=calcular_total).pack(anchor="w")

# Panel Derecho: Checkbuttons para Extras
frame_extras = LabelFrame(root, text="Complementos Extras", font=("Arial", 10, "bold"), padx=10, pady=10)
frame_extras.grid(row=1, column=1, padx=10, pady=10, sticky="nw")

Checkbutton(frame_extras, text="Aguacate ($15)", variable=extra_aguacate, onvalue=1, offvalue=0, command=calcular_total).pack(anchor="w")
Checkbutton(frame_extras, text="Queso Crema ($15)", variable=extra_queso, onvalue=1, offvalue=0, command=calcular_total).pack(anchor="w")
Checkbutton(frame_extras, text="Chiles Toreados ($10)", variable=extra_chiles, onvalue=1, offvalue=0, command=calcular_total).pack(anchor="w")

# Panel Inferior: Display del Total y Botón de Cobro
frame_total = Frame(root)
frame_total.grid(row=2, column=0, columnspan=2, pady=20)

Label(frame_total, text="TOTAL A PAGAR:", font=("Arial", 14, "bold")).pack(side="left", padx=10)

# Entry de solo lectura configurado como "display"
pantalla_total = Entry(frame_total, textvariable=total_venta, font=("Arial", 16, "bold"), width=8, justify="right", state="readonly")
pantalla_total.pack(side="left", padx=10)

Button(root, text="PROCESAR COBRO", font=("Arial", 12, "bold"), bg="green", fg="white", width=20, command=cobrar).grid(row=3, column=0, columnspan=2, pady=20)

# --- BUCLE PRINCIPAL ---
root.mainloop()
raiz.geometry("650x350")

#  Cambiar el color de fondo 
raiz.config(bg="blue")

#  Bucle infinito para mantener la ventana en ejecución (debe ir siempre al final)
raiz.mainloop()