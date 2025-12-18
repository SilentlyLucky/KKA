import math
from multiprocessing import Pool, cpu_count
from config import WIDTH, DEPTH, BASE_HEIGHT, DIRT_LAYER_THICKNESS

# --- WORKER FUNCTION ---
# Fungsi ini berjalan di proses terpisah (core lain).
# Tidak boleh ada kode Ursina/Entity di sini, hanya matematika murni.

def _calculate_chunk_data(args):
    """
    Menghitung data map untuk sebagian area (chunk).
    args: (start_x, end_x, world_type)
    """
    start_x, end_x, world_type = args
    
    local_heights = []
    local_map_data = [] # Akan berisi list of columns (list of lists)
    
    for x in range(start_x, end_x):
        # 1. Hitung Tinggi Permukaan (Sama seperti logika di world.py)
        if world_type == "sand":
            h = BASE_HEIGHT + int(math.sin(x / 30) * 12 + math.cos(x / 15) * 4)
        else:
            h = BASE_HEIGHT + int(math.sin(x / 20) * 10 + math.cos(x / 10) * 5)
            
        # Clamp agar tidak keluar batas
        h = max(5, min(h, DEPTH - 1))
        local_heights.append(h)
        
        # 2. Generate Kolom Blok
        # Kita buat array 1D untuk sumbu Y di posisi X ini
        column = [0] * DEPTH
        
        # Bedrock di dasar
        column[0] = 1 
        
        # Isi tanah/batu sampai ketinggian h
        for y in range(1, h):
            block_val = 1 # Solid (Dirt/Stone/Sand)
            
            # Logika Gua (Cave Noise)
            stone_level = h - DIRT_LAYER_THICKNESS
            
            # Gua hanya muncul di lapisan batu (bawah dirt)
            if y < stone_level:
                # Rumus noise gua
                cave_value = (
                    math.sin(x * 0.1) * math.cos(y * 0.1) 
                    + math.sin(x * 0.05) * math.cos(y * 0.15)
                )
                
                threshold = 0.4 if world_type == "sand" else 0.3
                
                if cave_value > threshold:
                    block_val = 0 # Jadi udara/gua
            
            column[y] = block_val
            
        local_map_data.append(column)
        
    return (start_x, local_heights, local_map_data)

# --- MAIN INTERFACE ---

def generate_map_data_parallel(world_type):
    """
    Fungsi utama untuk membagi tugas ke semua core CPU yang tersedia.
    """
    # Gunakan maksimal core yang ada, tapi batasi agar tidak memakan 100% PC user jika corenya banyak
    # Biasanya disisakan 1-2 core untuk OS dan Main Thread game.
    available_cores = cpu_count()
    num_processes = max(1, available_cores - 1) 
    
    print(f"[MULTIPROCESSING] Menggunakan {num_processes} Core CPU untuk generasi dunia...")
    
    pool = Pool(processes=num_processes)
    
    # Bagi tugas berdasarkan lebar dunia (WIDTH)
    chunk_size = math.ceil(WIDTH / num_processes)
    tasks = []
    
    for i in range(num_processes):
        start = i * chunk_size
        end = min((i + 1) * chunk_size, WIDTH)
        
        if start < end:
            tasks.append((start, end, world_type))
            
    # Jalankan worker secara paralel
    results = pool.map(_calculate_chunk_data, tasks)
    
    pool.close()
    pool.join()
    
    # Gabungkan hasil dari tiap worker
    final_heights = [0] * WIDTH
    final_map_data = [[0] * DEPTH for _ in range(WIDTH)]
    
    for res in results:
        start_x, heights, columns = res
        
        for i, h in enumerate(heights):
            if start_x + i < WIDTH:
                final_heights[start_x + i] = h
                
        for i, col in enumerate(columns):
            if start_x + i < WIDTH:
                final_map_data[start_x + i] = col

    return final_heights, final_map_data