from ursina import *
from world import World
from player import Player
from mob import ZombieSpawner
from config import WIDTH
from scene import Scene
from menu import Menu
from save_system import save_game, load_game

# --- Setup App ---
app = Ursina()
window.color = color.cyan
window.borderless = False
window.title = "Minecraft 2D - Zombie AI"

# --- Setup Camera ---
camera.orthographic = True
camera.fov = 20

# Game state
game_world = None
player = None
mouse_catcher = None
game_over_ui = None
pause_ui = None
menu = None # Inisialisasi variabel menu global
current_world_name = None
current_world_type = None
is_paused = False
zombie_spawner = None

center_x = int(WIDTH / 2)
spawn_y = 40

# --- PAUSE MENU UI ---
class PauseMenu(Entity):
    def __init__(self, on_resume, on_save_exit):
        super().__init__(parent=camera.ui, enabled=False)
        self.on_resume = on_resume
        self.on_save_exit = on_save_exit
        
        self.bg = Entity(parent=self, model='quad', scale=(2,2), color=color.rgba(0,0,0,180), z=1)
        self.title = Text(parent=self, text="PAUSED", origin=(0,0), y=0.2, scale=2)
        
        self.btn_resume = Button(parent=self, text="Resume", y=0.05, scale=(0.3, 0.08), color=color.azure, text_color=color.black, on_click=self.resume)
        self.btn_save = Button(parent=self, text="Save & Exit", y=-0.05, scale=(0.3, 0.08), color=color.green, text_color=color.black, on_click=self.save_exit)
        
        # Petunjuk tombol
        self.hint = Text(parent=self, text="Press L to Resume", origin=(0,0), y=-0.2, scale=1, color=color.gray)

    def resume(self):
        self.on_resume()
        
    def save_exit(self):
        self.on_save_exit()

    def show(self):
        self.enabled = True
        
    def hide(self):
        self.enabled = False

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
    global game_world, player, mouse_catcher, game_over_ui, pause_ui, zombie_spawner
    camera.scripts.clear()

    if zombie_spawner:
        zombie_spawner.cleanup() 
        destroy(zombie_spawner)
        zombie_spawner = None

    for ent in (player, mouse_catcher, game_world, game_over_ui, pause_ui):
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

def start_new_game(name, world_type):
    global current_world_name
    current_world_name = name
    launch_game_environment(world_type=world_type, save_data=None)

def load_saved_game(name):
    global current_world_name
    current_world_name = name
    
    data = load_game(name)
    if data:
        launch_game_environment(world_type=data['world_type'], save_data=data)
    else:
        print("Error loading game")
        # Jika load gagal, kembali ke menu (menu harus dibuat ulang karena sudah didestroy saat loading)
        back_to_menu()

def launch_game_environment(world_type, save_data=None):
    global game_world, player, mouse_catcher, game_over_ui, pause_ui, is_paused, menu, zombie_spawner
    
    # --- PERBAIKAN 1: HAPUS MENU LOADING ---
    # Kita harus menghancurkan objek menu (yang berisi teks "Generating World...")
    # sebelum memulai game environment.
    if menu:
        try:
            menu.destroy()
        except:
            pass
        menu = None

    cleanup_game()
    window.color = color.cyan
    is_paused = False

    # 1. World (Generate or Load)
    game_world = World(world_type=world_type, save_data=save_data)
    
    # Render manual awal
    game_world.update()
 
    if save_data:
        spawn_pos = save_data.get('player_pos', (center_x, 40))
    else:
        # Cari permukaan aman
        if center_x < len(game_world.surface_heights):
            spawn_y = game_world.surface_heights[center_x] + 4
        spawn_pos = (center_x, spawn_y)

    # 3. UI
    game_over_ui = GameOverOverlay(on_respawn=restart_game, on_exit=back_to_menu)
    pause_ui = PauseMenu(on_resume=resume_game, on_save_exit=save_and_exit_game)

    # 4. Player Entity
    player = Player(
        world_instance=game_world, 
        position=spawn_pos,
        on_death=lambda: game_over_ui.show()
    )
    # --- SPAWN ZOMBIE ---
    zombie_spawner = ZombieSpawner(game_world, player)

    camera.scripts.clear()
    camera.add_script(SmoothFollow(target=player, offset=[0, 1, -30], speed=5))

    camera.x = player.x
    camera.y = player.y + 1
    
def update():
    if zombie_spawner: 
        zombie_spawner.update()


# --- Mouse Catcher ---
mouse_catcher = Entity(
    model='quad', 
    scale=999, 
    color=color.clear, 
    z=2, 
    collider='box'
)

def exit_app():
    application.quit()

def restart_game():
    if player:
        player.respawn()

def back_to_menu():
    global menu
    cleanup_game()
    # Pastikan menu lama bersih jika ada
    if menu:
        try:
            menu.destroy()
        except:
            pass
    menu = Menu(on_start_new_callback=start_new_game, on_load_callback=load_saved_game, on_exit_callback=exit_app)

# --- PAUSE SYSTEM ---
def input(key):
    global is_paused
    
    # Jika game sedang berjalan (player ada) dan menu TIDAK ada
    if player and not menu:
        # --- PERBAIKAN 2: GANTI TOMBOL KE 'L' ---
        if key == 'l':
            if not is_paused:
                pause_game()
            else:
                resume_game()

def pause_game():
    global is_paused
    is_paused = True
    application.pause() # Stop update ursina entities
    if pause_ui:
        pause_ui.show()
    # Mouse harus terlihat saat pause
    mouse.visible = True
    mouse.locked = False

def resume_game():
    global is_paused
    is_paused = False
    if pause_ui:
        pause_ui.hide()
    application.resume()
    # Kembalikan state mouse
    mouse.visible = True 
    mouse.locked = False

def save_and_exit_game():
    global current_world_name
    
    print("Saving...")
    if game_world and player and current_world_name:
        w_data = game_world.get_save_data()
        p_data = {"position": (player.x, player.y)}
        save_game(current_world_name, w_data, p_data)
    
    resume_game() # Unpause dulu sebelum destroy
    back_to_menu()

scene = Scene()

# --- Initialize Menu ---
if __name__ == '__main__':
    menu = Menu(on_start_new_callback=start_new_game, on_load_callback=load_saved_game, on_exit_callback=exit_app)
    app.run()