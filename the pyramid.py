import os
import tkinter as tk
from tkinter import ttk, font
from PIL import Image, ImageTk
import win32gui
import win32con
import win32api
import random

class CardImageButton:
    button_width = 189
    button_height = 270
    button_x_spacing = 10
    def __init__(self, canvas, x, y, prefix, rolled_game):
        self.image = []
        self.rolled_game = rolled_game
        self.button_widget = tk.Button(canvas, image=None,width=CardImageButton.button_width, height=CardImageButton.button_height)
        self.prefix = prefix
        # [Petra]: Not future-proofed in case of more than two prefixes... but I think it's fine.
        if prefix == 'p':
            self.button_widget.place(x=x, y=y)
        else: 
            self.button_widget.place(x=x + CardImageButton.button_width + CardImageButton.button_x_spacing, y=y)
        self.roll_objective_from_game()
    
    def roll_objective_from_game(self):
        __location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))+'\\Resources'
        image_folder = os.path.join(__location__, self.rolled_game)

        _image = Image.open(self.random_image_path_from_folder(image_folder, self.prefix))
        _image = _image.resize((CardImageButton.button_width, CardImageButton.button_height))
        _photo = ImageTk.PhotoImage(_image)

        self.image.clear()
        self.image.append(_photo)
        # [Petra]: Having CardImageButton.image be an array that we reference the tail of is likely unneeded. But this code worked for me.
        self.button_widget.config(image=self.image[-1])

    def random_image_path_from_folder(self,image_folder, prefix):
        images = [f for f in os.listdir(image_folder) if f.startswith(prefix) and f.endswith(('.png', '.jpg', '.jpeg'))]
        output = os.path.join(image_folder, random.choice(images))
        # [Petra]: Debugging; print loaded image filepath
        #print(str(output))
        return output

