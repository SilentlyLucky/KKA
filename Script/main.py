from ursina import *
from world import World
from player import Player
from mob import ZombieSpawner, ChickenSpawner, initialize_ai_executor, shutdown_ai_executor # Import baru
from config import *
from scene import Scene
from menu import *
from save_system import save_game, load_game

# --- Global Variables (Initialized to None) ---
app = None
game_world = None
player = None
mouse_catcher = None
game_over_ui = None
pause_ui = None
menu = None
game_background = None 
zombie_spawner = None
chicken_spawner = None
current_world_name = None
current_world_type = None
current_difficulty_state = "EASY"
is_paused = False

class GameInputController(Entity):
    def __init__(self):
        super().__init__(ignore_paused=True)

    def input(self, key):
        global is_paused
        if player and not menu:
            if key == 'escape':
                if not is_paused:
                    pause_game()
                else:
                    resume_game()

# --- GAME OVER UI ---
class GameOverOverlay(Entity):
    def __init__(self, on_respawn, on_exit):
        super().__init__(parent=camera.ui, enabled=False)
        self.on_respawn = on_respawn
        self.on_exit = on_exit

        self.bg = Entity(parent=self, model='quad', color=color.rgba(0, 0, 0, 160), scale=(2, 2), z=1)
        self.title = Text(parent=self, text="GAME OVER", origin=(0, 0), y=0.2, scale=2, color=color.white, outline=(0.3, color.black))
        self.respawn_btn = Button(parent=self, text="Respawn", color=color.azure, text_color=color.black, scale=(0.3, 0.1), y=0.0, on_click=self.handle_respawn)
        self.exit_btn = Button(parent=self, text="Exit", color=color.red, text_color=color.black, scale=(0.3, 0.1), y=-0.15, on_click=self.handle_exit)

    def handle_respawn(self):
        self.enabled = False
        self.on_respawn()

    def handle_exit(self):
        self.enabled = False
        self.on_exit()

    def show(self):
        self.enabled = True

def cleanup_game():
    global game_world, player, mouse_catcher, game_over_ui, pause_ui, zombie_spawner, chicken_spawner, game_background
    camera.scripts.clear()
    
    # Hapus semua entity game
    entities_to_remove = [player, mouse_catcher, game_world, game_over_ui, pause_ui, game_background]
    
    for ent in entities_to_remove:
        if ent:
            try:
                destroy(ent)
            except:
                pass
                
    game_world = None
    player = None
    mouse_catcher = None
    game_over_ui = None
    pause_ui = None
    zombie_spawner = None
    chicken_spawner = None
    game_background = None

def start_new_game(name, world_type, difficulty="EASY"):
    global current_world_name, current_difficulty_state
    current_world_name = name
    current_difficulty_state = difficulty
    set_difficulty(difficulty)
    print(f"[DEBUG] Starting new game: {name} [{current_difficulty_state}]")
    launch_game_environment(world_type=world_type, save_data=None)

def load_saved_game(name):
    global current_world_name, current_difficulty_state
    current_world_name = name
    
    data = load_game(name)
    if data:
        loaded_diff = data.get('difficulty', 'EASY')
        current_difficulty_state = loaded_diff
        set_difficulty(loaded_diff)
        print(f"[DEBUG] Loading save: {name}")
        launch_game_environment(world_type=data['world_type'], save_data=data)
    else:
        print("Error loading game")
        back_to_menu()

def launch_game_environment(world_type, save_data=None):
    global game_world, player, mouse_catcher, game_over_ui, pause_ui, is_paused, menu, zombie_spawner, game_controller, chicken_spawner, game_background
    
    if menu:
        try:
            menu.destroy()
        except:
            pass
        menu = None

    cleanup_game()
    window.color = color.cyan
    is_paused = False
    
    # MATIKAN VSYNC untuk FPS maksimal (opsional, kadang bikin tearing tapi FPS naik)
    window.vsync = False 

    # 1. Setup Background (Parallax)
    game_background = Scene()

    # 2. Setup World
    game_world = World(world_type=world_type, save_data=save_data)
    game_world.update()

    center_x = int(WIDTH / 2)

    if save_data:
        spawn_pos = save_data.get('player_pos', (center_x, 40))
        inv_data = save_data.get('inventory', None)
        saved_spawn_point = save_data.get('spawn_point', None)
    else:
        # NEW GAME: Find safe spawn height
        if center_x < len(game_world.surface_heights):
            spawn_y = game_world.surface_heights[center_x]  # 4 blocks above surface
        else:
            spawn_y = 40  # Fallback
        
        spawn_pos = (center_x, spawn_y)
        inv_data = None
        saved_spawn_point = None
        
        print(f"New game spawn position: {spawn_pos}")

    game_over_ui = GameOverOverlay(on_respawn=restart_game, on_exit=back_to_menu)
    pause_ui = PauseMenu(on_resume=resume_game, on_save_exit=save_and_exit_game)

    game_controller = GameInputController()
    
    player = Player(
        world_instance=game_world, 
        position=spawn_pos,
        inventory_data=inv_data,
        saved_spawn_point=saved_spawn_point
    )

    zombie_spawner = ZombieSpawner(game_world, player)
    chicken_spawner = ChickenSpawner(game_world, player)

    # 3. Setup Mouse Catcher
    mouse_catcher = Entity(
        model='quad', 
        scale=999, 
        color=color.clear, 
        z=1000, 
        collider='box'
    )

    camera.scripts.clear()
    camera.add_script(SmoothFollow(target=player, offset=[0, 1, -30], speed=5))

    camera.x = player.x
    camera.y = player.y + 1

    mouse.locked = False
    mouse.visible = True
    
def update():
    if zombie_spawner: 
        zombie_spawner.update()
    if chicken_spawner:
        chicken_spawner.update()

def exit_app():
    # Bersihkan pool process sebelum keluar
    shutdown_ai_executor()
    application.quit()

def restart_game():
    if player:
        player.respawn()

def back_to_menu():
    global menu
    cleanup_game()
    if menu:
        try:
            menu.destroy()
        except:
            pass
    menu = Menu(on_start_new_callback=start_new_game, on_load_callback=load_saved_game, on_exit_callback=exit_app)
    mouse.locked = False
    mouse.visible = True

def pause_game():
    global is_paused
    is_paused = True
    application.pause()
    if pause_ui:
        pause_ui.show()
    mouse.visible = True
    mouse.locked = False

def resume_game():
    global is_paused
    is_paused = False
    if pause_ui:
        pause_ui.hide()
    application.resume()
    mouse.visible = True 
    mouse.locked = False

def save_and_exit_game():
    global current_world_name, current_difficulty_state
    print(f"Saving... Current Global Difficulty is: {current_difficulty_state}")
    if game_world and player and current_world_name:
        w_data = game_world.get_save_data()
        
        p_data = {
            "position": (player.x, player.y),
            "spawn_point": (player.spawn_x, player.spawn_y) 
        }
        i_data = player.inventory_system.get_save_data()
        
        save_game(current_world_name, w_data, p_data, i_data, difficulty=current_difficulty_state)
        exit_app()
        return
    resume_game() 
    back_to_menu()

# --- Initialize Menu ---
if __name__ == '__main__':
    app = Ursina()
    
    # Inisialisasi Multiprocessing Pool untuk AI
    initialize_ai_executor()
    
    window.color = color.cyan
    window.borderless = False
    window.title = "Minecraft 2D - Zombie AI"
    
    camera.orthographic = True
    camera.fov = 20
    
    menu = Menu(on_start_new_callback=start_new_game, on_load_callback=load_saved_game, on_exit_callback=exit_app)
    
    app.run()