import tkinter as tk
from tkinter.simpledialog import askstring
import random
import os

# Initialize global variables
score = 0
car_speed = 20
obstacle_speed = 6
is_paused = False
player_name =None
game_loaded = False

# Function to move the car to the left
def move_left(event):
    if not is_paused:
        current_x = canvas.coords(car)[0]
        if current_x - car_speed > 0:
            canvas.move(car, -car_speed, 0)

# Function to move the car to the right
def move_right(event):
    if not is_paused:
        current_x = canvas.coords(car)[0]
        if current_x + car_speed < canvas.winfo_width():
            canvas.move(car, car_speed, 0)

# Function to toggle pause
def toggle_pause(event):
    global is_paused
    is_paused = not is_paused
    if is_paused:
        canvas.create_text(300, 300, text="Paused", font=("Helvetica", 36), tags="pause_text", fill="white")
    else:
        canvas.delete("pause_text")

# Function to update the game state
def update():
    global score, obstacle_speed, game_loop_id, dashed_line, game_loaded
    
    if not is_paused:
        move_obstacles()  
        check_collision()
        score += 1
        if score == 200 or score == 450:
            canvas.itemconfig(score_text, font=("Helvetica", 24), fill="gold")
            root.after(5000, reset_text_format)
        else:
            canvas.itemconfig(score_text, font=("Helvetica", 16), fill="white")

        canvas.itemconfig(score_text, text=f"Score: {score}")
        # Adjust obstacle speed based on the score
        if score > 450:
            obstacle_speed = 17  
        elif score > 200:
            obstacle_speed = 12

    
    game_loop_id = root.after(100, update)

def reset_text_format():
    canvas.itemconfig(score_text, font=("Helvetica", 16), fill="white")

def handle_collision():
    global player_name
    player_name_window =tk.Toplevel(root)
    player_name_window.title("Enter Your Name")

    name_label = tk.Label(player_name_window, text = "Enter your name: ")
    name_label.pack()

    name_entry = tk.Entry(player_name_window)
    name_entry.pack()

    def on_enter():
        global player_name
        player_name = name_entry.get()
        try:
          player_name_window.destroy()
        except tk.TclError as e:
          print(f"Error destroying window: {e}")
        update_leaderboard(player_name, score)
        reset_game()

    enter_button = tk.Button(player_name_window, text ="Enter", command=on_enter)
    enter_button.pack()
    # Pause the game until the player enters their name
    root.after_cancel(game_loop_id)

def open_leaderboard():
    global player_name
    leaderboard_window = tk.Toplevel(root)
    leaderboard_window.title("LeaderBoard")
    #read scores from file if exists
    try:
        with open("leaderboard.txt", "r") as file:
            leaderboard_data = [entry.strip() for entry in file.readlines()]
    except FileNotFoundError:
        leaderboard_data = []
  
    leaderboard_data.sort(key=lambda x: int(x.split(',')[1]) if x.split(',')[1].isdigit() else 0, reverse=True)

    # Display scores in the leaderboard window
    for i, entry in enumerate(leaderboard_data):
        label = tk.Label(leaderboard_window, text=f"{i + 1}. {entry}", font=("Helvetica", 20))
        label.pack()


def update_leaderboard(name, score):
    global player_name
    # Read existing scores from a file (if it exists)
    try:
        with open("leaderboard.txt", "r") as file:
            leaderboard_data = [entry.strip() for entry in file.readlines()]
    except FileNotFoundError:
        leaderboard_data = []

     # Add the current score and player name to the leaderboard
    leaderboard_data.append(f"{name}, {score}")
    # Sort the scores in descending order
    leaderboard_data.sort(key=lambda x: int(x.split(',')[1]) if x.split(',')[1].isdigit() else 0, reverse=True)
    leaderboard_data = leaderboard_data[:5]

    # Write the updated leaderboard back to the file
    with open("leaderboard.txt", "w") as file:
        for entry in leaderboard_data:
            file.write(f"{entry}\n")

def on_enter_button_click():
    global player_name, is_paused, game_loaded
    player_name = name_entry.get()
    is_paused = False
    entry_window.destroy()

    if not game_loaded:
        # If it's a new game, reset and start the game
        reset_game()
        game_loaded = True


def delete_leaderboard():
    # Delete the leaderboard file
    try:
        os.remove("leaderboard.txt")
        print("Leaderboard cleared!")
    except FileNotFoundError:
        print("Leaderboard file not found.")

# Function to move obstacles and spawn new ones
def move_obstacles():
    for obstacle in obstacles.copy():
        canvas.move(obstacle, 0, obstacle_speed)
        if canvas.coords(obstacle)[1] > 600:
            canvas.delete(obstacle)
            obstacles.remove(obstacle)
            spawn_obstacle()
            

# Function to check collision between the car and obstacles
def check_collision():
    global score, is_paused
    car_bbox = canvas.bbox(car)
    for obstacle in obstacles.copy():
        obstacle_coords = canvas.coords(obstacle)
        if (
            car_bbox is not None and len(car_bbox) == 4 and
            len(obstacle_coords) == 4 and
            car_bbox[0] < obstacle_coords[2]
            and car_bbox[2] > obstacle_coords[0]
            and car_bbox[1] < obstacle_coords[3]
            and car_bbox[3] > obstacle_coords[1]
        ):
            is_paused =True
            update_leaderboard(player_name, score)
            show_entry_window()
            reset_game()