class ImageGalleryApp:
    def __init__(self, root, image_folder):
        self.root = root
        self.image_folder = image_folder
        self.images = []
        self.current_page = 0
        self.images_per_page = 24
        self.clicked_images = {}
        self.done_button_clicked = False

        # [Petra]: I am not certain, but I think we need to store our buttons here after making them, so they don't [...]
        # fall out of scope and get scooped up by Python's somewhat zealous garbage collector.
        self.primary_objective_buttons = []
        self.secondary_objective_buttons = []

        self.load_images()
        self.create_widgets()

    def load_images(self):
        # Load images from the specified folder
        image_files = [f for f in os.listdir(self.image_folder) if f.endswith(('.png', '.jpg', '.jpeg'))]
        for filename in image_files:
            image_path = os.path.join(self.image_folder, filename)
            image = Image.open(image_path)
            image = image.resize((CardImageButton.button_width, CardImageButton.button_height))  # Resize the image
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

        #[Petra]: Gotta update our font drip before we publish this. Arial and Helvetica do not have the juice.
        #[Petra]: They are neither fleek nor on-point.
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

    # [Petra]: Probably rename this function? 
    def show_page(self, page_number):
        start_idx = page_number * self.images_per_page
        end_idx = min((page_number + 1) * self.images_per_page, len(self.images))

        for widget in self.canvas.winfo_children():
            widget.grid_forget()  # Remove all previous buttons

        for i in range(start_idx, end_idx):
            image, filename = self.images[i]
            photo = ImageTk.PhotoImage(image)
            btn = tk.Button(self.canvas, image=photo, width=CardImageButton.button_width, height=CardImageButton.button_height,
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
        clicked_image = clicked_image.resize((CardImageButton.button_width // 4, CardImageButton.button_height // 4))
        clicked_photo = ImageTk.PhotoImage(clicked_image)

        clicked_label = tk.Label(self.clicked_frame, image=clicked_photo)
        clicked_label.image = clicked_photo
        clicked_label.pack(side=tk.LEFT)

    # [Petra]: GPT's clear screen clears screen, but immediately proceeds into non-screen-clearing as it sets up the "How Many Games" page. 
    # [Petra]: Likely this should be split into two functions. I'll leave it for now while I'm still getting my bearings.
    def clear_screen(self):
        self.done_button_clicked = True
        self.canvas.destroy()
        self.clicked_frame.destroy()
        self.next_button.place_forget()
        self.prev_button.place_forget()
        self.done_button.place_forget()

        self.canvas = tk.Canvas(self.root, width=1920, height=1080, highlightthickness=0, bg='#DAEE01')
        hwnd = self.canvas.winfo_id()
        colorkey = win32api.RGB(218, 238, 1)
        wnd_exstyle = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
        new_exstyle = wnd_exstyle | win32con.WS_EX_LAYERED
        win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, new_exstyle)
        win32gui.SetLayeredWindowAttributes(hwnd, colorkey, 255, win32con.LWA_COLORKEY)
        self.canvas.place(x=0, y=0)

        self.clicked_frame = tk.Frame(self.root)
        self.clicked_frame.place(x=950, y=940, anchor=tk.CENTER)

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
        self.start_button = ttk.Button(self.root, text="Start", command=self.prep_canvas_for_run, style="Large.TButton")
        self.start_button.place(x=960, y=800, anchor=tk.CENTER)

    def prep_canvas_for_run(self):
        self.games_1_button.place_forget()
        self.games_3_button.place_forget()
        self.games_5_button.place_forget()
        self.custom_games_entry.place_forget()
        self.start_button.place_forget()
        self.games_label.place_forget()

        # Clear the previous screen
        self.canvas.destroy()
        self.clicked_frame.destroy()
        
        # Create a new canvas for displaying selected images
        # [Petra]: Consider defining a single canvas in init which would be reused between functions.
        self.canvas = tk.Canvas(self.root, width=1920, height=1080, highlightthickness=0, bg='#DAEE01')
        hwnd = self.canvas.winfo_id()
        colorkey = win32api.RGB(218, 238, 1)
        wnd_exstyle = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
        new_exstyle = wnd_exstyle | win32con.WS_EX_LAYERED
        win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, new_exstyle)
        win32gui.SetLayeredWindowAttributes(hwnd, colorkey, 255, win32con.LWA_COLORKEY)
        self.canvas.place(x=0, y=0)

        self.clicked_frame = tk.Frame(self.root)
        self.clicked_frame.place(x=950, y=940, anchor=tk.CENTER)

        self.start_games()


    def start_games(self):
        self.primary_objective_buttons.clear()
        self.secondary_objective_buttons.clear()
        if self.games_selection:
            weighted_images = []
            for rolled_game, weight in self.clicked_images.items():
                weighted_images.extend([rolled_game] * weight)

            selected_images = random.sample(weighted_images, int(self.games_selection.get()))
            self.reroll_button = tk.Button(self.root, text="REROLL", font="Helvetica", bg="black", fg="white", cursor="hand2", command=self.start_games)
            self.reroll_button.place(x=940, y=10)  # Adjust the coordinates as needed

            #image_width = CardImageButton.button_width
            #image_height = CardImageButton.button_height
            #spacing = 10  # Adjust the spacing between images

            #if int(self.games_selection.get()) == 5:
            #         top_row_x_positions,bottom_row_x_positions = [],[]

            #         pair_spacing = 100  # Adjust the spacing between pairs
            #         pair_spacing_between_rows = 50  # Adjust the spacing between the top and bottom rows

            #         # Calculate x positions for top row
            #         x_start_top = (1920 - (6 * (2 * image_width + pair_spacing) - (pair_spacing*2))) // 2 + image_width

            #         top_row_x_positions = []
            #         for i in range(3):
            #             x_position = x_start_top + (2 * image_width + pair_spacing) * (i + 1)
            #             top_row_x_positions.append(x_position)

            #         # Calculate x positions for bottom row
            #         x_start_bottom = (1920 - (4 * (2 * image_width + pair_spacing) - (pair_spacing*2))) // 2 + image_width

            #         bottom_row_x_positions = []
            #         for i in range(2):
            #             x_position = x_start_bottom + (2 * image_width + pair_spacing) * (i+.5)
            #             bottom_row_x_positions.append(x_position)

            #         y_top = 300  # Y position for the top row
            #         y_bottom = y_top + image_height + pair_spacing_between_rows  # Y position for the bottom row

                    
            #         if i < 3:  # Display images on the top row
            #             x_position = top_row_x_positions[i]
            #             y_position = y_top
            #         else:  # Display images on the bottom row
            #             x_position = bottom_row_x_positions[i - 3]
            #             y_position = y_bottom
            #else:
                #x_position = (1920 - (image_width * (len(selected_images)*2) + spacing * (len(selected_images) - 1))) // 2
                #y_position = 300  # Adjust the y-position as needed

            if int(self.games_selection.get()) < 1:
                    print("Please select the number of games before starting.")
            
            x_position = 328
            y_position = 300

            for rolled_game in selected_images:
                rolled_game_in = rolled_game.split('.')[0]

                # [Petra]: repeated code, could probably make a function for this.
                p_btn = CardImageButton(self.canvas, x_position, y_position, 'p', rolled_game_in)
                p_btn.button_widget.config(command= p_btn.roll_objective_from_game)
                self.primary_objective_buttons.append(p_btn)

                s_btn = CardImageButton(self.canvas, x_position, y_position, 's', rolled_game_in)
                s_btn.button_widget.config(command= s_btn.roll_objective_from_game)
                self.secondary_objective_buttons.append(s_btn)

                x_position += 478
                if(x_position > 1284 and y_position < 620):
                    x_position = 567
                    y_position = 620
                           
    def close_program(self, event):
        self.root.destroy()

if __name__ == "__main__":
    __location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__))) + "\\Resources"
    image_folder_path = os.path.join(__location__, 'Card Backs App')  # Replace with the actual folder path containing your images

    root = tk.Tk()
    app = ImageGalleryApp(root, image_folder_path)

    root.attributes('-fullscreen', True)
    root.mainloop()
