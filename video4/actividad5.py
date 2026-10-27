from tkinter import *

# 1. Configuración de la Ventana Principal (Raíz)
root = Tk()
root.title("Formulario con Entry y Grid")

# 2. Creación del Frame Contenedor
mi_frame = Frame(root, width=1200, height=600)
mi_frame.pack()

# --- CAMPO 1: NOMBRE ---
nombre_label = Label(mi_frame, text="Nombre:")
nombre_label.grid(row=0, column=0, sticky="e", padx=10, pady=10)

cuadro_nombre = Entry(mi_frame)
cuadro_nombre.grid(row=0, column=1, padx=10, pady=10)
# Personalización: texto en rojo y centrado al escribir
cuadro_nombre.config(fg="red", justify="center")

# --- CAMPO 2: CONTRASEÑA (PASSWORD) ---
pass_label = Label(mi_frame, text="Password:")
pass_label.grid(row=1, column=0, sticky="e", padx=10, pady=10)

cuadro_pass = Entry(mi_frame)
cuadro_pass.grid(row=1, column=1, padx=10, pady=10)
# Personalización: ocultar texto mostrando asteriscos
cuadro_pass.config(show="*")

# --- CAMPO 3: APELLIDO ---
apellido_label = Label(mi_frame, text="Apellido:")
apellido_label.grid(row=2, column=0, sticky="e", padx=10, pady=10)

cuadro_apellido = Entry(mi_frame)
cuadro_apellido.grid(row=2, column=1, padx=10, pady=10)

# --- CAMPO 4: DIRECCIÓN DE CASA ---
direccion_label = Label(mi_frame, text="Dirección de casa:")
direccion_label.grid(row=3, column=0, sticky="e", padx=10, pady=10)

cuadro_direccion = Entry(mi_frame)
cuadro_direccion.grid(row=3, column=1, padx=10, pady=10)

# 3. Bucle Principal de Ejecución
root.mainloop()