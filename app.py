import tkinter as tk
from tkinter import messagebox
import os
import sys
import webbrowser

import pandas as pd
from jinja2 import Template
from datetime import datetime
from xhtml2pdf import pisa
from xhtml2pdf.default import DEFAULT_FONT
from xhtml2pdf.config.httpconfig import httpConfig

def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

httpConfig['allowLocalFiles'] = True
EXCEL_PATH = os.path.join(os.getcwd(), "SampleExcelFile.xlsx") 
PLANTILLAS_PATH = os.path.join(os.getcwd(), "plantillas") 
SALIDA_PATH = os.path.join(os.getcwd(), "salida")
font_path = resource_path("fonts/DejaVuSans.ttf")
DEFAULT_FONT["sans-serif"] = font_path
DEFAULT_FONT["DejaVuSans"] = font_path

def abrir_excel():
    if os.path.exists(EXCEL_PATH):
        os.startfile(EXCEL_PATH)
    else:
        messagebox.showerror("Error", f"No se encontró el archivo {EXCEL_PATH}")

def abrir_salida():
    if not os.path.exists(SALIDA_PATH):
        os.makedirs(SALIDA_PATH)
    os.startfile(SALIDA_PATH)

def generar_documentos_gui():
    if not os.path.exists(EXCEL_PATH):
        messagebox.showerror("Error", f"No se encontró el archivo {EXCEL_PATH}")
        return

    try:
        generar_documentos()
        messagebox.showinfo("Éxito", "Documentos generados correctamente.")
    except Exception as e:
        messagebox.showerror("Error", f"Ocurrió un error:\n{e}")

def abrir_readme():
    ruta = os.path.join(os.getcwd(), "README.md")
    webbrowser.open(ruta)

root = tk.Tk()
root.title("Generador de Documentos")
root.configure(bg="#F7F7F7")
root.geometry("800x500")
root.minsize(700, 400)
root.iconbitmap("icono.ico")

# Texto explicativo
texto = (
    "1. Prepara las plantillas en html. \n"
    "2. Llena el archivo Excel con los datos.\n"
    "3. Guarda y cierra el archivo Excel.\n"
    "4. Pulsa el botón 'Generar' para crear los documentos.\n"
    "5. Los archivos generados estarán en la carpeta 'salida'.\n"
)

label = tk.Label(root, text=texto, justify="left", font=("Segoe UI", 11), bg="#F7F7F7")
label.pack(pady=20)

# Botones
frame = tk.Frame(root)
frame.pack(pady=20)

tk.Button(frame, 
          text="Abrir Excel", 
          width=20, 
          height=2, 
          bg="#FF8A5C", 
          fg="white", 
          activebackground="#FF6A3D", 
          activeforeground="white", 
          relief="flat", 
          font=("Segoe UI", 10, "bold"),
          command=abrir_excel).grid(row=0, column=0, padx=10)
tk.Button(frame, 
          text="Generar Documentos", 
          width=20, 
          height=2, 
          bg="#FF8A5C", 
          fg="white", 
          activebackground="#FF6A3D", 
          activeforeground="white", 
          relief="flat", 
          font=("Segoe UI", 10, "bold"), 
          command=generar_documentos_gui).grid(row=0, column=1, padx=10)
tk.Button(frame, 
          text="Abrir carpeta salida", 
          width=20, 
          height=2, 
          bg="#FF8A5C", 
          fg="white", 
          activebackground="#DEDAD9", 
          activeforeground="white", 
          relief="flat", 
          font=("Segoe UI", 10, "bold"), 
          command=abrir_salida).grid(row=0, column=2, padx=10)
btn_readme = tk.Button(
    root,
    text="Ver README",
    command=abrir_readme,
    bg="#E0E0E0", 
    fg="#333333", 
    activebackground="#C8C8C8", 
    activeforeground="#000000",
    relief="flat",
    font=("Segoe UI", 10, "bold"),
    cursor="hand2"
)
btn_readme.place(relx=1.0, rely=1.0, anchor="se", x=-20, y=-20)

def generar_documentos():

    df = pd.read_excel("SampleExcelFile.xlsx")
    df = df.fillna("")

    plantillas = {
        "contrato": "plantillas/contrato_sampledoc.html",
        "aviso": "plantillas/aviso_sampledoc.html",
    }

    os.makedirs("salida", exist_ok=True)

    for _, row in df.iterrows():
        nombre_cliente = row["NOMBRE_CLIENTE"]
        carpeta = f"salida/{nombre_cliente}"
        os.makedirs(carpeta, exist_ok=True)

        for nombre, ruta in plantillas.items():
            with open(ruta, encoding="utf-8") as f:
                template = Template(f.read())

            html = template.render(
                CIUDAD=row["CIUDAD"],
                FECHA=row["FECHA"],
                NOMBRE_CLIENTE=row["NOMBRE_CLIENTE"],
                DNI_CLIENTE=row["DNI_CLIENTE"],
                NOMBRE_INQUILINO=row["NOMBRE_INQUILINO"],
                DNI_INQUILINO=row["DNI_INQUILINO"],
                DIRECCION_INMUEBLE=row["DIRECCION_INMUEBLE"],
                DURACION_MESES=row["DURACION_MESES"],
                PRECIO_MENSUAL=row["PRECIO_MENSUAL"],
                FIANZA=row["FIANZA"],
                CONCEPTO=row["CONCEPTO"],
                FECHA_LIMITE=row["FECHA_LIMITE"],
                IBAN=row["IBAN"],
                EMPRESA=row["EMPRESA"], 
                IMPORTE=row["IMPORTE"],
            )

            with open(f"{carpeta}/{nombre}.html", "w", encoding="utf-8") as f:
                f.write(html)

            # Generar PDF solo si existe condiciones.html
            ruta_html = f"{carpeta}/{nombre}.html"
            ruta_pdf = f"{carpeta}/{nombre_cliente}_{nombre}.pdf"

            if os.path.exists(ruta_html): 
                try: 
                    with open(ruta_html, "r", encoding="utf-8") as f:
                        html_content = f.read()
                        html_para_pdf = f"""
<html>
<head>
<meta charset="UTF-8">
<style>
@page {{ size: A4; margin: 2cm; }}
body {{ font-family: DejaVuSans; }}
</style>
</head>
<body>
{html_content}
</body>
</html>
"""                    
                    with open(ruta_pdf, "wb") as salida_pdf:
                        pisa.CreatePDF(html_para_pdf, dest=salida_pdf)                
                except Exception as e: 
                    print(f"Error generando PDF {nombre} para {nombre_cliente}: {e}")

    print("Documentos generados correctamente.")

root.mainloop()
