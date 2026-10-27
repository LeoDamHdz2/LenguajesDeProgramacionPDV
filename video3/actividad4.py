from tkinter import *

# Creación de la raíz y frame principal
root = Tk()
root.title("sixsenevn")

mi_frame = Frame(root, width=500, height=400)
mi_frame.pack()

# Creación y configuración del Label
mi_label = Label(mi_frame, text="betito es el lord sixseven", fg="blue", font=("Comic Sans MS", 20))
mi_label.place(x=100, y=200)

# Sintaxis abreviada (si no se reutilizará la variable 'mi_label'):
#Label(mi_frame, text="Hola alumnos de Python", fg="red", font=("Comic Sans MS", 18)).place(x=100, y=200)

root.mainloop()