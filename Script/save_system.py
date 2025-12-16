import pickle
import os
from config import WIDTH, DEPTH

# Folder untuk menyimpan save file
SAVE_FOLDER = "Saves"

if not os.path.exists(SAVE_FOLDER):
    os.makedirs(SAVE_FOLDER)

def get_save_path(world_name):
    return os.path.join(SAVE_FOLDER, f"{world_name}.ursinasave")

def save_game(world_name, world_data, player_data):
    """
    Menyimpan data world dan player ke file.
    """
    data = {
        "world_type": world_data["world_type"],
        "map_data": world_data["map_data"],
        "ore_map": world_data["ore_map"],
        "player_pos": player_data["position"],
        "seed": world_data.get("seed", 42)
    }
    
    try:
        with open(get_save_path(world_name), "wb") as f:
            pickle.dump(data, f)
        print(f"Game saved successfully: {world_name}")
        return True
    except Exception as e:
        print(f"Failed to save game: {e}")
        return False

def load_game(world_name):
    """
    Memuat data dari file.
    """
    path = get_save_path(world_name)
    if not os.path.exists(path):
        print(f"Save file not found: {world_name}")
        return None
        
    try:
        with open(path, "rb") as f:
            data = pickle.load(f)
        return data
    except Exception as e:
        print(f"Failed to load game: {e}")
        return None

def get_saved_worlds():
    """
    Mengembalikan list nama file save yang ada.
    """
    if not os.path.exists(SAVE_FOLDER):
        return []
    
    files = [f.replace(".ursinasave", "") for f in os.listdir(SAVE_FOLDER) if f.endswith(".ursinasave")]
    return files

def delete_world(world_name):
    """Menghapus file save world."""
    path = get_save_path(world_name)
    if os.path.exists(path):
        try:
            os.remove(path)
            print(f"World deleted: {world_name}")
            return True
        except Exception as e:
            print(f"Error deleting world: {e}")
            return False
    return False

def rename_world(old_name, new_name):
    """Mengganti nama file save world."""
    old_path = get_save_path(old_name)
    new_path = get_save_path(new_name)
    
    if not os.path.exists(old_path):
        print("Old world file does not exist.")
        return False
        
    if os.path.exists(new_path):
        print("A world with the new name already exists.")
        return False
        
    try:
        os.rename(old_path, new_path)
        print(f"World renamed from {old_name} to {new_name}")
        return True
    except Exception as e:
        print(f"Error renaming world: {e}")
        return False