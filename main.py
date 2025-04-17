import tkinter as tk
import os
import glob
from tkinter import filedialog
from PIL import Image
from functools import lru_cache
from customtkinter import *

window = CTk()
window.title("Material Explorer")
screen_width = window.winfo_screenwidth()
screen_height = window.winfo_screenheight()
window_width = 800
window_height = 600
x = (screen_width // 2) - (window_width // 2)
y = (screen_height // 2) - (window_height // 2)
window.geometry(f"{window_width}x{window_height}+{x}+{y}")
set_appearance_mode("dark")

images = []

@lru_cache(maxsize=100)
def load_image(img_path, size):
    img = Image.open(img_path).resize((size, size))
    return CTkImage(img, size=(size, size))

def select_folder():
    folder_path = filedialog.askdirectory()
    if folder_path:
        entry.delete(0, tk.END)  
        entry.insert(0, folder_path)
        
        global images
        images = []

        for filename in glob.glob(os.path.join(folder_path, '**', '*_preview.*'), recursive=True):
            images.append(filename)  
       
        create_canvas()

        populate_grid()

def create_canvas():
    global canvas, scrollbar, scrollable_frame
    canvas = CTkCanvas(window)
    scrollbar = CTkScrollbar(window, orientation="vertical", command=canvas.yview)
    scrollable_frame = CTkFrame(canvas)

    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.grid(row=1, column=0, sticky="nsew")
    scrollbar.grid(row=1, column=1, sticky="ns")
   
    canvas.bind("<Configure>", on_scroll)

def on_scroll(event):
    """Detecta o scroll e atualiza as imagens visíveis."""
    canvas.update_idletasks()
    populate_grid()

frame = CTkFrame(window)
frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5,)  

window.rowconfigure(0, weight=1)
window.columnconfigure(0, weight=1)

text = CTkLabel(frame, text="Select folder with materials")
text.grid(row=0, column=0, columnspan=2, padx=10, pady=(50,0), sticky="s")  

entry = CTkEntry(frame, width=300)
entry.grid(row=1, column=0, padx=10, pady=10, sticky="ew")

frame.columnconfigure(0, weight=1)

button = CTkButton(frame, text="...", command=select_folder, corner_radius=5)
button.grid(row=1, column=1, padx=(0,10), pady=5, sticky="w", columnspan=1, rowspan=1)
button.configure(width=50)

slider_frame = CTkFrame(frame, width=256)  
slider_frame.grid(row=2, column=0, columnspan=2, sticky="nsew", padx=5, pady=10)

slider_frame.columnconfigure(0, weight=1)
slider_frame.columnconfigure(1, weight=3)

sliderLabel = CTkLabel(slider_frame, text="Icon Size")
sliderLabel.grid(row=0, column=0, padx=5, pady=5, sticky="e")

icon_size = 64

def slider_event(value):
    global icon_size
    icon_size = int(value)  
    update_images(icon_size)

slider = CTkSlider(slider_frame, from_=32, to=512, command=slider_event, state="disabled")
slider.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
slider.set(64)

currentIconSize = CTkLabel(slider_frame, text=f"{icon_size}px") 
currentIconSize.grid(row=0, column=2, padx=5, pady=5, sticky="e")

def on_enter(event, label, img_path):
    
    label.configure(width=int(icon_size + icon_size / 3), height=int(icon_size + icon_size / 3), cursor="hand2")
    
    file_name = os.path.basename(img_path)  
    base_name = file_name.split('_')[-2]  

def on_leave(event, label):
    label.configure(width=icon_size, height=icon_size, cursor="arrow")  

def on_click(event, img_path):
    print(f"Imagem clicada: {img_path}")
    folder_path = os.path.dirname(img_path)
    os.startfile(folder_path)

def populate_grid():
    """Popula apenas as imagens visíveis no momento."""
    
    for widget in scrollable_frame.winfo_children():
        widget.destroy()
    
    available_width = canvas.winfo_width()  
    if available_width == 1:  
        available_width = window.winfo_width()

    columns = max(1, available_width // (icon_size + 20))  
    for col in range(columns):
        scrollable_frame.columnconfigure(col, weight=1)
    
    for i, img_path in enumerate(images):
        try:
            photo = load_image(img_path, icon_size)
            file_name = os.path.basename(img_path)
            base_name = file_name.split('_')[-2]

            img_label = CTkLabel(scrollable_frame, image=photo, width=icon_size, height=icon_size, text=base_name)
            img_label.image = photo

            img_label.bind("<Enter>", lambda event, label=img_label, img_path=img_path: on_enter(event, label, img_path))
            img_label.bind("<Leave>", lambda event, label=img_label: on_leave(event, label))
            img_label.bind("<Button-1>", lambda event, img_path=img_path: on_click(event, img_path))
            
            row = i // columns
            col = i % columns
            img_label.grid(row=row, column=col, padx=10, pady=10)

        except Exception as e:
            print(f"Erro ao carregar a imagem {img_path}: {e}")
   
    slider.configure(state="normal")
    materials_Detected = CTkLabel(window, text=f"{len(images)} materials detected")
    materials_Detected.place(relx=1.0, rely=1.0, anchor="se", x=-10, y=-10)

def update_images(icon_size):
    """Update all images' size in the grid without recreating the labels."""
    for widget in scrollable_frame.winfo_children():
        if isinstance(widget, CTkLabel):
            img_path = images[scrollable_frame.winfo_children().index(widget)]  
            photo = load_image(img_path, icon_size)
            widget.configure(image=photo, width=icon_size, height=icon_size)
            widget.image = photo

window.mainloop()
