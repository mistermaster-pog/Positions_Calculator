import tkinter as tk
from tkinter import messagebox, scrolledtext, ttk, filedialog, Canvas, PhotoImage
from PIL import Image, ImageTk, ImageOps
import tkinter.font as tkFont
import random
import pyperclip
import matplotlib.pyplot as plt
import numpy as np
import math
import re
from scipy.spatial import KDTree
from perlin_noise import PerlinNoise
from objects.objects import objects

# --- Pierwszy program jako funkcja ---

class MapEditor:
    def __init__(self, parent):
        self.frame = ttk.Frame(parent)
        self.canvas = tk.Canvas(self.frame, width=800, height=600, bg="white")
        self.canvas.pack(fill="both", expand=True)

        self.parent = parent

        # Domyślne ustawienia mapy
        self.map_size = 805
        self.current_zoom = 1.0  # Zoom factor
        self.offset_x = 0  # Przesunięcie mapy w poziomie
        self.offset_y = 0  # Przesunięcie mapy w pionie
        self.dragging = False  # Flaga dla przesuwania mapy
        self.start_drag_x = 0
        self.start_drag_y = 0

        self.offset_x = 0
        self.offset_y = 0

        self.object_positions = []  # Lista obiektów (pozycje na mapie)
        self.object_code_lines = []  # Lista kodu (linia dla każdego obiektu)
        self.default_map_path = "images/map.png"  # Ustaw domyślną ścieżkę
        self.map_image_scaled = None  # Obraz po skalowaniu
        self.current_object_type = ""
        self.dir_mode = "Random"
        self.dir_value = 0.00
        self.objects = objects
        self.current_object_type = "Me"  # Domyślny typ obiektu
        self.selection_mode = "List"  # Domyślny tryb wyboru (ustawiony na List)

        self.search_entry = None  # Pole wyszukiwania obiektów
        
        self.insect_mode = tk.BooleanVar()
        self.radius_value = tk.DoubleVar()
        self.selected_insect_mode = tk.StringVar()
        self.water_level = 30.0

        # Cache dla przeskalowanych obrazów
        self.map_cache = {}

        # Interfejs GUI
        self.setup_gui()

    def setup_gui(self):
        # Główna ramka
        self.frame = ttk.Frame(self.parent)
        self.frame.pack(fill=tk.BOTH, expand=True)

        # Mapa
        self.canvas = tk.Canvas(self.frame, width=self.map_size, height=self.map_size, bg="white")
        self.canvas.grid(row=0, column=2, columnspan=3, rowspan=25, pady=10, padx=10)
        self.canvas.bind("<Button-1>", self.place_object)
        self.canvas.bind("<MouseWheel>", self.zoom_map)
        self.canvas.bind("<ButtonPress-2>", self.start_drag)
        self.canvas.bind("<B2-Motion>", self.drag_map)
        self.canvas.bind("<Motion>", self.on_mouse_move)  # Rejestracja zdarzenia ruchu myszy
        

        self.position_label = tk.Label(self.frame, text="X: 0, Y: 0", width=20, anchor="w")
        self.position_label.grid(row=25, column=2, sticky="w")  # Etykieta do wyświetlania współrzędnych

        self.type_label = tk.Label(self.frame, text="type= ", width=20, anchor="w")
        self.type_label.grid(row=25, column=3, sticky="w")  # Etykieta do wyświetlania typu obiektu


        # Tryb wyboru obiektu (manualny lub lista)
        self.selection_mode_var = tk.StringVar(value=self.selection_mode)
        ttk.Label(self.frame, text="Selection mode=").grid(row=1, column=0, sticky="e", padx=5)
        self.selection_mode_combo = ttk.Combobox(self.frame, textvariable=self.selection_mode_var, values=["List", "Manual"], state="readonly")
        self.selection_mode_combo.grid(row=1, column=1, sticky="ew", padx=5)
        self.selection_mode_combo.bind("<<ComboboxSelected>>", self.update_selection_mode)

        # Pole do wpisania typu obiektu
        ttk.Label(self.frame, text="Object type=").grid(row=2, column=0, sticky="e", padx=5)
        self.object_type_entry = ttk.Entry(self.frame, width=30)
        self.object_type_entry.grid(row=2, column=1, sticky="ew", padx=5)
        self.object_type_entry.insert(0, self.current_object_type)
        
        # Opcje dla dir
        self.dir_mode_label = ttk.Label(self.frame, text="Dir Mode:")
        self.dir_mode_label.grid(row=3, column=0, sticky="e", padx=5)
        ttk.Label(self.frame, text="dir=").grid(row=4, column=0, sticky="e", padx=5)
        self.dir_mode_combo = ttk.Combobox(self.frame, values=["Random", "Manual"], state="readonly", width=8)
        self.dir_mode_combo.current(0)
        self.dir_mode_combo.grid(row=3, column=1, sticky="w", padx=5)
        self.dir_mode_combo.bind("<<ComboboxSelected>>", self.update_dir_mode)

        self.dir_entry = ttk.Entry(self.frame, width=8)
        self.dir_entry.grid(row=4, column=1, sticky="w", padx=5)
        self.dir_entry.insert(0, "0.00")
        self.dir_entry.configure(state="disabled")

        # Insect Mode Options
        self.insect_mode_label = ttk.Label(self.frame, text="Insect Mode:")
        self.insect_mode_label.grid(row=8, column=0, sticky="e", padx=5)

        self.insect_mode_check = ttk.Checkbutton(self.frame, text="Enable", variable=self.insect_mode, command=self.toggle_insect_mode)
        self.insect_mode_check.grid(row=8, column=1, sticky="w", padx=5)

        ttk.Label(self.frame, text="Mode:").grid(row=9, column=0, sticky="e", padx=5)
        self.insect_mode_combo = ttk.Combobox(self.frame, values=["Idle Ant", "Advancing Ant", "Idle Moving Spider"], state="disabled", textvariable=self.selected_insect_mode, width=20)
        self.insect_mode_combo.grid(row=9, column=1, sticky="w", padx=5)
        self.selected_insect_mode.set("Idle Ant")
        self.insect_mode_combo.bind("<<ComboboxSelected>>", self.update_insect_image)

        ttk.Label(self.frame, text="radius/time:").grid(row=10, column=0, sticky="e", padx=5)
        self.radius_entry = ttk.Entry(self.frame, textvariable=self.radius_value, width=10)
        self.radius_entry.grid(row=10, column=1, sticky="w", padx=5)
        self.radius_entry.configure(state="disabled")

        ttk.Label(self.frame, text="Water Level (0-60):").grid(row=11, column=0, sticky="e", padx=5)
        self.water_level_entry = ttk.Entry(self.frame, width=10)
        self.water_level_entry.grid(row=11, column=1, sticky="w", padx=5)
        self.water_level_entry.insert(0, "30.0")

        ttk.Button(self.frame, text="Apply Water Level", command=self.apply_water_level).grid(row=11, column=1, sticky="e", padx=10)

        # Przyciski
        ttk.Button(self.frame, text="Load Positions", command=self.load_positions).grid(row=5, column=0, columnspan=1, sticky="e", padx=10)
        ttk.Button(self.frame, text="Load Map (.png/.bmp)", command=self.load_map).grid(row=5, column=1, sticky="w", padx=10)
        ttk.Button(self.frame, text="Clear Map", command=self.confirm_clear_map).grid(row=6, column=0, sticky="e", padx=10)
        ttk.Button(self.frame, text="Copy Output", command=self.copy_output).grid(row=7, column=1, columnspan=1, sticky="w", padx=10)
        ttk.Button(self.frame, text="Refresh", command=self.refresh).grid(row=6, column=1, columnspan=1, sticky="w", padx=10)

        self.delete_mode_var = tk.BooleanVar(value=False)  # Zmienna przechowująca stan trybu usuwania
        ttk.Checkbutton(self.frame, text="Delete Mode", variable=self.delete_mode_var, command=self.toggle_delete_mode).grid(row=7, column=0, columnspan=1, sticky="e", padx=10)
        self.canvas.bind("<Button-1>", self.on_canvas_click) # Przypisz obsługę kliknięcia myszy do funkcji delete_object

        # Ramka na output
        self.output_frame = ttk.Frame(self.frame)
        self.output_frame.grid(row=1, column=5, rowspan=25, pady=10, padx=10, sticky="nsew")

        # Pole tekstowe na wynik
        self.output_text = tk.Text(self.output_frame, height=30, width=90, wrap=tk.NONE)  # Wyłącz zawijanie tekstu
        self.output_text.pack(fill=tk.BOTH, expand=True)

        # Poziomy pasek przewijania
        self.scrollbar_x = tk.Scrollbar(self.output_frame, orient='horizontal', command=self.output_text.xview)
        self.scrollbar_x.pack(fill=tk.X, side=tk.BOTTOM)

        # Połączenie scrollbara z polem tekstowym
        self.output_text.config(xscrollcommand=self.scrollbar_x.set)


        self.load_default_map()

        # Pole wyszukiwania obiektów
        ttk.Label(self.frame, text="Search:").grid(row=12, column=0, sticky="e", padx=5)
        self.search_entry = ttk.Entry(self.frame, width=30)
        self.search_entry.grid(row=12, column=1, sticky="ew", padx=5)
        self.search_entry.bind("<KeyRelease>", self.filter_object_list)

        # Lista obiektów
        self.object_listbox = tk.Listbox(self.frame, selectmode=tk.EXTENDED, height=20)
        self.object_listbox.grid(row=13, column=0, columnspan=2, rowspan=4, sticky="nsew", padx=5, pady=5)
        self.object_listbox.bind("<ButtonRelease-1>", self.on_object_select)

        # Ramka na obraz wybranego obiektu
        self.selected_object_image_frame = ttk.Frame(self.frame, width=200, height=200)
        self.selected_object_image_frame.grid(row=17, column=0, columnspan=2, pady=10)
        self.selected_object_image_frame.grid_propagate(False)  # Zapobiega zmienianiu rozmiaru ramki

        self.selected_object_image_label = ttk.Label(self.selected_object_image_frame, anchor="center")
        self.selected_object_image_label.place(relx=0.5, rely=0.5, anchor="center")  # Obraz w środku ramki

        self.populate_object_list()
        self.object_listbox.selection_set(0)  # Zaznaczenie pierwszego elementu listy domyślnie
        self.update_selection_mode(None)  # Ustaw stan zgodnie z trybem domyślnym
        self.update_selected_object_image()  # Wyświetl domyślny obraz


    def on_mouse_move(self, event):
        mouse_x = event.x
        mouse_y = event.y

        # Przekształcenie współrzędnych kursora na współrzędne mapy
        map_x = (mouse_x - self.offset_x - self.map_size // 2) / self.current_zoom
        map_y = -(mouse_y - self.offset_y - self.map_size // 2) / self.current_zoom

        # Zaktualizowanie etykiety z nowymi współrzędnymi
        self.position_label.config(text=f"X: {map_x:.2f}, Y: {map_y:.2f}")

        # Sprawdzanie, czy kursor jest nad jakimkolwiek obiektem
        self.check_for_dot_hover(mouse_x, mouse_y)

    def check_for_dot_hover(self, mouse_x, mouse_y):
        # Sprawdzamy, czy kursor jest blisko którejkolwiek kropki na mapie
        for obj in self.object_positions:
            if len(obj) == 5:  # Kropka zawiera 5 elementów
                x, y, object_type, direction, dot = obj  # Rozpakowujemy na odpowiednie zmienne
            elif len(obj) == 4:  # Kropka zawiera 4 elementy
                x, y, object_type, dot = obj  # Rozpakowujemy na 4 elementy
                direction = None  # Brak kierunku, ustawiamy jako None
            else:
                continue  # Jeśli nie ma odpowiedniej liczby elementów, pomijamy ją

            # Przeliczamy pozycję kropki na mapie
            dot_x = self.offset_x + self.map_size // 2 + x * self.current_zoom
            dot_y = self.offset_y + self.map_size // 2 - y * self.current_zoom
            distance = ((mouse_x - dot_x) ** 2 + (mouse_y - dot_y) ** 2) ** 0.5  # Obliczamy odległość

            if distance < 10:  # Jeżeli kursor znajduje się w pobliżu kropki
                # Jeśli w object_type jest "type=", wyciągamy wartość po "type="
                if "type=" in object_type:
                    start_index = object_type.find("type=") + len("type=")
                    end_index = object_type.find(" ", start_index)
                    if end_index == -1:  # Jeśli nie ma spacji, bierzemy całą resztę tekstu
                        object_type = object_type[start_index:]
                    else:
                        object_type = object_type[start_index:end_index]
                # Wyświetlamy informacje o typie obiektu w osobnej etykiecie
                self.type_label.config(text=f"type= {object_type}")

                return  # Przerywamy po znalezieniu obiektu

        self.type_label.config(text="type= ")  # Jeżeli nie ma obiektu, usuwamy typ obiektu

    def clear_cache(self):
        self.map_cache = {}

    def update_selection_mode(self, event):
        """Aktualizuj tryb wyboru obiektu."""
        mode = self.selection_mode_var.get()
        if mode == "Manual":
            self.object_type_entry.configure(state="normal")
            self.object_listbox.configure(state="disabled")
            self.search_entry.configure(state="disabled")
        elif mode == "List":
            self.object_type_entry.configure(state="disabled")
            self.object_listbox.configure(state="normal")
            self.search_entry.configure(state="normal")

    def populate_object_list(self):
        """Wypełnij listę obiektów dostępnymi obiektami."""
        self.object_listbox.delete(0, tk.END)
        for object_type in self.objects.keys():
            self.object_listbox.insert(tk.END, object_type)

    def filter_object_list(self, event):
        """Filtruje listę obiektów na podstawie wpisanego tekstu."""
        search_term = self.search_entry.get().lower()
        self.object_listbox.delete(0, tk.END)
        for object_type in self.objects.keys():
            if search_term in object_type.lower():
                self.object_listbox.insert(tk.END, object_type)

    def on_object_select(self, event):
        """Obsługuje wybór obiektu z listy."""
        if self.selection_mode_var.get() != "List":
            return

        try:
            # Pobierz wszystkie zaznaczone elementy
            selections = self.object_listbox.curselection()
            selected_objects = [self.object_listbox.get(i) for i in selections]

            # Jeśli coś zaznaczono, zaktualizuj obiekt
            if selected_objects:
                self.selected_object_types = selected_objects  # Lista zaznaczonych obiektów
                self.current_object_type = random.choice(self.selected_object_types)  # Losowy wybór
                self.object_type_entry.delete(0, "end")
                self.object_type_entry.insert(0, self.current_object_type)

                if not self.insect_mode.get():
                    self.update_selected_object_image()
        except IndexError:
            pass

    def update_selected_object_image(self):
        """Aktualizuje wyświetlany obraz wybranego obiektu."""
        if self.insect_mode.get():
            self.update_insect_image()
            return

        image_file = self.objects.get(self.current_object_type, "icons/none.png")
        self.set_image(image_file)

    def set_image(self, image_file):
        """Ustawia obraz w ramce."""
        try:
            img = Image.open(image_file)
            img = img.resize((200, 200), Image.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            self.selected_object_image_label.configure(image=photo, text="")
            self.selected_object_image_label.image = photo
        except FileNotFoundError:
            self.selected_object_image_label.configure(text=f"Image not found for {self.current_object_type}", image="")
            self.selected_object_image_label.image = None


    def update_dir_mode(self, event):
        self.dir_mode = self.dir_mode_combo.get()
        if self.dir_mode == "Manual":
            self.dir_entry.configure(state="normal")
        else:
            self.dir_entry.configure(state="disabled")

    def load_default_map(self):
        try:
            img = Image.open("images/map.png")
            img = img.resize((self.map_size, self.map_size), Image.Resampling.LANCZOS)
            # Odwrócenie kolorów obrazu
            img = ImageOps.invert(img.convert("RGB"))
            self.map_image = img
            self.map_image_scaled = ImageTk.PhotoImage(img)
            self.canvas.create_image(self.map_size // 2, self.map_size // 2, anchor="center", image=self.map_image_scaled, tags="map")
            self.apply_water_level()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load default map: {e}")

    def load_map(self):
        self.clear_cache()
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png;*.bmp")])
        if file_path:
            try:
                img = Image.open(file_path)
                img = img.resize((self.map_size, self.map_size), Image.Resampling.LANCZOS)
                # Odwrócenie kolorów obrazu
                img = ImageOps.invert(img.convert("RGB"))
                self.map_image = img
                self.map_image_scaled = ImageTk.PhotoImage(img)
                self.canvas.delete("all")
                self.offset_x = 0
                self.offset_y = 0
                self.canvas.create_image(self.map_size // 2, self.map_size // 2, anchor=tk.CENTER, image=self.map_image_scaled, tags="map")
                self.object_positions = []
                self.object_code_lines = []
                messagebox.showinfo("Success", "Map loaded successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load map: {e}")

    def zoom_map(self, event):
        # Określ czynnik skali na podstawie kierunku scrollowania
        scale_factor = 1.1 if event.delta > 0 else 0.9
        new_zoom = max(1.0, self.current_zoom * scale_factor)

        # Pozycja kursora względem mapy
        cursor_x = self.canvas.canvasx(event.x)
        cursor_y = self.canvas.canvasy(event.y)

        # Relatywna pozycja kursora w skali mapy
        rel_x = (cursor_x - self.offset_x) / (self.map_size * self.current_zoom)
        rel_y = (cursor_y - self.offset_y) / (self.map_size * self.current_zoom)

        # Aktualizacja zoomu
        self.current_zoom = new_zoom

        # Sprawdź, czy obraz w odpowiednim rozmiarze jest w cache
        if new_zoom not in self.map_cache:
            # Przeskaluj obraz i dodaj go do cache
            new_size = int(self.map_image.width * new_zoom), int(self.map_image.height * new_zoom)
            scaled_image = self.map_image.resize(new_size, Image.Resampling.LANCZOS)
            self.map_cache[new_zoom] = ImageTk.PhotoImage(scaled_image)

        self.map_image_scaled = self.map_cache[new_zoom]

        # Oblicz nowy offset na podstawie kursora
        self.offset_x += (rel_x * self.map_size * (scale_factor - 1))
        self.offset_y += (rel_y * self.map_size * (scale_factor - 1))

        # Rysowanie mapy i obiektów
        self.redraw_map()
        self.apply_water_level()

    def start_drag(self, event):
        self.dragging = True
        self.start_drag_x = event.x
        self.start_drag_y = event.y

    def drag_map(self, event):
        if self.dragging:
            dx, dy = event.x - self.start_drag_x, event.y - self.start_drag_y

            # Ograniczenia przesuwania mapy
            max_offset_x = (self.current_zoom - 1) * self.map_size // 2
            max_offset_y = (self.current_zoom - 1) * self.map_size // 2

            self.offset_x = max(-max_offset_x, min(max_offset_x, self.offset_x + dx))
            self.offset_y = max(-max_offset_y, min(max_offset_y, self.offset_y + dy))

            self.start_drag_x, self.start_drag_y = event.x, event.y
            self.redraw_map()

    def end_drag(self, event):
        self.dragging = False

    def redraw_map(self):
        if self.map_image_scaled:
            self.canvas.delete("map")
            self.canvas.create_image(self.offset_x + self.map_size // 2, self.offset_y + self.map_size // 2, anchor=tk.CENTER, image=self.map_image_scaled, tags="map")

        for i, obj in enumerate(self.object_positions):
            self.canvas.delete(obj[-1])
            scaled_x = int(self.offset_x + self.map_size // 2 + obj[0] * self.current_zoom)
            scaled_y = int(self.offset_y + self.map_size // 2 - obj[1] * self.current_zoom)

            dot = self.canvas.create_oval(scaled_x - 3, scaled_y - 3, scaled_x + 3, scaled_y + 3, fill="red", outline="red")
            self.object_positions[i] = (*obj[:-1], dot)

    def load_water_level(self, water_level):
        if not self.map_image:
            messagebox.showerror("Error", "No map loaded. Please load a map first.")
            return

        try:
            if water_level not in self.map_cache:
                gray_threshold = int(water_level * 4)
                gray_image = self.map_image.convert("L")

                colored_image = Image.new("RGB", gray_image.size)
                pixels = gray_image.load()
                colored_pixels = colored_image.load()

                for y in range(gray_image.size[1]):
                    for x in range(gray_image.size[0]):
                        gray_value = pixels[x, y]
                        if gray_value <= gray_threshold:
                            inverted_intensity = gray_value + 150
                            colored_pixels[x, y] = (
                                min(255, int(150 * inverted_intensity / 255)),
                                min(255, int(200 * inverted_intensity / 255)),
                                min(255, int(255 * inverted_intensity / 255)),
                            )
                        else:
                            colored_pixels[x, y] = (gray_value, gray_value, gray_value)

                self.map_cache[water_level] = colored_image

            colored_image = self.map_cache[water_level]
            new_size = int(self.map_size * self.current_zoom)
            scaled_colored_image = colored_image.resize((new_size, new_size), Image.Resampling.LANCZOS)

            self.map_image_scaled = ImageTk.PhotoImage(scaled_colored_image)
            self.redraw_map()

        except Exception as e:
            messagebox.showerror("Error", f"Failed to apply water level: {e}")

    def apply_water_level(self):
        try:
            water_level = float(self.water_level_entry.get())
            if not 0 <= water_level <= 60:
                raise ValueError("Water level must be between 0 and 60.")
            self.load_water_level(water_level)
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid water level: {e}")

    def toggle_insect_mode(self):
        """Włącza/wyłącza tryb insektów oraz aktualizuje stan elementów UI."""
        state = "normal" if self.insect_mode.get() else "disabled"
        self.insect_mode_combo.configure(state=state)
        self.radius_entry.configure(state=state)

        # Wyłącz elementy związane z trybem wyboru obiektów
        object_type_state = "disabled" if self.insect_mode.get() else "normal"
        self.object_type_entry.configure(state=object_type_state)
        self.object_listbox.configure(state=object_type_state)
        self.selection_mode_combo.configure(state=object_type_state)
        self.search_entry.configure(state=object_type_state)

        if self.insect_mode.get():
            self.update_insect_image()
        else:
            self.update_selected_object_image()  # Reset obraz po wyłączeniu Insect Mode

    def toggle_delete_mode(self):
        """Włącza/wyłącza tryb usuwania obiektów i aktualizuje stan elementów UI."""
        if self.delete_mode_var.get():
            # Włącz tryb usuwania: wyłącz wszystkie inne kontrolki i przypisz kliknięcia do usuwania
            self.insect_mode_combo.configure(state="disabled")
            self.radius_entry.configure(state="disabled")
            self.object_type_entry.configure(state="disabled")
            self.object_listbox.configure(state="disabled")
            self.selection_mode_combo.configure(state="disabled")
            self.search_entry.configure(state="disabled")
            self.dir_mode_combo.configure(state="disabled")
            
            # Disable insect mode label and checkbutton
            self.insect_mode_label.configure(state="disabled")
            self.insect_mode_check.configure(state="disabled")
            self.dir_mode_label.configure(state="disabled")  # Ensure this label is created
            self.dir_mode_combo.configure(state="disabled")

            # Przypisz kliknięcie do funkcji usuwania obiektów
            self.canvas.bind("<Button-1>", self.delete_object)
        else:
            # Wyłącz tryb usuwania: przywróć wszystkie kontrolki
            self.insect_mode_combo.configure(state="normal")
            self.radius_entry.configure(state="normal")
            self.object_type_entry.configure(state="normal")
            self.object_listbox.configure(state="normal")
            self.selection_mode_combo.configure(state="normal")
            self.search_entry.configure(state="normal")
            self.dir_mode_combo.configure(state="normal")
            
            # Przywróć etykiety i przyciski
            self.insect_mode_label.configure(state="normal")
            self.insect_mode_check.configure(state="normal")
            self.dir_mode_label.configure(state="normal")
            self.dir_mode_combo.configure(state="normal")

            # Przypisz kliknięcie do funkcji stawiania obiektów
            self.canvas.bind("<Button-1>", self.place_object)

            # Przywróć obrazek obiektu po wyłączeniu delete mode
            self.update_selected_object_image()

    def update_insect_image(self, event=None):
        """Aktualizuje obraz dla trybu Insect Mode."""
        selected_mode = self.selected_insect_mode.get()
        if selected_mode in ["Idle Ant", "Advancing Ant"]:
            image_file = "icons/AlienAnt.png"
        elif selected_mode == "Idle Moving Spider":
            image_file = "icons/AlienSpider.png"
        else:
            image_file = "icons/none.png"

        self.set_image(image_file)

    def place_object(self, event):
        if self.selection_mode_var.get() == "Manual":
            self.current_object_type = self.object_type_entry.get()

        if not self.current_object_type:
            messagebox.showwarning("Warning", "Please select or enter a valid object type!")
            return

        if self.selection_mode_var.get() == "List" and hasattr(self, "selected_object_types") and self.selected_object_types:
            self.current_object_type = random.choice(self.selected_object_types)

        x = (event.x - self.map_size // 2 - self.offset_x) / self.current_zoom
        y = (self.map_size // 2 - event.y + self.offset_y) / self.current_zoom

        if self.dir_mode == "Random":
            direction = round(random.uniform(0, 2), 1)
        else:
            try:
                direction = float(self.dir_entry.get())
                if not 0 <= direction <= 2:
                    raise ValueError("dir value must be between 0 and 2")
            except ValueError:
                messagebox.showerror("Error", "Invalid dir value. Please enter a number between 0 and 2.")
                return

        cmdline = ""
        if self.insect_mode.get():
            selected_mode = self.selected_insect_mode.get()

            if selected_mode == "Idle Ant":
                self.current_object_type = "AlienAnt"
                script1 = "antict.txt"
                radius = self.radius_value.get()
                rand_x = x + random.uniform(-radius / 2, radius / 2)
                rand_y = y + random.uniform(-radius / 2, radius / 2)
                cmdline = f"cmdline= {rand_x:.2f}; {rand_y:.2f}; {radius:.2f} script1=\"{script1}\""

            elif selected_mode == "Advancing Ant":
                self.current_object_type = "AlienAnt"
                script1 = "ant02.txt"
                time_delay = self.radius_value.get()
                cmdline = f"cmdline= {time_delay:.2f} script1=\"{script1}\""

            elif selected_mode == "Idle Moving Spider":
                self.current_object_type = "AlienSpider"
                script1 = "spidict.txt"
                radius = self.radius_value.get()
                rand_x = x + random.uniform(-radius / 2, radius / 2)
                rand_y = y + random.uniform(-radius / 2, radius / 2)
                cmdline = f"cmdline= {rand_x:.2f}; {rand_y:.2f}; {radius:.2f} script1=\"{script1}\""

        obj_id = len(self.object_positions)
        dot_x = int(self.offset_x + self.map_size // 2 + x * self.current_zoom)
        dot_y = int(self.offset_y + self.map_size // 2 - y * self.current_zoom)

        dot = self.canvas.create_oval(dot_x - 3, dot_y - 3, dot_x + 3, dot_y + 3, fill="red", outline="red")
        self.object_positions.append((x, y, self.current_object_type, direction, dot))

        output_line = f"CreateObject pos={x:.2f};{y:.2f} dir={direction} type={self.current_object_type}"
        if cmdline:
            output_line += f" {cmdline} run=1"

        self.object_code_lines.append(output_line)
        self.update_output()

    def on_canvas_click(self, event):
        """Obsługuje kliknięcie na canvas w zależności od aktywnego trybu."""
        if self.delete_mode_var.get():
            # Jeśli aktywny jest Delete Mode, wykonaj usuwanie obiektu
            self.delete_object(event)
        else:
            # W przeciwnym razie wykonaj dodawanie obiektu
            self.place_object(event)

    def delete_object(self, event):
        """Usuwa obiekt po kliknięciu w trybie Delete Mode."""
        if not self.delete_mode_var.get():
            return

        # Przekształć współrzędne kliknięcia na pozycję na mapie
        x_click = (event.x - self.map_size // 2 - self.offset_x) / self.current_zoom
        y_click = (self.map_size // 2 - event.y + self.offset_y) / self.current_zoom

        # Znajdź najbliższy obiekt w zasięgu 10 jednostek
        radius = 10 / self.current_zoom  # Promień zależny od zoomu
        for i, obj in enumerate(self.object_positions):
            if len(obj) == 5:  # Case for 5 values: (x, y, obj_type, direction, dot)
                x, y, obj_type, direction, dot = obj
            elif len(obj) == 4:  # Case for 4 values: (x, y, obj_type, direction)
                x, y, obj_type, direction = obj
                dot = None  # If there's no dot, set it to None or handle accordingly
            else:
                continue  # Skip if the tuple doesn't match expected length

            # Check if the click is within the deletion radius
            if abs(x - x_click) <= radius and abs(y - y_click) <= radius:
                # Usuń obiekt z canvas (usuwa tylko jeśli dot istnieje)
                if dot:
                    self.canvas.delete(dot)

                # Usuń obiekt z list
                del self.object_positions[i]
                del self.object_code_lines[i]

                # Zaktualizuj wyjście i mapę
                self.update_output()
                self.redraw_map()
                break  # Przerywamy po znalezieniu pierwszego obiektu

    def load_positions(self):
        # Open file dialog to select a file
        filepath = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
        if not filepath:
            return  # If the user cancels, do nothing

        try:
            # Open the file with UTF-8 encoding
            with open(filepath, "r", encoding="utf-8") as file:
                lines = file.readlines()

            objects_added = 0
            # Process each line in the file
            for line in lines:
                line = line.strip()  # Remove leading/trailing whitespaces
                if line.startswith("//") or not line:
                    continue  # Skip comments and empty lines

                # Match the line against the pattern
                match = re.match(r"^CreateObject pos=\s*([\d.-]+);\s*([\d.-]+)\s*(.+)", line)
                if match:
                    x = float(match.group(1))
                    y = float(match.group(2))
                    rest_of_line = match.group(3)  # Rest of the line (e.g., type, direction)

                    # Add object to the map (without removing previous objects)
                    self.add_object_to_map(x, y, rest_of_line)
                    objects_added += 1

            # Update the output field with the newly loaded objects
            self.update_output()

            # Display a message depending on the result
            if objects_added > 0:
                messagebox.showinfo("Success", f"Loaded {objects_added} objects successfully!")
            else:
                messagebox.showinfo("Info", "No valid objects found in the file.")

        except UnicodeDecodeError as e:
            messagebox.showerror("Error", f"Failed to load positions: {e}")
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred: {e}")

    def add_object_to_map(self, x, y, rest_of_line):
        # Calculate position in pixels on the map based on zoom and offset
        dot_x = int(self.offset_x + self.map_size // 2 + x * self.current_zoom)
        dot_y = int(self.offset_y + self.map_size // 2 - y * self.current_zoom)

        # Add the object as a dot on the canvas
        dot = self.canvas.create_oval(dot_x - 3, dot_y - 3, dot_x + 3, dot_y + 3, fill="red", outline="red")

        # Append the object data to the list of object positions
        self.object_positions.append((x, y, rest_of_line, dot))

        # Format the object creation line for the output
        output_line = f"CreateObject pos={x:.2f};{y:.2f} {rest_of_line}"
        self.object_code_lines.append(output_line)

        # Update the output display with the new object
        self.update_output()

    def update_output(self):
        # Clear the existing text in the output text widget
        self.output_text.delete(1.0, tk.END)

        # Insert the new object lines into the output text area
        for line in self.object_code_lines:
            self.output_text.insert(tk.END, f"{line}\n")

        # Allow the user to edit the output text if needed
        self.output_text.configure(state="normal")

    def refresh(self):
        # Clear the map before redrawing objects
        self.canvas.delete("all")
        self.object_positions = []  # Reset the list of object positions
        self.object_code_lines = []  # Reset the list of object code lines

        # Read and process the edited data from output_text widget
        lines = self.output_text.get(1.0, tk.END).splitlines()

        for line in lines:
            line = line.strip()
            
            # Skip comments and empty lines
            if line.startswith("//") or not line:
                continue

            # Regex pattern to match the CreateObject command
            match = re.match(r"^CreateObject pos=\s*([\d.-]+);\s*([\d.-]+)\s*(.+)", line)
            if match:
                x = float(match.group(1))  # Extract X coordinate
                y = float(match.group(2))  # Extract Y coordinate
                rest_of_line = match.group(3)  # Remaining part of the line (e.g., direction, type)

                # Add object to the map based on the extracted data
                self.add_object_to_map(x, y, rest_of_line)

        self.redraw_map()  # Update the map after objects are added
        messagebox.showinfo("Success", "Map refreshed successfully!")

    def copy_output(self):
       self.parent.clipboard_clear()
       self.parent.clipboard_append(self.output_text.get(1.0, tk.END))
       self.parent.update()

    def confirm_clear_map(self):
        """Zapytanie potwierdzające przed wyczyszczeniem mapy."""
        confirm = messagebox.askyesno("Confirm Clear Map", "Are you sure you want to clear the map?")
        if confirm:
            self.clear_map()

    def clear_map(self):
        self.canvas.delete("all")
        self.object_positions = []
        self.object_code_lines = []
        self.canvas.delete(self.object_positions)
        self.update_output()
        self.redraw_map()

    def get_frame(self):
        return self.frame

class RandomPositionsGenerator:
    def __init__(self, parent):
        self.frame = ttk.Frame(parent)

        # Input fields
        ttk.Label(self.frame, text="Number of Objects:").grid(row=0, column=0, sticky="e")
        self.num_objects_entry = ttk.Entry(self.frame, width=5)
        self.num_objects_entry.grid(row=0, column=1, sticky="w")
        self.num_objects_entry.insert(0, "100")

        ttk.Label(self.frame, text="Object Types (comma-separated):").grid(row=1, column=0, sticky="e")
        self.object_types_entry = ttk.Entry(self.frame, width=80)
        self.object_types_entry.grid(row=1, column=1, columnspan=2)
        self.object_types_entry.insert(0, "Greenery15,Greenery16,Greenery17")

        ttk.Label(self.frame, text="Center Position (x; y):").grid(row=2, column=0, sticky="e")
        self.center_position_entry = ttk.Entry(self.frame, width=20)
        self.center_position_entry.grid(row=2, column=1, sticky="w")
        self.center_position_entry.insert(0, "0.00; 0.00")

        ttk.Label(self.frame, text="Radius:").grid(row=3, column=0, sticky="e")
        self.radius_entry = ttk.Entry(self.frame, width=5)
        self.radius_entry.grid(row=3, column=1, sticky="w")
        self.radius_entry.insert(0, "200")

        ttk.Label(self.frame, text="No-Spawn Radius:").grid(row=4, column=0, sticky="e")
        self.no_spawn_radius_entry = ttk.Entry(self.frame, width=5)
        self.no_spawn_radius_entry.grid(row=4, column=1, sticky="w")
        self.no_spawn_radius_entry.insert(0, "50")

        ttk.Label(self.frame, text="Randomness Algorithm:").grid(row=5, column=0, sticky="e")
        self.algorithm_var = tk.StringVar(value="Uniform")
        self.algorithm_menu = ttk.Combobox(self.frame, textvariable=self.algorithm_var, state="readonly")
        self.algorithm_menu["values"] = ("Uniform", "Normal", "Perlin", "Cellular Automata")
        self.algorithm_menu.grid(row=5, column=1, sticky="w")

        # Output field
        ttk.Label(self.frame, text="Output:").grid(row=9, column=0, sticky="w")
        self.output_text = scrolledtext.ScrolledText(self.frame, width=80, height=20)
        self.output_text.grid(row=10, column=0, rowspan=3, columnspan=4, padx=5, pady=5)

        # Buttons
        ttk.Button(self.frame, text="Generate Positions", command=self.generate_positions).grid(row=6, column=0, pady=10)
        ttk.Button(self.frame, text="Copy to Clipboard", command=self.copy_to_clipboard).grid(row=6, column=1, pady=10)
        ttk.Button(self.frame, text="Reset", command=self.reset).grid(row=7, column=0, pady=10)

    def generate_positions(self):
        try:
            num_objects = int(self.num_objects_entry.get())
            object_types = self.object_types_entry.get().split(",")
            center_x, center_y = map(float, self.center_position_entry.get().split(";"))
            radius = float(self.radius_entry.get())
            no_spawn_radius = float(self.no_spawn_radius_entry.get())
            algorithm = self.algorithm_var.get()
        except ValueError:
            messagebox.showerror("Error", "Please enter valid input values.")
            return

        positions = []
        self.output_text.delete(1.0, tk.END)

        if algorithm == "Cellular Automata":
            positions = self.cellular_automata_algorithm(num_objects, center_x, center_y, radius)
        else:
            for _ in range(num_objects):
                while True:
                    if algorithm == "Uniform":
                        angle = random.uniform(0, 2 * np.pi)
                        distance = random.uniform(no_spawn_radius, radius)
                    elif algorithm == "Normal":
                        angle = random.uniform(0, 2 * np.pi)
                        distance = min(max(random.gauss((radius + no_spawn_radius) / 2, (radius - no_spawn_radius) / 4), no_spawn_radius), radius)
                    elif algorithm == "Perlin":
                        angle = random.uniform(0, 2 * np.pi)
                        distance = random.uniform(no_spawn_radius, radius)

                        noise = PerlinNoise(octaves=4, seed=random.randint(0, 10000))
                        noise_factor_x = noise([angle, 0])
                        noise_factor_y = noise([angle, 1])

                        distance += noise_factor_x * (radius - no_spawn_radius) * 0.1
                        distance = min(max(distance, no_spawn_radius), radius)

                    x = center_x + distance * np.cos(angle)
                    y = center_y + distance * np.sin(angle)
                    if len(positions) < num_objects:
                        positions.append((x, y))
                        break

        for i, pos in enumerate(positions):
            obj_type = random.choice(object_types)
            self.output_text.insert(tk.END, f"CreateObject pos={pos[0]:.2f};{pos[1]:.2f} dir={random.uniform(0, 2):.1f} type={obj_type}\n")

        self.draw_grid(positions)

    def cellular_automata_algorithm(self, num_objects, center_x, center_y, radius):
        grid_size = int(radius * 2 + 1)
        grid = [[0 for _ in range(grid_size)] for _ in range(grid_size)]
        center = grid_size // 2

        for _ in range(num_objects):
            while True:
                x = random.randint(max(0, center - int(radius)), min(grid_size - 1, center + int(radius)))
                y = random.randint(max(0, center - int(radius)), min(grid_size - 1, center + int(radius)))
                if grid[x][y] == 0:
                    grid[x][y] = 1
                    break

        iterations = 10
        for _ in range(iterations):
            new_grid = [[0 for _ in range(grid_size)] for _ in range(grid_size)]
            for x in range(1, grid_size - 1):
                for y in range(1, grid_size - 1):
                    neighbors = sum([
                        grid[x - 1][y - 1], grid[x][y - 1], grid[x + 1][y - 1],
                        grid[x - 1][y],                grid[x + 1][y],
                        grid[x - 1][y + 1], grid[x][y + 1], grid[x + 1][y + 1],
                    ])
                    if grid[x][y] == 1 and 2 <= neighbors <= 3:
                        new_grid[x][y] = 1
                    elif grid[x][y] == 0 or neighbors == 3:
                        new_grid[x][y] = 1
            grid = new_grid

        positions = []
        for x in range(grid_size):
            for y in range(grid_size):
                if grid[x][y] == 1:
                    real_x = (x - center) + center_x
                    real_y = (y - center) + center_y
                    positions.append((real_x, real_y))
                    if len(positions) >= num_objects:
                        return positions

        return positions

    def copy_to_clipboard(self):
        text = self.output_text.get(1.0, tk.END).strip()
        if text:
            pyperclip.copy(text)
            messagebox.showinfo("Copied", "Output copied to clipboard!")
        else:
            messagebox.showerror("Error", "No output to copy.")

    def draw_grid(self, positions):
        plt.figure(figsize=(8, 8))
        plt.xlim(-360, 360)
        plt.ylim(-360, 360)
        plt.grid(True, which='both', linestyle='--', linewidth=0.5)
        plt.axhline(0, color='black', linewidth=1)
        plt.axvline(0, color='black', linewidth=1)
        plt.title("Object Positions on Grid")
        plt.xlabel("X Coordinate")
        plt.ylabel("Y Coordinate")

        for pos in positions:
            plt.plot(pos[0], pos[1], 'o', color='red')

        plt.show()

    def reset(self):
        self.num_objects_entry.delete(0, tk.END)
        self.object_types_entry.delete(0, tk.END)
        self.center_position_entry.delete(0, tk.END)
        self.radius_entry.delete(0, tk.END)
        self.no_spawn_radius_entry.delete(0, tk.END)
        self.output_text.delete(1.0, tk.END)

    def get_frame(self):
        return self.frame

# Funkcja do stworzenia zakładki Object Placement Generator
class SpaceShipObjects:
    def __init__(self, parent):
        self.frame = ttk.Frame(parent)

        # Input fields for robots
        tk.Label(self.frame, text="Robots (leave blank if none):").grid(row=0, column=0, sticky="w")
        self.robot_entries = []
        for i in range(4):
            tk.Label(self.frame, text=f"Robot {i + 1}:").grid(row=i + 1, column=0, sticky="w")
            entry = tk.Entry(self.frame, width=45)
            entry.grid(row=i + 1, column=0, sticky="e")
            self.robot_entries.append(entry)

        # Input field for objects
        tk.Label(self.frame, text="Objects (leave blank if none):").grid(row=5, column=0, sticky="w")
        objects_frame = ttk.Frame(self.frame)
        objects_frame.grid(row=6, column=0, columnspan=2, sticky="w")

        self.object_entries = []
        for i in range(12):  # Allow up to 6 different object types
            tk.Label(objects_frame, text=f"Object {i + 1}:").grid(row=i, column=0, sticky="e")
            obj_type_entry = tk.Entry(objects_frame, width=20)
            obj_type_entry.grid(row=i, column=1, sticky="w")
            tk.Label(objects_frame, text="Quantity:").grid(row=i, column=2, sticky="e")
            quantity_entry = tk.Entry(objects_frame, width=3)
            quantity_entry.grid(row=i, column=3, sticky="w")
            self.object_entries.append((obj_type_entry, quantity_entry))

        # Input fields for ship position and direction
        tk.Label(self.frame, text="Ship Position (x; y):").grid(row=7, column=0, sticky="e")
        self.ship_position_entry = tk.Entry(self.frame, width=20)
        self.ship_position_entry.grid(row=7, column=1, sticky="w")
        self.ship_position_entry.insert(0, "0.00; 0.00")

        tk.Label(self.frame, text="Ship Direction (0.00-1.99):").grid(row=8, column=0, sticky="e")
        self.ship_direction_entry = tk.Entry(self.frame, width=5)
        self.ship_direction_entry.grid(row=8, column=1, sticky="w")
        self.ship_direction_entry.insert(0, "0.00")

        # Output field
        tk.Label(self.frame, text="Output:").grid(row=10, column=0, sticky="w")
        self.output_text = scrolledtext.ScrolledText(self.frame, width=80, height=20)
        self.output_text.grid(row=10, column=0, columnspan=3, padx=5, pady=5)

        # Default positions and objects
        self.default_positions = {
            "ship": (0.00, 0.00),
            "me": (-3.25, 0.00),
            "robots": [(-3.25, 3.25), (-3.25, -3.25), (0.00, 3.25), (0.00, -3.25)],
            "objects": [
                (2.50, 3.75), (3.75, 3.75), (2.50, 2.50), (3.75, 2.50),
                (2.50, 0.63), (3.75, 0.63), (2.50, -0.62), (3.75, -0.62),
                (2.50, -2.50), (3.75, -2.50), (2.50, -3.75), (3.75, -3.75)
            ]
        }

        def adjust_positions(base_position, positions, direction):
            base_x, base_y = base_position
            angle = (2.0 - direction) * math.pi  # Calculate angle in radians

            def rotate_and_translate(point):
                p_x, p_y = point
                rotated_x = base_x + (p_x - base_x) * math.cos(angle) - (p_y - base_y) * math.sin(angle)
                rotated_y = base_y + (p_x - base_x) * math.sin(angle) + (p_y - base_y) * math.cos(angle)
                return rotated_x, rotated_y

            return [rotate_and_translate((x + base_x, y + base_y)) for x, y in positions]

        # Functions
        def generate_positions():
            try:
                ship_position = tuple(map(float, self.ship_position_entry.get().split(";"))) if self.ship_position_entry.get() else self.default_positions["ship"]
                ship_direction = float(self.ship_direction_entry.get()) if self.ship_direction_entry.get() else 0.0

                me_position = adjust_positions(ship_position, [self.default_positions["me"]], ship_direction)[0]
                robot_positions = adjust_positions(ship_position, self.default_positions["robots"], ship_direction)
                object_positions = adjust_positions(ship_position, self.default_positions["objects"], ship_direction)
            except ValueError:
                messagebox.showerror("Error", "Invalid input for ship position or direction.")
                return

            self.output_text.delete(1.0, tk.END)
            self.output_text.insert(tk.END, f"CreateObject pos= {ship_position[0]:.2f}; {ship_position[1]:.2f} dir={ship_direction:.2f} type=SpaceShip run=1\n")
            self.output_text.insert(tk.END, f"CreateObject pos= {me_position[0]:.2f}; {me_position[1]:.2f} dir={ship_direction:.2f} type=Me\n")

            for i, entry in enumerate(self.robot_entries):
                robot_type = entry.get().strip()
                if robot_type:
                    pos = robot_positions[i]
                    self.output_text.insert(
                        tk.END, f"CreateObject pos= {pos[0]:.2f}; {pos[1]:.2f} dir={ship_direction:.2f} type={robot_type}\n"
                    )

            objects = []
            for obj_type_entry, quantity_entry in self.object_entries:
                obj_type = obj_type_entry.get().strip()
                quantity = quantity_entry.get().strip()
                if obj_type and quantity.isdigit():
                    objects.extend([obj_type] * int(quantity))

            if len(objects) > len(object_positions):
                messagebox.showerror("Error", "Too many objects for available positions.")
                return

            for obj_type, pos in zip(objects, object_positions):
                self.output_text.insert(
                    tk.END, f"CreateObject pos= {pos[0]:.2f}; {pos[1]:.2f} dir={ship_direction:.2f} type={obj_type}\n"
                )

        def copy_to_clipboard():
            text = self.output_text.get(1.0, tk.END).strip()
            if text:
                pyperclip.copy(text)
                messagebox.showinfo("Copied", "Output copied to clipboard!")
            else:
                messagebox.showerror("Error", "No output to copy.")

        def reset():
            for entry in self.robot_entries:
                entry.delete(0, tk.END)
            for obj_type_entry, quantity_entry in self.object_entries:
                obj_type_entry.delete(0, tk.END)
                quantity_entry.delete(0, tk.END)
            self.ship_position_entry.delete(0, tk.END)
            self.ship_direction_entry.delete(0, tk.END)
            self.output_text.delete(1.0, tk.END)

        # Buttons
        tk.Button(self.frame, text="Generate Positions", command=generate_positions).grid(row=9, column=0, pady=10)
        tk.Button(self.frame, text="Copy to Clipboard", command=copy_to_clipboard).grid(row=9, column=1, pady=10)
        tk.Button(self.frame, text="Reset", command=reset).grid(row=9, column=2, pady=10)

        text_label = tk.Label(self.frame, text="Input types and quantities of the objects and program will place\nthem on the Space Ship according to the below diagram.          ", font=("Arial", 14))
        text_label.grid(row=0, column=4, rowspan=3, sticky="w", pady=(10, 5))

        text_label = tk.Label(self.frame, text="For example 4 x PowerCell and 6 x Titanium will place PowerCell\nin 1-4 spots, Titanium in 5-10 spots and leave 11-12 spots empty.", font=("Arial", 10))
        text_label.grid(row=3, column=4, rowspan=3, sticky="w", pady=(10, 5))

        ship_path = "images/ship.png"  # Replace with the correct path
        ship_image = Image.open(ship_path)
        ship_image = ship_image.resize((600, 600), Image.Resampling.LANCZOS)
        ship = ImageTk.PhotoImage(ship_image)

        ship_label = tk.Label(self.frame, image=ship)
        ship_label.grid(row=6, column=4, rowspan=11)
        ship_label.image = ship  # Prevent garbage collection

    def get_frame(self):
        return self.frame


# Funkcja zamykająca aplikację z potwierdzeniem
def close_application():
    # Pytanie, czy na pewno chcesz zamknąć aplikację
    if messagebox.askyesno("Close Application?", "Are you sure you want to close the application?"):
        root.destroy()  # Zamyka aplikację

root = tk.Tk()
root.title("Colobot Positions Multi-Tool Calculator")

# Uruchomienie aplikacji w maksymalnym oknie
root.state('zoomed')  # Maksymalizuje okno przy starcie
root.attributes("-fullscreen", True)
root.bind("<Escape>", lambda event: root.attributes("-fullscreen", False))

# Ramka nad zakładkami
button_frame = tk.Frame(root)
button_frame.pack(side="top", fill="x", padx=10, pady=10)

logo_path = "images/logo-root.png"  # Zmień ścieżkę na plik logo
logo_image = Image.open(logo_path)
logo_image = logo_image.resize((60, 60), Image.Resampling.LANCZOS)
main_logo = ImageTk.PhotoImage(logo_image)

# Logo programu
label = tk.Label(button_frame, image=main_logo, anchor="w", justify="left")
label.pack(side="left")

# Nazwa programu
label = tk.Label(button_frame, text="Colobot Positions Multi-Tool Calculator", font=("Arial", 20, "bold"), anchor="w", justify="left")
label.pack(side="left")


# Przycisk z ikonką
button_icon = tk.PhotoImage(file="images/icon4.png")  # Ikona przycisku
button = ttk.Button(button_frame, image=button_icon, command=close_application)
button.pack(side="right")
label = tk.Label(button_frame, text="Exit ", font=("Arial", 12))
label.pack(side="right")

# Styl dla zakładek
style = ttk.Style()

# Styl zakładek (wstążek) nieaktywnych
style.configure("TNotebook.Tab", font=("Arial", 12), padding=[10, 5], background="#5990C2", foreground="black")

# Styl zakładek aktywnych
#style.map("TNotebook.Tab", background=[("selected", "#4CAF50")], foreground=[("selected", "black")])

# Notebook (zakładki)
notebook = ttk.Notebook(root)
notebook.pack(fill="both", expand=True)

# Wczytanie ikon (obrazów)
icon1 = tk.PhotoImage(file="images/icon1.png")  # Upewnij się, że plik jest w tym samym folderze
icon2 = tk.PhotoImage(file="images/icon2.png")
icon3 = tk.PhotoImage(file="images/icon3.png")
#icon4 = tk.PhotoImage(file="icon4.png")

# Dodanie zakładek z obrazkami
# Zakładka 1: The Map Editor
map_editor = MapEditor(notebook)
notebook.add(map_editor.get_frame(), text=" The Map Editor", image=icon1, compound="left")

# Zakładka 2: Random Positions Generator
positions_tab = RandomPositionsGenerator(notebook)
notebook.add(positions_tab.get_frame(), text=" Random Positions Generator", image=icon2, compound="left")

# Zakładka 3: Space Ship Objects
ship_objects_tab = SpaceShipObjects(notebook)
notebook.add(ship_objects_tab.get_frame(), text=" Space Ship Objects", image=icon3, compound="left")

# Ramka pod zakładkami
foot_frame = tk.Frame(root)
foot_frame.pack(side="bottom", fill="x", padx=10, pady=10)

# Etykieta z tekstem w lewym dolnym rogu
label = tk.Label(foot_frame, text="Colobot Positions Multi-Tool Calculator Version: 1.1.2\nAuthor: bipel88", font=("Arial", 8), anchor="w", justify="left")
label.pack(side="left")

# Etykieta z tekstem w lewym dolnym rogu
label = tk.Label(foot_frame, text="Press ESC to exit full screen", font=("Arial", 15, "italic"), anchor="e", justify="right")
label.pack(side="right")
root.iconbitmap('images/icon.ico')
root.mainloop()
