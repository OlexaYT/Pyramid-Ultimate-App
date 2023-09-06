import os
import tkinter as tk
from tkinter import ttk, font, Misc
from PIL import Image, ImageTk
import win32gui
import win32con
import win32api
import random
import csv
import json

class GameDraft:
    def __init__(self, canvas, rolled_game, x_position, y_position, scale=[1.0,1.0]) -> None:
        self.rolled_game=rolled_game
        self.canvas = canvas
        self.primaries=[]
        self.curse=[]
        self.secondaries=[]
        self.x_position = x_position
        self.y_position = y_position
        self.scale = scale
        self.GenerateCardImageButtons(rolled_game)
    
    def GenerateCardImageButtons(self, rolled_game):
        #NOTE: Insert duplicate reroll code here, and/or dynamic additional objective draft.
        self.primaries.clear()
        self.curse.clear()
        self.secondaries.clear()

        #[Petra] Edited curse probability for debug purposes
        curse = bool(random.randrange(0,5)==0)
        if (curse):
           self.scale = [self.scale[0], self.scale[1]]
           self.CardImageButtonFactory('c')
        match rolled_game:
            case "monster train":
                self.CardImageButtonFactory('p', [0.66,0.66])
                self.CardImageButtonFactory('p', [0.66,0.66])
                self.CardImageButtonFactory('s')
            case "sporcle":
                self.CardImageButtonFactory('p')
                self.CardImageButtonFactory('s')
                self.CardImageButtonFactory('s')
            case "wordle":
                self.CardImageButtonFactory('p')
                self.CardImageButtonFactory('s')
                self.CardImageButtonFactory('s')
            case "question deck free":
                for i in range(5):
                    self.CardImageButtonFactory('p', [0.66, 0.66])
            case "question deck paid":
                for i in range(5):
                    self.CardImageButtonFactory('p', [0.66, 0.66])
            case _:
                self.CardImageButtonFactory('p')
                self.CardImageButtonFactory('s')
        
            # [Petra]: Debug, shows if curses are rolled
            #print("Curse rolled")
        self.PlaceCardImageButtons()
        return

    def CardImageButtonFactory(self, prefix, scale=[1.0,1.0]):
        btn = CardImageButton(self.canvas, self.x_position, self.y_position, prefix, self.rolled_game, [self.scale[0]*scale[0],self.scale[1]*scale[1]])
        btn.button_widget.config(command= btn.roll_objective_from_game)
        match prefix:
            case 'p':
                self.primaries.append(btn)
            case 's':
                self.secondaries.append(btn)
            case 'c':
                self.curse.append(btn)
            case _:
                print("Error: Unhandled prefix passed to CardImageButtonFactory()")
        return btn
    
    def PlaceCardImageButtons(self):
        if len(self.curse) > 0:
            curse_space = 1.0
        else:
            curse_space = 0
        for p in range(len(self.primaries)): #For each primary-objective button
            target = self.primaries[p] #Grab target button from array
            position = self.ui_position_calc(p, self.x_position, self.y_position, 'p', target.scale, curse_space) #Pass to ui_position_calc to do the math.
            target.button_widget.place(x=position[0],y=position[1]) #set the position to the output of ui_position_calc
        for s in range(len(self.secondaries)):
            target = self.secondaries[s]
            position = self.ui_position_calc(s, self.x_position, self.y_position, 's', target.scale, curse_space)
            target.button_widget.place(x=position[0],y=position[1])
        for c in range(len(self.curse)):
            target = self.curse[c]
            position = self.ui_position_calc(c, self.x_position, self.y_position, 'c', target.scale, curse_space)
            target.button_widget.place(x=position[0],y=position[1])

    def ui_position_calc(self, index, x_position, y_position, prefix, scale, curse_space):
        out_x_position = x_position 
        out_y_position = y_position
        match prefix:
            case 'p':
                out_x_position = x_position + int(0.5 * CardImageButton.button_width * scale[0] * index) #For each primary, set the x_pos to inital pos + (.75 * card_width * x_scale * index)
                out_y_position = y_position + int(0.25 * CardImageButton.button_height * scale[1] * index) #For each primary, set the y_pos to inital pos + (.25 * card_height * scale * index)
            case 's':
                out_x_position = x_position + int(0.5 * CardImageButton.button_width * scale[0] * index) + int(CardImageButton.button_width * scale[0]) #Same as primary, but x_pos += (card width * scale) (or 2 times card width if curse)
                out_y_position = y_position + int(0.25 * CardImageButton.button_height * scale[1] * index)
            case 'c':
                out_x_position = x_position + int(0.5 * CardImageButton.button_width * scale[0] * index) + int(CardImageButton.button_width * scale[0] * 0.5) #Same as primary, but x_pos += (card width * scale)
                out_y_position = y_position + int(0.25 * CardImageButton.button_height * scale[1] * index + (CardImageButton.button_height * 0.5 * scale[1]))
            case _:
                print("Error: Unhandled prefix passed to GameDraft.ui_position_calc()")
        return [out_x_position,out_y_position]

