from pathlib import Path
import subprocess
import shutil
import os
import json
import time
import numpy as np # type: ignore
from error_Broyden import error
from concurrent.futures import ProcessPoolExecutor, as_completed
from plotVelocity import plot_velocity_map
from progress import run_with_progress
import csv

# No me gusta usar variables globales pero es lo que toca porque si no tengo que cambiar 40000 lineas de codigo
#----------------------------------------------------------------------------------------------------------------
with open("caseData.json", "r") as file:
    params = json.load(file)
tEnd = params["tEnd"]
tol = params["tolBroyden"]
deltaT = params["deltaT"]
tInterval = 1/deltaT
CeInit = params["CeInit"]
CkInit = params["CkInit"]
tInitStationary = params["tInitStationary"]
test = params["test"]
Re = params["Re"]

if Re != 3200 and Re != 5000:
    raise ValueError("Re debe ser 3200 o 5000 de momento, no esta implementado para comparar con más")

if not tInitStationary % tInterval:
    raise ValueError("tInitStationary no es múltiplo de deltaT. Cambia el valor de tInitStationary en caseData.json")

# ----------------- AUX: OBTENER VALOR MAXIMO DE Yplus
def ymas(t, sim_path):
    t_str = str(t)
    path_try1 = os.path.join(sim_path, t_str, "yPlus")
    
    if not os.path.exists(path_try1):
        if float(t).is_integer():
            t_str = str(int(t))
            path_try2 = os.path.join(sim_path, t_str, "yPlus")
            if os.path.exists(path_try2):
                path = path_try2
            else:
                raise FileNotFoundError(f"No se encontró 'yPlus' ni en {path_try1} ni en {path_try2}")
        else:
            raise FileNotFoundError(f"No se encontró 'yPlus' en {path_try1}")
    else:
        path = path_try1

    startCounting = False
    max_yPlus = 0
    with open(path, "r") as file:
        for linea in file:
            linea = linea.strip()
            if linea == "(":
                startCounting = True
            elif startCounting and linea == ")":
                startCounting = False
            elif startCounting:
                try:
                    value = float(linea)
                    max_yPlus = max(max_yPlus, value)
                except ValueError:
                    continue  
    return max_yPlus

def ymasaverage(t, sim_path):
    t_str = str(t)
    path_try1 = os.path.join(sim_path, t_str, "yPlus")
    
    if not os.path.exists(path_try1):
        if float(t).is_integer():
            t_str = str(int(t))
            path_try2 = os.path.join(sim_path, t_str, "yPlus")
            if os.path.exists(path_try2):
                path = path_try2
            else:
                raise FileNotFoundError(f"No se encontró 'yPlus' ni en {path_try1} ni en {path_try2}")
        else:
            raise FileNotFoundError(f"No se encontró 'yPlus' en {path_try1}")
    else:
        path = path_try1

    startCounting = False
    av_yPlus = 0
    indices = 0
    with open(path, "r") as file:
        for linea in file:
            linea = linea.strip()
            if linea == "(":
                startCounting = True
            elif startCounting and linea == ")":
                startCounting = False
            elif startCounting:
                try:
                    value = float(linea)
                    av_yPlus += value
                    indices += 1
                except ValueError:
                    continue  
    return av_yPlus/indices

