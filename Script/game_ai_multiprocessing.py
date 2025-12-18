import heapq
import math

# --- LOGIKA A* (A-STAR) MURNI ---
# Fungsi ini akan dijalankan di core CPU lain.
# Kita tidak boleh menggunakan objek 'World' atau 'Entity' ursina di sini.
# Kita hanya menerima data mentah (list of lists map_data).

def get_neighbors_raw(x, y, width, depth, map_data):
    """Mencari tetangga yang valid berdasarkan map_data mentah"""
    res = []
    # 8 Arah (termasuk diagonal)
    for dx, dy in [(1,0), (-1,0), (1,1), (-1,1), (1,-1), (-1,-1), (0, 1), (0, -1)]:
        nx, ny = x + dx, y + dy
        
        # Cek batas dunia
        if not (0 <= nx < width and 0 <= ny < depth):
            continue
            
        # Cek apakah bisa dipijak (Logic is_standable versi data mentah)
        # 1. Badan (ny) harus kosong (0) atau tembus pandang (bukan 1/tanah padat)
        #    Note: Di map_data, biasanya 0=Udara, 1=Tanah. Tapi ada ID blok lain.
        #    Kita asumsikan blok ID < 100 yang BUKAN 0 adalah PADAT kecuali GRASS_PLANT(9), LOG(10), LEAVES(11), TORCH(101).
        #    Untuk simplifikasi multiprocessing, kita kirim solid_map (True/False) daripada block ID, atau kita proses di sini.
        
        # Sederhananya untuk A* cepat: Cek apakah blok tsb 0 (udara) atau tipe 'passable'
        # Kita terima 'collision_map' (True jika padat, False jika bisa lewat)
        
        # Cek Badan (nx, ny) -> Harus False (Tidak Padat)
        if map_data[nx][ny]: 
            continue
            
        # Cek Kepala (nx, ny+1) -> Harus False (Tidak Padat)
        if ny + 1 < depth and map_data[nx][ny+1]:
            continue
            
        # Cek Kaki (nx, ny-1) -> Harus True (Padat/Pijakan)
        if ny - 1 >= 0:
            if not map_data[nx][ny-1]: # Jika kaki kosong (udara), tidak bisa pijak
                continue
        else:
            continue
            
        res.append((nx, ny))
    return res

def calculate_path_astar(args):
    """
    Worker function untuk menghitung jalur.
    args: (start_pos, target_pos, width, depth, solid_map_data)
    """
    start, goal, width, depth, solid_map = args
    
    # Batasi pencarian agar worker tidak hang selamanya
    max_steps = 500 
    
    def h(a, b): return abs(a[0]-b[0]) + abs(a[1]-b[1])
    
    open_set = [(0, start)]
    came_from = {}
    g_score = {start: 0}
    
    steps = 0
    
    while open_set:
        steps += 1
        if steps > max_steps:
            return [] # Gagal menemukan jalan dalam batas step
            
        current_score, current = heapq.heappop(open_set)
        
        if current == goal:
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            path.reverse()
            return path
            
        neighbors = get_neighbors_raw(current[0], current[1], width, depth, solid_map)
        
        for neighbor in neighbors:
            tentative_g_score = g_score[current] + 1
            
            if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g_score
                f_score = tentative_g_score + h(neighbor, goal)
                heapq.heappush(open_set, (f_score, neighbor))
                
    return []