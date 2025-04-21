from tqdm import tqdm
import subprocess
import threading
import time
import os

def run_with_progress(sim_path, tEnd, check_interval=2):
    process = subprocess.Popen(
        ["pisoFoam"],
        cwd=sim_path,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

    pbar = tqdm(total=tEnd, desc="Progreso de iteración", unit="s", ncols=80)

    def monitor_progress():
        last_time = 0.0
        while process.poll() is None:
            # Buscar los nombres de carpeta que sean números
            folders = [f for f in os.listdir(sim_path) if f.replace('.', '', 1).isdigit()]
            if folders:
                times = sorted([float(f) for f in folders])
                current_time = max(times)
                if current_time > last_time:
                    pbar.update(current_time - last_time)
                    last_time = current_time
            time.sleep(check_interval)
        
        # Al finalizar, asegurarse de completar la barra
        pbar.update(tEnd - pbar.n)
        pbar.close()

    monitor_thread = threading.Thread(target=monitor_progress)
    monitor_thread.start()
    process.wait()
    monitor_thread.join()