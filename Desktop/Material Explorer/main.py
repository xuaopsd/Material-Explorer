import tkinter as tk
import os
import glob
from tkinter import ttk, filedialog
from PIL import Image, ImageTk
from functools import lru_cache
from customtkinter import *

# Create the main window
window = CTk()
window.title("Material Explorer")

screen_width = window.winfo_screenwidth()
screen_height = window.winfo_screenheight()

window_width = 800
window_height = 600

x = (screen_width // 2) - (window_width // 2)
y = (screen_height // 2) - (window_height // 2)
print(f"{window_width}x{window_height}+{x}+{y}")

window.geometry(f"{window_width}x{window_height}+{x}+{y}")  # Set the window size

set_appearance_mode("dark")
images = []

@lru_cache(maxsize=100)
def load_image(img_path, size):
    img = Image.open(img_path).resize((size, size))
    return ImageTk.PhotoImage(img)

# Select folder function
def select_folder():
    folder_path = filedialog.askdirectory()
    if folder_path:
        entry.delete(0, tk.END)  # Clear the text field
        entry.insert(0, folder_path)
        
        global images
        images = []

        for filename in glob.glob(os.path.join(folder_path, '**', '*_preview.*'), recursive=True):
            images.append(filename)  # Store only the image paths

        populate_grid()

# Create a frame to contain the widgets
frame = CTkFrame(window)
frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)  # Center frame with padding

# Configure the main window to make the frame responsive
window.rowconfigure(0, weight=1)
window.columnconfigure(0, weight=1)

# Add a label to the frame
text = CTkLabel(frame, text="Select folder with materials")
text.grid(row=0, column=0, columnspan=2, padx=10, pady=(50,0), sticky="s")  # Spanning across columns for better alignment

# Add an entry field for the folder path
entry = CTkEntry(frame, width=300)
entry.grid(row=1, column=0, padx=10, pady=10, sticky="ew")

# Configure the frame to make the entry field expandable
frame.columnconfigure(0, weight=1)

# Add a button to select a folder
button = CTkButton(frame, text="...", command=select_folder, corner_radius=5)
button.grid(row=1, column=1, padx=(0,10), pady=5, sticky="w", columnspan=1, rowspan=1)
button.configure(width=50)

# Slider to icon sizes
icon_size = 50

def slider_event(value):
    global icon_size
    icon_size = int(value)  # Update icon size
    update_images(icon_size)

slider = CTkSlider(frame, from_=32, to=512, command=slider_event)
slider.grid(row=2, column=0)

# Canvas and Scrollbar
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

def on_enter(event, label, img_path):
    button.configure(cursor="hand2")
    label.configure(width=icon_size + icon_size/3, height=icon_size + icon_size/3)  # Increase size when mouse enters
    
    file_name = os.path.basename(img_path)  
    base_name = file_name.split('_')[-2]  
    
    path_label = CTkLabel(label, text=base_name, font=('Arial', 8), anchor='w', text_color="black")  
    path_label.place(relx=0, rely=1, anchor='sw', x=5, y=-5)  
    label.path_label = path_label  

def on_leave(event, label):
    button.configure(cursor="arrow")
    label.configure(width=icon_size, height=icon_size)  
    
    if hasattr(label, 'path_label'):
        label.path_label.destroy()
        del label.path_label

def on_click(event, img_path):
    print(f"Imagem clicada: {img_path}")
    folder_path = os.path.dirname(img_path)
    os.startfile(folder_path)

def populate_grid():
    start_index = canvas.yview()[0] * len(images)
    end_index = start_index + canvas.winfo_height() // icon_size * 3  

    for i in range(int(start_index), int(end_index)):
        if i < len(images):
            img_path = images[i]
            try:
                # Load image with cache
                photo = load_image(img_path, icon_size)

                img_label = CTkLabel(scrollable_frame, image=photo, width=icon_size, height=icon_size)
                img_label.image = photo  

                img_label.bind("<Enter>", lambda event, label=img_label, img_path=img_path: on_enter(event, label, img_path))
                img_label.bind("<Leave>", lambda event, label=img_label: on_leave(event, label))
                img_label.bind("<Button-1>", lambda event, img_path=img_path: on_click(event, img_path))

                img_label.grid(row=i // 3, column=i % 3, padx=10, pady=10)

            except Exception as e:
                print(f"Erro ao carregar a imagem {img_path}: {e}")

    materials_Detected = CTkLabel(window, text=f"{len(images)} materials detected")
    materials_Detected.place(relx=1.0, rely=1.0, anchor="se", x=-10, y=-10)

def update_images(icon_size):
    """Update all images' size in the grid without recreating the labels."""
    for widget in scrollable_frame.winfo_children():
        if isinstance(widget, CTkLabel):
            img_path = images[scrollable_frame.winfo_children().index(widget)]  # Get the correct image path based on the widget index
            photo = load_image(img_path, icon_size)
            widget.configure(image=photo, width=icon_size, height=icon_size)
            widget.image = photo
            

# Run the main loop
window.mainloop()