#Opens window for namae and enter button
def show_entry_window():
    global entry_window, name_entry
    entry_window = tk.Toplevel(root)
    entry_window.title("Enter Your Name")

    label = tk.Label(entry_window, text="Enter your name:")
    label.pack()

    name_entry = tk.Entry(entry_window)
    name_entry.pack()

    enter_button = tk.Button(entry_window, text="Enter", command=on_enter_button_click)
    enter_button.pack()

# Function to spawn a new obstacle
def spawn_obstacle():
    num_obstacles = random.randint(1, 2)
    min_distance = 100
    for _ in range(num_obstacles):
        x = random.randint(0, 500)
        y = 0
        
        # Ensure the new obstacle does not overlap with existing obstacles
        while any(
            obstacle
            for obstacle in obstacles
            if (
                obstacle is not None
                and canvas.coords(obstacle) is not None
                and len(canvas.coords(obstacle)) == 4
                and abs(canvas.coords(obstacle)[0] - x) < min_distance
            )
        ) or y < 0:
            x = random.randint(0, 500)
            y = random.randint(-200, 0)

        obstacle = canvas.create_rectangle(x, y, x + 50, y + 20, fill="red")
        obstacles.append(obstacle)

# Function to end the game
def end_game():
    global is_paused, obstacle_speed, score
    canvas.create_text(300, 300, text=f"Game Over\nScore: {score}", font=("Helvetica", 24),fill="white")
    is_paused = True
    obstacle_speed = 6
    update_leaderboard(player_name, score)
    root.bind("<n>", restart_game)
    canvas.after_cancel(game_loop_id)
    reset_game()

def restart_game(event):
    global is_paused, score, obstacle_speed, game_loop_id, game_loaded
    is_paused = False
   
    score =0
    game_loaded =False
    canvas.after_cancel(game_loop_id)
    reset_game()

# Function to reset the game
def reset_game():
    global score, score_text, car, resized_car_image, obstacle_speed, game_loop_id, dashed_line
    
    canvas.delete("all")
    obstacles.clear()
    score = 0
    score_text = None
    obstacle_speed = 6
    draw_score()
    spawn_obstacle()
    
    # Recreate the dashed line and update the reference
    
    car_image = tk.PhotoImage(file="YELLOWcar2.png")
    resized_car_image = car_image.subsample(8, 8)
    car = canvas.create_image(400, 500, anchor="center", image=resized_car_image)

    canvas.after_cancel(game_loop_id)
    game_loop_id = root.after(100, update)

# Function to draw the score on the canvas
def draw_score():
    global score_text
    score_text = canvas.create_text(500, 50, text=f"Score: {score}", font=("Helvetica", 16), fill="white")

def save_game():
    global score, player_name, obstacle_speed
    with open("save_game.txt", "w") as file:
        file.write(f"{player_name},{score},{obstacle_speed}")
        print("Game Saved")

def load_game():
    global score, player_name, obstacle_speed
    try:
        with open ("save_game.txt", "r") as file:
            data = file.read().split(',')
            player_name, score, obstacle_speed = data[0], int(data[1]), int(data[2])
            print("Game Loaded...")
    except FileNotFoundError:
        print("Save file not found. Starting a new game.")
        player_name = None
        score = 0
        obstacle_speed = 6
         # Create an empty save file
        with open("save_game.txt", "w") as file:
            file.write(f"{player_name},{score},{obstacle_speed}")


def start_new_game():
    global is_paused, score, obstacle_speed, game_loaded
    is_paused = False
    score = 0
    game_loaded = False
    reset_game()

def load_game_window():
    load_window = tk.Toplevel(root)
    load_window.title("Load Game")

    new_game_button = tk.Button(load_window, text="Start New Game", command=start_new_game)
    new_game_button.pack()

    load_button = tk.Button(load_window, text="Load Saved Game", command=load_game)
    load_button.pack()

# Initialize the main window
root = tk.Tk()
root.title("Car Dodging Game")
root.geometry("600x600")
root.configure(bg="Green")

# Create the canvas
canvas = tk.Canvas(root, bg="black", width=600, height=600, relief=tk.FLAT)
canvas.pack()

# Load car image
car_image = tk.PhotoImage(file="YELLOWcar2.png")
resized_car_image = car_image.subsample(8, 8)
car = canvas.create_image(400, 500, anchor="center", image=resized_car_image)

# Initialize obstacles list
obstacles = []

# Bind keys to functions
root.bind("<Left>", move_left)
root.bind("<Right>", move_right)
root.bind("<space>", toggle_pause)
root.bind("<n>", restart_game)
root.bind("<d>", lambda event :delete_leaderboard())
root.bind("<s>", lambda event: save_game())  # Press 's' to save the game
root.bind("<l>", lambda event: load_game_window())  # Press 'l' to load the saved game

# Draw initial score and spawn the first obstacle
draw_score()
spawn_obstacle()
# Button to open the leaderboard window
leaderboard_button = tk.Button(root, text="Leaderboard", command=open_leaderboard, width=20, height=2)
leaderboard_button.pack()

# Start the game loop
update()

root.mainloop()