class CardImageButton:
    button_width = 189
    button_height = 270
    button_x_spacing = 10
    def __init__(self, canvas, x, y, prefix, rolled_game, scale=[1.0,1.0]):
        self.canvas=canvas
        self.scale=scale
        self.image = []
        self.rolled_game = rolled_game
        self.button_widget = tk.Button(canvas, image=None,width=int(CardImageButton.button_width*self.scale[0]), height=int(CardImageButton.button_height*self.scale[1]), highlightthickness=0)
        self.button_widget.bind("<Enter>",lambda event: self.raise_self())
        self.prefix = prefix
        self.roll_objective_from_game()
    
    def raise_self(self):
        Misc.tkraise(self.button_widget)
    
    def roll_objective_from_game(self):
        __location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))+'\\Resources'
        image_folder = os.path.join(__location__, self.rolled_game)

        _image = Image.open(self.random_image_path_from_folder(image_folder, self.prefix))
        _image = _image.resize((int(CardImageButton.button_width*self.scale[0]), int(CardImageButton.button_height*self.scale[1])))
        _photo = ImageTk.PhotoImage(_image)

        self.image.clear()
        self.image.append(_photo)
        # [Petra]: Having CardImageButton.image be an array that we reference the tail of is likely unneeded. But this code worked for me. ¯\_(ツ)_/¯
        self.button_widget.config(image=self.image[-1])

    def random_image_path_from_folder(self,image_folder, prefix):
        images = [f for f in os.listdir(image_folder) if f.startswith(prefix) and f.endswith(('.png', '.jpg', '.jpeg'))]
        if len(images) < 1:
            print(str("Error loading images at: + " + str(self.prefix) + " " + str(self.rolled_game)))
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
        
        self.adjectives = []
        self.nouns = []

        self.drafted_games = []
        self.bg = []
        self.bg_index = 0
        
        self.load_bgs()
        self.background_photo = self.bg[0]
        self.read_csv()
        self.load_images()
        self.create_widgets()
    
    def load_bgs(self):
        image_folder= os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))+'\\Resources\\bgs'
        images = [f for f in os.listdir(image_folder) if f.endswith(('.png', '.jpg', '.jpeg'))]
        for filename in images:
            image_path = os.path.join(image_folder, filename)
            image = Image.open(image_path)
            image = ImageTk.PhotoImage(image)
            self.bg.append(image)  # Store both image and filename
        if len(images) < 1:
            print(str("Error loading bg images or no images in bgs folder"))
    
    def cycle_bg(self):
        self.bg_index += 1
        if self.bg_index >= len(self.bg):
            self.bg_index = 0
        self.bg_label.config(image=self.bg[self.bg_index])
        

    def load_images(self):
        # Load images from the specified folder
        image_files = [f for f in os.listdir(self.image_folder) if f.endswith(('.png', '.jpg', '.jpeg'))]
        for filename in image_files:
            image_path = os.path.join(self.image_folder, filename)
            image = Image.open(image_path)
            image = image.resize((CardImageButton.button_width, CardImageButton.button_height))  # Resize the image
            self.images.append((image, filename))  # Store both image and filename

    def create_widgets(self):
        self.next_image = ImageTk.PhotoImage(Image.open("Resources/Buttons/next.png"))
        self.previous_image = ImageTk.PhotoImage(Image.open("Resources/Buttons/previous.png"))
        self.donedrafting_image = ImageTk.PhotoImage(Image.open("Resources/Buttons/done_drafting.png"))

        # Create a Label to display the background image
        self.bg_label = tk.Label(self.root, image=self.background_photo)
        self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)

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

        self.next_button = ttk.Button(self.root, image=self.next_image, command=self.next_page, style="Small.TButton")
        self.next_button.place(x=1500, y=950)

        self.prev_button = ttk.Button(self.root, image=self.previous_image, command=self.prev_page, style="Small.TButton")
        self.prev_button.place(x=220, y=950)

        self.done_button = ttk.Button(self.root, image=self.donedrafting_image, command=self.choose_number_of_drafts, style="Small.TButton")
        self.done_button.place(x=950, y=1000, anchor=tk.CENTER)
        
        self.cycle_bg_button = ttk.Button(self.root, text="Cycle Background", command=self.cycle_bg, style="Small.TButton")
        self.cycle_bg_button.place(x=650, y=1020, anchor=tk.CENTER)

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
            btn = tk.Button(self.canvas, image=photo, width=CardImageButton.button_width, height=CardImageButton.button_height)
                            #,command=lambda f=filename: self.add_to_clicked_images(f))  # Pass filename to lambda
            btn.image = photo
            btn.grid(row=(i - start_idx) // 8, column=(i - start_idx) % 8, padx=22, pady=10)
            btn.bind("<Button-1>", lambda event, f = filename: self.add_to_clicked_images(f)) #.bind inputs self, so we use lambda event to throw away that extra parameter
            btn.bind("<Button-2>", lambda event, f = filename: self.remove_from_clicked_images(f))
            btn.bind("<Button-3>", lambda event, f = filename: self.remove_from_clicked_images(f))

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

        self.done_button.place(x=950, y=1026, anchor=tk.CENTER)
        self.generate_selected_deck_images()
    
    def remove_from_clicked_images(self, filename):
        if filename in self.clicked_images:
            self.clicked_images[filename] -= 1
        else:
            self.clicked_images[filename] = 0        
        self.generate_selected_deck_images()

    def generate_selected_deck_images(self):
        for widget in self.clicked_frame.winfo_children():
            widget.destroy()
        for filename in self.clicked_images:
            if self.clicked_images[filename] > 0:
                i = 0
                while i < self.clicked_images[filename]:
                    clicked_image_path = os.path.join(self.image_folder, filename)
                    clicked_image = Image.open(clicked_image_path)
                    clicked_image = clicked_image.resize((CardImageButton.button_width // 4, CardImageButton.button_height // 4))
                    clicked_photo = ImageTk.PhotoImage(clicked_image)

                    clicked_label = tk.Label(self.clicked_frame, image=clicked_photo)
                    clicked_label.image = clicked_photo
                    clicked_label.pack(side=tk.LEFT)
                    i += 1

    def choose_number_of_drafts(self):
        self.clear_screen(0)

        self.one_image = ImageTk.PhotoImage(Image.open("Resources/Buttons/one.png"))
        self.three_image = ImageTk.PhotoImage(Image.open("Resources/Buttons/three.png"))
        self.five_image = ImageTk.PhotoImage(Image.open("Resources/Buttons/five.png"))

        # Create a label asking how many games to play
        self.title = tk.Label(self.canvas,text="How many games would you like to play?", font=("Helvetica",50))
        self.title.place(x=962, y=200, anchor=tk.CENTER)

        # Create buttons for 1, 3, and 5 games
        self.games_selection = tk.StringVar()  # Variable to store the selected number of games

        self.games_1_button = tk.Button(self.root, image=self.one_image, font=("Helvetica", 24), command=lambda: self.start_games(1))
        self.games_1_button.place(x=500, y=600, anchor=tk.CENTER)

        self.games_3_button = tk.Button(self.root, image=self.three_image, font=("Helvetica", 24), command=lambda: self.start_games(3))
        self.games_3_button.place(x=960, y=600, anchor=tk.CENTER)

        self.games_5_button = tk.Button(self.root, image=self.five_image, font=("Helvetica", 24), command=lambda: self.start_games(5))
        self.games_5_button.place(x=1420, y=600, anchor=tk.CENTER)
    
    def return_button(self):
        self.clear_screen(2)
        self.create_widgets()

    def clear_screen(self, prev_screen_index=0):
        self.canvas.destroy()
        self.clicked_frame.destroy()
        match prev_screen_index:
            case 0: #Image Selection Screem
                self.next_button.place_forget()
                self.prev_button.place_forget()
                self.done_button.place_forget()
            case 1: # Game Number Selection Screen5
                self.games_1_button.place_forget()
                self.games_3_button.place_forget()
                self.games_5_button.place_forget()
            case 2: # Draft Screen
                self.reroll_button.place_forget()
                self.back_button.place_forget()
                self.drafted_games.clear()
                self.clicked_images.clear()
                self.title_label.destroy()
                self.close_button.destroy()

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
    
    def read_csv(self):
        csv_file_path = 'word_bank.csv'
        delimiter = ','  # Change to the appropriate delimiter if necessary
        # Read the CSV file and split each line into values
        with open(csv_file_path, newline='') as csv_file:
            csv_reader = csv.DictReader(csv_file) #, delimiter=delimiter
            for row in csv_reader:
                self.adjectives.append(row['Adjectives'])
                self.nouns.append(row['Nouns'])
        # [Petra]: Debug print    
        #for i in range(len(self.adjectives)):
        #    print(""+str(self.adjectives[i])+" Pyramid of "+str(self.nouns[i]))
    
    def random_adjective(self):
        return self.adjectives[random.randrange(len(self.adjectives))]
    
    def random_noun(self):
        return self.nouns[random.randrange(len(self.nouns))]
    
    def reroll_all(self, num_games):
        self.reroll_button.place_forget()
        self.back_button.place_forget()
        self.dice_button.place_forget()
        self.title_label.destroy()
        self.close_button.destroy()
        self.start_games(num_games)
    
    def die_roll(self):
        self.dice_button.config(text=str(random.randrange(1,7)))

    def start_games(self, num_games):
        self.clear_screen(1)
        if self.games_selection:
            weighted_images = []
            while weighted_images.__len__() < num_games:
                for rolled_game, weight in self.clicked_images.items():
                    if weight > 0:
                        weighted_images.extend([rolled_game] * weight)

            selected_images = random.sample(weighted_images, num_games)

            # Create a Label to display the background image
            #self.title_label = tk.Label(self.root, text=""+str(self.random_adjective())+" Pyramid of "+str(self.random_noun()), font=("Helvetica",50), bg="black", fg="white")
            #self.title_label.place(x=900, y=80, anchor=tk.CENTER)
            
            adjective = self.random_adjective()
            noun = self.random_noun()
            text_r = ""+str(adjective)+ " Pyramid of "+str(noun)
            self.title_label = tk.Label(self.root, text=text_r, font=("Helvetica",50), wraplength=1920, fg="white", bg="black")
            self.title_label.pack(side="top", expand=False, fill="x")

            close_font = font.Font(family="Arial", size=16, weight="bold")  # Adjust font properties as needed
            self.close_button = tk.Label(self.root, text="X", font=close_font, bg="red", fg="white", cursor="hand2")
            self.close_button.place(x=1880, y=10)  # Adjust the coordinates as needed
            self.close_button.bind("<Button-1>", self.close_program)

            zoom = .80  # multiplier for image size by zooming -/+
            self.rerollbutton_image = Image.open("Resources/Buttons/reroll_games.png")
            self.rerollbutton_image = ImageTk.PhotoImage(self.rerollbutton_image.resize(tuple([int(zoom * x) for x in self.rerollbutton_image.size])))
            self.backbutton_image = Image.open("Resources/Buttons/back_button.png")
            self.backbutton_image = ImageTk.PhotoImage(self.backbutton_image.resize(tuple([int(zoom * x) for x in self.backbutton_image.size])))
            self.rolldiebutton_image = Image.open("Resources/Buttons/roll_d6.png")
            self.rolldiebutton_image = ImageTk.PhotoImage(self.rolldiebutton_image.resize(tuple([int(zoom * x) for x in self.rolldiebutton_image.size])))
            
            self.reroll_button = tk.Button(self.root, image=self.rerollbutton_image, font="Helvetica", bg="black", fg="white", cursor="hand2", command=lambda: self.reroll_all(num_games))
            self.reroll_button.place(x=800, y=1000)  # Adjust the coordinates as needed

            self.dice_button = tk.Button(self.root, image=self.rolldiebutton_image, font="Helvetica", bg="black", fg="white", cursor="hand2")
            self.dice_button.config(command=lambda:self.die_roll())
            self.dice_button.place(x=30, y=1000)  # Adjust the coordinates as neede

            self.back_button = tk.Button(self.root, image=self.backbutton_image, font="Helvetica", bg="black", fg="white", cursor="hand2", command=self.return_button)
            self.back_button.place(x=30, y=10)  # Adjust the coordinates as needed

            #IMPORTANT: These variables store the inital position and spacing between GameDrafts.
            x_position = 100
            y_position = 200
            game_draft_scale = [1.0, 1.0] #This SCALE is passed into the GameDraft.new() and affects ALL the cards in a drafted game.
            x_add = 650
            y_add = 370

            #IMPORTANT: Edit this function's hardcoded values to adjust UI for different numbers of games chosen.
            match num_games:
                case 1:
                    x_position = 550
                    y_position = 250
                    game_draft_scale = [2.0,2.0]
                case 3:
                    x_position = 233
                    y_position = 450
                    x_add = 515
                    game_draft_scale = [1.0,1.0]
                case 5:
                    x_position = 100
                    y_position = 300
                    x_add = 625
                    y_add = 300
                case _:
                    print("Error: Start games received an unexpected number of games")

            for rolled_game in selected_images:
                rolled_game_in = rolled_game.split('.')[0]
                self.drafted_games.append(GameDraft(self.canvas,rolled_game_in,x_position,y_position,game_draft_scale))

                x_position += x_add
                if(x_position > 1900 and y_position < 470): #This code is hardcoded, but it should only ever affect 5 draft anyways.
                    x_position = 100 + (1.5 * CardImageButton.button_width) + 33
                    y_position += y_add

        if num_games < 1:
            print("Please select the number of games before starting.")
        
        self.multiplayerbutton_image = Image.open("Resources/Buttons/multiplayer_rules.png")
        self.multiplayerbutton_image = ImageTk.PhotoImage(self.multiplayerbutton_image.resize(tuple([int(zoom * x) for x in self.multiplayerbutton_image.size])))
        self.coopbutton_image = Image.open("Resources/Buttons/coop_rules.png")
        self.coopbutton_image = ImageTk.PhotoImage(self.coopbutton_image.resize(tuple([int(zoom * x) for x in self.coopbutton_image.size])))
        

        self.multiplayer_button = tk.Button(self.root, image=self.multiplayerbutton_image, font="Helvetica", bg="black", fg="white", cursor="hand2", command=self.multiplayer_rules_button)
        self.multiplayer_button.place(x=1620, y=920)  # Adjust the coordinates as needed

        self.coop_button = tk.Button(self.root, image=self.coopbutton_image, font="Helvetica", bg="black", fg="white", cursor="hand2", command=self.coop_rules_button)
        self.coop_button.place(x=1620, y=1000)  # Adjust the coordinates as needed             

    def multiplayer_rules_button(self):
        
        file_path = json.load(open('output.json')) # dict
        t = ''

        for game in self.drafted_games:
            t += f"{game.rolled_game}\n\n{file_path[game.rolled_game]['multiplayer']}\n\n"

        self.multiplayer_rules = tk.Label(self.root, text=t, font=("Helvetica",24), wraplength=960, bg="white")
        self.multiplayer_rules.pack(side="left", expand=False, fill="x")
    def coop_rules_button(self):
        pass
    def close_program(self, event):
        self.root.destroy()

if __name__ == "__main__":
    __location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__))) + "\\Resources"
    image_folder_path = os.path.join(__location__, 'Card Backs App')  # Replace with the actual folder path containing your images

    root = tk.Tk()
    app = ImageGalleryApp(root, image_folder_path)

    root.attributes('-fullscreen', True)
    root.mainloop()
