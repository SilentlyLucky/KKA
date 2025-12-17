from ursina import *
from ursina.prefabs.input_field import InputField
from save_system import *

class Menu:
    def __init__(self, on_start_new_callback, on_load_callback, on_exit_callback):
        self.on_start_new = on_start_new_callback
        self.on_load = on_load_callback
        self.on_exit = on_exit_callback
        
        window.color = color.cyan
        self.entities = [] 
        self.input_field = None # Simpan referensi input field

        self.show_main_menu()
    
    def clear_menu(self):
        for e in self.entities:
            try:
                destroy(e)
            except:
                pass
        self.entities = []
        self.input_field = None

    def show_main_menu(self):
        self.clear_menu()
        title = Text(text="MINERIA", origin=(0, 0), scale=3, y=0.3, color=color.white, outline=(0.3, color.black))
        self.entities.append(title)
        
        btn_new = Button(text="Create New World", color=color.green, scale=(0.4, 0.08), y=0.05, text_color=color.black, on_click=self.show_name_input)
        self.entities.append(btn_new)
        
        btn_load = Button(text="Load World", color=color.brown, scale=(0.4, 0.08), y=-0.05, text_color=color.white, on_click=self.show_load_screen)
        self.entities.append(btn_load)
        
        btn_exit = Button(text="Exit", color=color.red, scale=(0.4, 0.08), y=-0.15, text_color=color.black, on_click=self.exit_app)
        self.entities.append(btn_exit)

    # --- NEW WORLD FLOW ---
    def show_name_input(self):
        self.clear_menu()
        
        title = Text(
            text="NAME YOUR WORLD", origin=(0, 0), scale=2, y=0.3,
            color=color.white, outline=(0.3, color.black)
        )
        self.entities.append(title)
        
        self.input_field = InputField(y=0.1, scale=(0.5, 0.08))
        self.entities.append(self.input_field)
        
        btn_next = Button(
            text="Next", color=color.azure, scale=(0.3, 0.08), y=-0.1,
            text_color=color.black, on_click=self.validate_name_and_next
        )
        self.entities.append(btn_next)
        
        btn_back = Button(
            text="Back", color=color.gray, scale=(0.3, 0.08), y=-0.2,
            text_color=color.black, on_click=self.show_main_menu
        )
        self.entities.append(btn_back)

    def validate_name_and_next(self):
        world_name = self.input_field.text
        if not world_name or world_name.strip() == "":
            print("Please enter a name")
            return
        self.show_difficulty_selection(world_name)
        
    def show_difficulty_selection(self, world_name):
        self.clear_menu()
        title = Text(text=f"DIFFICULTY: {world_name}", origin=(0, 0), scale=2, y=0.3, color=color.white, outline=(0.3, color.black))
        self.entities.append(title)
        
        btn_easy = Button(text="EASY\n(Weak Mobs)", color=color.green, scale=(0.4, 0.1), y=0.1, text_color=color.black, on_click=lambda: self.show_type_selection(world_name, "EASY"))
        self.entities.append(btn_easy)
        
        btn_hard = Button(text="HARD\n(Strong Mobs)", color=color.red, scale=(0.4, 0.1), y=-0.05, text_color=color.white, on_click=lambda: self.show_type_selection(world_name, "HARD"))
        self.entities.append(btn_hard)
        
        btn_back = Button(text="Back", color=color.gray, scale=(0.3, 0.08), y=-0.2, text_color=color.black, on_click=self.show_name_input)
        self.entities.append(btn_back)

    def show_type_selection(self, world_name):
        self.clear_menu()
        
        title = Text(
            text=f"SELECT BIOME FOR: {world_name}", origin=(0, 0), scale=2, y=0.3,
            color=color.white, outline=(0.3, color.black)
        )
        self.entities.append(title)
        
        btn_plains = Button(
            text="Plains", color=color.green, scale=(0.3, 0.08), y=0.1,
            text_color=color.black, 
            on_click=lambda: self.trigger_start_new(world_name, "plains")
        )
        self.entities.append(btn_plains)
        
        btn_desert = Button(
            text="Desert", color=color.yellow, scale=(0.3, 0.08), y=0.0,
            text_color=color.black, 
            on_click=lambda: self.trigger_start_new(world_name, "sand")
        )
        self.entities.append(btn_desert)
        
        btn_back = Button(
            text="Back", color=color.gray, scale=(0.3, 0.08), y=-0.15,
            text_color=color.black, on_click=self.show_name_input
        )
        self.entities.append(btn_back)

    # --- LOAD WORLD FLOW ---
    def show_load_screen(self):
        self.clear_menu()
        
        title = Text(
            text="SELECT WORLD", origin=(0, 0), scale=2, y=0.35,
            color=color.white, outline=(0.3, color.black)
        )
        self.entities.append(title)
        
        saved_worlds = get_saved_worlds()
        
        start_y = 0.2
        
        if not saved_worlds:
            t = Text(text="No saved worlds found.", origin=(0,0), y=0.1, color=color.black)
            self.entities.append(t)
        else:
            # Tampilkan list world (Max 5 for simplicity)
            for i, w_name in enumerate(saved_worlds[:5]):
                y_pos = start_y - (i * 0.1)
                btn = Button(
                    text=w_name, color=color.orange, scale=(0.5, 0.08), y=y_pos,
                    text_color=color.black,
                    # Klik world sekarang membuka opsi, bukan langsung main
                    on_click=lambda n=w_name: self.show_world_options(n)
                )
                self.entities.append(btn)
        
        btn_back = Button(
            text="Back to Main Menu", color=color.gray, scale=(0.4, 0.08), y=-0.35,
            text_color=color.black, on_click=self.show_main_menu
        )
        self.entities.append(btn_back)

    # --- SELECTED WORLD MENU (Play/Edit/Back) ---
    def show_world_options(self, world_name):
        self.clear_menu()
        
        title = Text(
            text=f"WORLD: {world_name}", origin=(0, 0), scale=2, y=0.3,
            color=color.white, outline=(0.3, color.black)
        )
        self.entities.append(title)
        
        # 1. Play
        btn_play = Button(
            text="Play", color=color.green, scale=(0.4, 0.08), y=0.1,
            text_color=color.black, 
            on_click=lambda: self.trigger_load(world_name)
        )
        self.entities.append(btn_play)

        # 2. Edit
        btn_edit = Button(
            text="Edit World", color=color.azure, scale=(0.4, 0.08), y=0.0,
            text_color=color.black, 
            on_click=lambda: self.show_edit_options(world_name)
        )
        self.entities.append(btn_edit)

        # 3. Back
        btn_back = Button(
            text="Back", color=color.gray, scale=(0.4, 0.08), y=-0.1,
            text_color=color.black, 
            on_click=self.show_load_screen
        )
        self.entities.append(btn_back)

    # --- EDIT WORLD MENU (Rename/Delete) ---
    def show_edit_options(self, world_name):
        self.clear_menu()
        title = Text(text=f"EDIT: {world_name}", origin=(0, 0), scale=2, y=0.35, color=color.white, outline=(0.3, color.black))
        self.entities.append(title)
        
        # 1. Rename
        btn_rename = Button(text="Rename", color=color.orange, scale=(0.4, 0.08), y=0.2, text_color=color.black, on_click=lambda: self.show_rename_ui(world_name))
        self.entities.append(btn_rename)

        # 2. Change Difficulty (NEW)
        btn_diff = Button(text="Change Difficulty", color=color.yellow, scale=(0.4, 0.08), y=0.1, text_color=color.black, on_click=lambda: self.show_change_difficulty_ui(world_name))
        self.entities.append(btn_diff)

        # 3. Delete
        btn_delete = Button(text="Delete World", color=color.red, scale=(0.4, 0.08), y=0.0, text_color=color.white, on_click=lambda: self.show_delete_confirmation(world_name))
        self.entities.append(btn_delete)

        btn_back = Button(text="Back", color=color.gray, scale=(0.4, 0.08), y=-0.1, text_color=color.black, on_click=lambda: self.show_world_options(world_name))
        self.entities.append(btn_back)
        
    def show_change_difficulty_ui(self, world_name):
        self.clear_menu()
        title = Text(text=f"DIFFICULTY: {world_name}", origin=(0, 0), scale=2, y=0.3, color=color.white, outline=(0.3, color.black))
        self.entities.append(title)
        
        btn_easy = Button(text="Set to EASY", color=color.green, scale=(0.4, 0.1), y=0.1, text_color=color.black, on_click=lambda: self.perform_difficulty_change(world_name, "EASY"))
        self.entities.append(btn_easy)
        
        btn_hard = Button(text="Set to HARD", color=color.red, scale=(0.4, 0.1), y=-0.05, text_color=color.white, on_click=lambda: self.perform_difficulty_change(world_name, "HARD"))
        self.entities.append(btn_hard)
        
        btn_back = Button(text="Back", color=color.gray, scale=(0.3, 0.08), y=-0.2, text_color=color.black, on_click=lambda: self.show_edit_options(world_name))
        self.entities.append(btn_back)
        
    def perform_difficulty_change(self, world_name, new_diff):
        success = update_world_difficulty(world_name, new_diff)
        if success:
            print(f"Difficulty changed to {new_diff}")
            self.show_edit_options(world_name)
        else:
            print("Failed to change difficulty")

    # --- RENAME UI ---
    def show_rename_ui(self, old_name):
        self.clear_menu()
        
        title = Text(
            text=f"RENAME: {old_name}", origin=(0, 0), scale=2, y=0.3,
            color=color.white, outline=(0.3, color.black)
        )
        self.entities.append(title)
        
        self.input_field = InputField(default_value=old_name, y=0.1, scale=(0.5, 0.08))
        self.entities.append(self.input_field)
        
        # Confirm Rename
        btn_ok = Button(
            text="Confirm Rename", color=color.green, scale=(0.3, 0.08), y=-0.05,
            text_color=color.black, 
            on_click=lambda: self.perform_rename(old_name)
        )
        self.entities.append(btn_ok)
        
        # Cancel
        btn_cancel = Button(
            text="Cancel", color=color.red, scale=(0.3, 0.08), y=-0.15,
            text_color=color.white, 
            on_click=lambda: self.show_edit_options(old_name)
        )
        self.entities.append(btn_cancel)

    def perform_rename(self, old_name):
        new_name = self.input_field.text
        if new_name and new_name.strip() != "":
            success = rename_world(old_name, new_name)
            if success:
                self.show_world_options(new_name)
            else:
                print("Rename failed")
        else:
            print("Invalid Name")

    # --- DELETE CONFIRMATION ---
    def show_delete_confirmation(self, world_name):
        self.clear_menu()
        
        title = Text(
            text=f"DELETE {world_name}?", origin=(0, 0), scale=2, y=0.3,
            color=color.red, outline=(0.3, color.black)
        )
        self.entities.append(title)
        
        warn = Text(
            text="This cannot be undone!", origin=(0, 0), scale=1.5, y=0.2,
            color=color.orange
        )
        self.entities.append(warn)
        
        # Yes (Delete)
        btn_yes = Button(
            text="Yes, Delete", color=color.red, scale=(0.3, 0.08), y=0.0,
            text_color=color.white, 
            on_click=lambda: self.perform_delete(world_name)
        )
        self.entities.append(btn_yes)
        
        # No (Cancel)
        btn_no = Button(
            text="No, Keep It", color=color.green, scale=(0.3, 0.08), y=-0.1,
            text_color=color.black, 
            on_click=lambda: self.show_edit_options(world_name)
        )
        self.entities.append(btn_no)

    def perform_delete(self, world_name):
        success = delete_world(world_name)
        self.show_load_screen() # Kembali ke list world

    # --- LAUNCHERS ---
    def trigger_start_new(self, name, w_type):
        self.clear_menu()
        loading = Text(text="Generating World...", origin=(0, 0), scale=2)
        self.entities.append(loading)
        invoke(self.on_start_new, name, w_type, delay=0.1)

    def trigger_load(self, name):
        self.clear_menu()
        loading = Text(text="Loading World...", origin=(0, 0), scale=2)
        self.entities.append(loading)
        invoke(self.on_load, name, delay=0.1)

    def exit_app(self):
        self.clear_menu()
        self.on_exit()
    
    def destroy(self):
        self.clear_menu()
        
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
        self.hint = Text(parent=self, text="Press ESC to Resume", origin=(0,0), y=-0.2, scale=1, color=color.gray)

    def resume(self):
        self.on_resume()
        
    def save_exit(self):
        self.on_save_exit()

    def show(self):
        self.enabled = True
        
    def hide(self):
        self.enabled = False