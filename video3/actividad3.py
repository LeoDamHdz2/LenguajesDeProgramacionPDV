from tkinter import *
import os
from PIL import Image, ImageTk

root = Tk()
root.title("Práctica Label con Imagen")

mi_frame = Frame(root, width=500, height=400)
mi_frame.pack()

# Cargar la imagen JPG desde la misma carpeta que este archivo
ruta_imagen = os.path.join(os.path.dirname(os.path.abspath(__file__)), "pou.jpg")
mi_imagen = ImageTk.PhotoImage(Image.open(ruta_imagen))

# Asignar la imagen al Label
mi_label = Label(mi_frame, image=mi_imagen)
mi_label.place(x=100, y=100)

root.mainloop()