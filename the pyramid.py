import os
import tkinter as tk
from tkinter import ttk, font
from PIL import Image, ImageTk
import win32gui
import win32con
import win32api
import random

class ImageGalleryApp:
    def __init__(self, root, image_folder):
        self.root = root
        self.image_folder = image_folder
        self.images = []
        self.current_page = 0
        self.images_per_page = 24
        self.button_width = 189
        self.button_height = 270
        self.clicked_images = {}
        self.done_button_clicked = False

        self.load_images()
        self.create_widgets()

    def load_images(self):
        # Load images from the specified folder
        image_files = [f for f in os.listdir(self.image_folder) if f.endswith(('.png', '.jpg', '.jpeg'))]
        for filename in image_files:
            image_path = os.path.join(self.image_folder, filename)
            image = Image.open(image_path)
            image = image.resize((self.button_width, self.button_height))  # Resize the image
            self.images.append((image, filename))  # Store both image and filename

    def create_widgets(self):

        self.background_image = Image.open("Resources/bg.png")  # Replace with your background image path
        self.background_photo = ImageTk.PhotoImage(self.background_image)

        # Create a Label to display the background image
        bg_label = tk.Label(self.root, image=self.background_photo)
        bg_label.place(x=0, y=0, relwidth=1, relheight=1)

        
        self.canvas = tk.Canvas(root, width=1920, height=1080, highlightthickness=0, bg='#DAEE01')
        hwnd = self.canvas.winfo_id()
        colorkey = win32api.RGB(218,238,1) 
        wnd_exstyle = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
        new_exstyle = wnd_exstyle | win32con.WS_EX_LAYERED
        win32gui.SetWindowLong(hwnd,win32con.GWL_EXSTYLE,new_exstyle)
        win32gui.SetLayeredWindowAttributes(hwnd,colorkey,255,win32con.LWA_COLORKEY)

        self.canvas.place(x=0, y=0)

        close_font = font.Font(family="Arial", size=16, weight="bold")  # Adjust font properties as needed
        self.close_button = tk.Label(self.root, text="X", font=close_font, bg="red", fg="white", cursor="hand2")
        self.close_button.place(x=1880, y=10)  # Adjust the coordinates as needed
        self.close_button.bind("<Button-1>", self.close_program)

        self.next_button = ttk.Button(self.root, text="Next", command=self.next_page, style="Large.TButton")
        self.next_button.place(x=1700, y=1000)

        self.prev_button = ttk.Button(self.root, text="Previous", command=self.prev_page, style="Large.TButton")
        self.prev_button.place(x=220, y=1000)

        self.done_button = ttk.Button(self.root, text="I'm Done Drafting my Deck!", command=self.clear_screen, style="Large.TButton")
        self.done_button.place(x=950, y=1000, anchor=tk.CENTER)

        self.clicked_frame = tk.Frame(self.root)
        self.clicked_frame.place(x=950, y=940, anchor=tk.CENTER)
        
        self.show_page(0)

    def show_page(self, page_number):
        start_idx = page_number * self.images_per_page
        end_idx = min((page_number + 1) * self.images_per_page, len(self.images))

        for widget in self.canvas.winfo_children():
            widget.grid_forget()  # Remove all previous buttons

        for i in range(start_idx, end_idx):
            image, filename = self.images[i]
            photo = ImageTk.PhotoImage(image)
            btn = tk.Button(self.canvas, image=photo, width=self.button_width, height=self.button_height,
                            command=lambda f=filename: self.add_to_clicked_images(f))  # Pass filename to lambda
            btn.image = photo
            btn.grid(row=(i - start_idx) // 8, column=(i - start_idx) % 8, padx=22, pady=10)

    def next_page(self):
        self.current_page = (self.current_page + 1) % ((len(self.images) + self.images_per_page - 1) // self.images_per_page)
        self.show_page(self.current_page)

    def prev_page(self):
        self.current_page = (self.current_page - 1) % ((len(self.images) + self.images_per_page - 1) // self.images_per_page)
        self.show_page(self.current_page)

    def add_to_clicked_images(self, filename):
        if filename in self.clicked_images:
            self.clicked_images[filename] += 1
        else:
            self.clicked_images[filename] = 1

        clicked_image_path = os.path.join(self.image_folder, filename)
        clicked_image = Image.open(clicked_image_path)
        clicked_image = clicked_image.resize((self.button_width // 4, self.button_height // 4))
        clicked_photo = ImageTk.PhotoImage(clicked_image)

        clicked_label = tk.Label(self.clicked_frame, image=clicked_photo)
        clicked_label.image = clicked_photo
        clicked_label.pack(side=tk.LEFT)

    
    def clear_screen(self):
        self.done_button_clicked = True
        self.canvas.destroy()
        self.clicked_frame.destroy()

        self.next_button.place_forget()
        self.prev_button.place_forget()
        self.done_button.place_forget()

        # Create a label asking how many games to play
        self.games_label = tk.Label(self.root, text="How many games would you like to play?", font=("Helvetica", 18))
        self.games_label.place(x=960, y=500, anchor=tk.CENTER)

        # Create buttons for 1, 3, and 5 games
        self.games_selection = tk.StringVar()  # Variable to store the selected number of games

        def set_games_selection(value):
            self.games_selection.set(value)

        self.games_1_button = tk.Button(self.root, text="1", font=("Helvetica", 24), command=lambda: set_games_selection("1"))
        self.games_1_button.place(x=800, y=600, anchor=tk.CENTER)

        self.games_3_button = tk.Button(self.root, text="3", font=("Helvetica", 24), command=lambda: set_games_selection("3"))
        self.games_3_button.place(x=960, y=600, anchor=tk.CENTER)

        self.games_5_button = tk.Button(self.root, text="5", font=("Helvetica", 24), command=lambda: set_games_selection("5"))
        self.games_5_button.place(x=1120, y=600, anchor=tk.CENTER)

        # Create an entry box for custom number of games
        self.custom_games_entry = tk.Entry(self.root, textvariable=self.games_selection, font=("Helvetica", 24))
        self.custom_games_entry.place(x=960, y=700, anchor=tk.CENTER)

        # Create a "Start" button to proceed
        self.start_button = ttk.Button(self.root, text="Start", command=self.start_games, style="Large.TButton")
        self.start_button.place(x=960, y=800, anchor=tk.CENTER)

    def start_games(self):
        self.games_1_button.place_forget()
        self.games_3_button.place_forget()
        self.games_5_button.place_forget()
        self.custom_games_entry.place_forget()
        self.start_button.place_forget()
        self.games_label.place_forget()

        if self.games_selection:
            weighted_images = []
            for image_name, weight in self.clicked_images.items():
                weighted_images.extend([image_name] * weight)

            selected_images = random.sample(weighted_images, int(self.games_selection.get()))

            # Clear the previous screen
            self.canvas.destroy()
            self.clicked_frame.destroy()

            # Create a new canvas for displaying selected images
            self.canvas = tk.Canvas(self.root, width=1920, height=1080, highlightthickness=0, bg='#DAEE01')
            hwnd = self.canvas.winfo_id()
            colorkey = win32api.RGB(218, 238, 1)
            wnd_exstyle = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
            new_exstyle = wnd_exstyle | win32con.WS_EX_LAYERED
            win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, new_exstyle)
            win32gui.SetLayeredWindowAttributes(hwnd, colorkey, 255, win32con.LWA_COLORKEY)
            self.canvas.place(x=0, y=0)

            # Calculate the width and height for each image placement
            image_width = self.button_width
            image_height = self.button_height
            spacing = 10  # Adjust the spacing between images
            if int(self.games_selection.get()) == 5:
                top_row_x_positions,bottom_row_x_positions = [],[]

                pair_spacing = 100  # Adjust the spacing between pairs
                pair_spacing_between_rows = 50  # Adjust the spacing between the top and bottom rows

                # Calculate x positions for top row
                x_start_top = (1920 - (6 * (2 * image_width + pair_spacing) - (pair_spacing*2))) // 2 + image_width

                top_row_x_positions = []
                for i in range(3):
                    x = x_start_top + (2 * image_width + pair_spacing) * (i + 1)
                    top_row_x_positions.append(x)

                # Calculate x positions for bottom row
                x_start_bottom = (1920 - (4 * (2 * image_width + pair_spacing) - (pair_spacing*2))) // 2 + image_width

                bottom_row_x_positions = []
                for i in range(2):
                    x = x_start_bottom + (2 * image_width + pair_spacing) * (i+.5)
                    bottom_row_x_positions.append(x)

                y_top = 300  # Y position for the top row
                y_bottom = y_top + image_height + pair_spacing_between_rows  # Y position for the bottom row

                for i, image_name in enumerate(selected_images):
                    if i < 3:  # Display images on the top row
                        x = top_row_x_positions[i]
                        y = y_top
                    else:  # Display images on the bottom row
                        x = bottom_row_x_positions[i - 3]
                        y = y_bottom

                    self.display_selected_image(image_name.split('.')[0], x, y)
            else:
                x_position = (1920 - (image_width * (len(selected_images)*2) + spacing * (len(selected_images) - 1))) // 2
                y_position = 300  # Adjust the y-position as needed

                for image_name in selected_images:
                    self.display_selected_image(image_name.split('.')[0], x_position, y_position)
                    x_position += (image_width*2) + (spacing*2)
        else:
            print("Please select the number of games before starting.")

    def display_selected_image(self, image_name, x, y):
        
        __location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))+'\\Resources'
        image_folder = os.path.join(__location__, image_name)
        p_images = [f for f in os.listdir(image_folder) if f.startswith('p') and f.endswith(('.png', '.jpg', '.jpeg'))]
        s_images = [f for f in os.listdir(image_folder) if f.startswith('s') and f.endswith(('.png', '.jpg', '.jpeg'))]

        p_image_path = os.path.join(image_folder, random.choice(p_images))
        s_image_path = os.path.join(image_folder, random.choice(s_images))

        p_image = Image.open(p_image_path)
        s_image = Image.open(s_image_path)

        p_image = p_image.resize((self.button_width, self.button_height))
        s_image = s_image.resize((self.button_width, self.button_height))

        p_photo = ImageTk.PhotoImage(p_image)
        s_photo = ImageTk.PhotoImage(s_image)

        p_label = tk.Label(self.canvas, image=p_photo, borderwidth=0, highlightthickness=0)
        p_label.photo = p_photo
        p_label.place(x=x, y=y)

        s_label = tk.Label(self.canvas, image=s_photo, borderwidth=0, highlightthickness=0)
        s_label.photo = s_photo
        s_label.place(x=x + self.button_width + 10, y=y)  # Place the second image to the right of the first image

    def close_program(self, event):
        self.root.destroy()

if __name__ == "__main__":
    __location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__))) + "\\Resources"
    image_folder_path = os.path.join(__location__, 'Card Backs App')  # Replace with the actual folder path containing your images

    root = tk.Tk()
    app = ImageGalleryApp(root, image_folder_path)

    root.attributes('-fullscreen', True)
    root.mainloop()