# ------------------ FUNCIÓN DE SIMULACIÓN ------------------ #
def f(C, tEnd, buena = False):
    Ce, Ck = C

    if not buena:
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        sim_name = f"sim_{timestamp}_Ce{Ce}_Ck{Ck}"
        sim_path = Path("simulaciones") / sim_name
    
    else:
        sim_name = "Constantes_Optimas"
        sim_path = Path("simulaciones") / sim_name

    os.makedirs(sim_path, exist_ok=True)

    # Copiar carpetas
    for folder in ["0", "constant", "system"]:
        src = Path(folder)
        dst = sim_path / folder
        if dst.exists():
            shutil.rmtree(dst)
        shutil.copytree(src, dst)

    # Modificar coeficientes en turbulenceProperties
    turb_file = sim_path / "constant" / "turbulenceProperties"
    if turb_file.exists():
        with open(turb_file, "r") as f_in:
            lines = f_in.readlines()

        with open(turb_file, "w") as f_out:
            in_coeff_block = False
            for line in lines:
                if "SmagorinskyCoeffs" in line:
                    in_coeff_block = True
                if in_coeff_block:
                    if "Ce" in line:
                        line = f"        Ce          {Ce};\n"
                    elif "Ck" in line:
                        line = f"        Ck          {Ck};\n"
                    elif "}" in line:
                        in_coeff_block = False
                f_out.write(line)

    try:
       
        run_with_progress(sim_path, tEnd)

        start_step = tInitStationary / deltaT # Flujo suficientemente desarrollado
        end_step = int(tEnd / deltaT)
        step_indices = np.arange(start_step, end_step + 1, tInterval)
        times = step_indices * deltaT
        times = np.round(times, 6)

        ymasMaxTotal = 0
        yAverage = 0

        for t in times:
            ymasMaxTotal = max(ymasMaxTotal, ymas(t, sim_path))
            yAverage += ymasaverage(t, sim_path)/len(times)

        if ymasMaxTotal > 30:
            print(f"❌ y+ máximo superior a 30 en la simulación {sim_name}: {ymasMaxTotal:.4f}.")
            return "yplus_error"

        if ymasMaxTotal > 5:
            print(f"⚠️ y+ máximo superior a 5 en la simulación {sim_name}: {ymasMaxTotal:.4f}.")
        
        else:
            print(f"y+ máximo total en la simulación actual: {ymasMaxTotal:.4f}")

        print(f"y+ medio en la simulación: {yAverage:.4f}")

    except subprocess.CalledProcessError:
        print(f"❌ Error ejecutando pisoFoam en {sim_path}")
        return float("inf")
    
    err, E_U, E_W = error(sim_path, tEnd, Ce, Ck, Re)

    if not buena:
        with open("output/registro_simulaciones.csv", "a", newline="") as csvfile:
            writer = csv.writer(csvfile)
            Cs = np.sqrt(Ck*np.sqrt(Ck/Ce))
            writer.writerow([Ce, Ck, err, E_U, E_W, Cs])
        
    with open("output/registro_yPlus.csv", "a", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([Ce, Ck, yAverage, ymasMaxTotal])

    return err

# PRUEBA DE CONVERGENCIA
def f2(C, tEnd, buena = False):
    x, y = C
    return x**2 + y**2 + 1/(x**2 + y**2 + 1)

# FUNCIÓN CON LA QUE SE CORRE VERDADERAMENTE LA SIM
def f_log(u, tEnd, buena = False):
    C = np.exp(u)
    return f(C, tEnd, buena)

# ------------------ GRADIENTE NUMÉRICO ------------------ #
def grad(C, tEnd, fun):
    C = np.array(C)
    h = 1e-2
    tasks = []

    for i in range(len(C)):
        C_plus = C.copy()
        C_minus = C.copy()
        C_plus[i] += h
        C_minus[i] -= h
        tasks.append(C_plus)
        tasks.append(C_minus)

    results = [None] * len(tasks)

    # Paralelizar evaluaciones de f
    with ProcessPoolExecutor(max_workers=6) as executor:
        future_to_index = {executor.submit(fun, C_i, tEnd): idx for idx, C_i in enumerate(tasks)}
        for future in as_completed(future_to_index):
            idx = future_to_index[future]
            try:
                result = future.result()
                if result == "yplus_error":
                    print("y+ inválido detectado. Abortando ejecución global.")
                    os._exit(1) 
                results[idx] = result
            except Exception as e:
                print(f"⚠️ Error en tarea {idx}: {e}")
                results[idx] = float("inf")

    # Calcular gradiente numérico
    gradient = []
    for i in range(len(C)):
        if results[2*i] == "yplus_error" or results[2*i + 1] == "yplus_error":
            return "yplus_error"
        f_plus = results[2 * i]
        f_minus = results[2 * i + 1]
        grad_i = (f_plus - f_minus) / (2 * h)
        gradient.append(grad_i)

    Ce, Ck = np.exp(C)
    with open("output/registro_gradientes.csv", "a", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([Ce, Ck] + list(gradient))

    return np.array(gradient)


# ------------------ BROYDEN ------------------ #
def Broyden(gradf, C0, S, tol = 1e-5):
    it = 1
    while np.linalg.norm(gradf) > tol:
        # Paso de Broyden
        DeltaC = -S @ gradf
        C1 = C0 + DeltaC

        # Nuevo gradiente
        gradf_new = grad(C1, tEnd, f_log)

        delta_g = gradf_new - gradf
        denom = delta_g @ DeltaC

        # Actualización de la inversa del Jacobiano (Broyden II)
        correction = np.outer((DeltaC - S @ delta_g), DeltaC) / denom
        S = S + correction

        # Actualizar para la próxima iteración
        C0 = C1
        gradf = gradf_new

        print(f"\n")
        print(f"Iteración {it}")
        it += 1
        print("Inversa del Jacobiano actualizada:\n", S, "\n")
        print("Constantes actuales (reales):\n", np.exp(C0), "\n")
        print("Constante de Smagorinsky actual:", np.sqrt(np.exp(C0[1])*np.sqrt(np.exp(C0[1])/np.exp(C0[0]))), "\n")
        print("Gradiente actual:\n", gradf, "\n")
        print("-" * 50)

    return C0

# ------------------ MAIN ------------------ #
if __name__ == "__main__":

    with open("output/registro_simulaciones.csv", "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Ce", "Ck", "Error", "E_U", "E_W", "Cs"])

    with open("output/registro_gradientes.csv", "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Ce", "Ck", "Grad_Ce", "Grad_Ck"])

    with open("output/registro_yPlus.csv", "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Ce", "Ck", "Average", "Max"])

    # Vectores iniciales Ce, Ck
    u0, tasks, results = None, None, None
    C0 = np.array([CeInit, CkInit])

    if CkInit != 0 and not test:
        u0 = np.log(C0)
        tasks = [u0]
        results = [None] * len(tasks)  
    elif CkInit == 0 and not test:
        raise ValueError("CkInit no puede ser 0 si no es un test")    
    
    tInit = time.time()

    if not test:
        # Paralelizar cálculo inicial de gradientes (antes eran 2 y ahora es 1 pero lo dejo por si acaso para que no pete)
        with ProcessPoolExecutor(max_workers=2) as executor:
            future_to_index = {
                executor.submit(grad, task, tEnd, f_log): idx
                for idx, task in enumerate(tasks)
            }
            for future in as_completed(future_to_index):
                idx = future_to_index[future]
                try:
                    results[idx] = future.result()
                except Exception as e:
                    print(f"⚠️ Error en tarea grad({idx}): {e}")
                    results[idx] = float("inf")
        
        gradf0 = results[0]

        if gradf0[0] == "yplus_error" or gradf0[1] == "yplus_error":
            print("Error en y+ detectado en el gradiente inicial. Abortando")
            exit(1)

        J = np.eye(len(C0))

        print("\n")
        print(f"Iteración 0")
        print("Jacobiano actual (id):\n", J, "\n")
        print("Gradiente actual:\n", gradf0, "\n")
        print("\n")
        cOpt = Broyden(gradf0, u0, J, tol)
        cOpt = np.exp(cOpt) 
    
    if test:
        cOpt = C0

    print("Constantes óptimas (Ce, Ck):", cOpt)

    print("Calculando la simulación correcta")
    
    f(cOpt, tEnd, buena = True)

    print("Ploteando")
    pathBuena = Path("simulaciones/Constantes_Optimas")
    plot_velocity_map(pathBuena, tEnd)


    print("Simulación completada con éxito (hopefully). Ver logs para todos los detalles")
    Cs = np.sqrt(cOpt[1]*np.sqrt(cOpt[1]/cOpt[0]))
    print(f"Constante de Smagorinsky: {Cs:.4f}")
    print("\n")
    tiempoEjecucion = time.time()-tInit
    print("Tiempo de ejecución:", f"{tiempoEjecucion:.2f}", "s")

    with open("output/tiempoEjecucion.csv", "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow( [f"Tiempo de ejecución: {tiempoEjecucion:.2f} s"] )

    # Definitivamente futuro trabajo es limpiar el código y hacerlo más robusto, porque madre del señor esto es frankenstein