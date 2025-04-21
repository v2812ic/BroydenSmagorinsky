import numpy as np # type: ignore
import subprocess
from pathlib import Path
import pyvista as pv  # type: ignore
import os
import matplotlib.pyplot as plt  # type: ignore
from scipy.interpolate import interp1d

def error(sim_path, tEnd, Ce, Ck, Re):
    sim_path = Path(sim_path)
    subprocess.run(["foamToVTK", "-time", str(tEnd)], cwd=sim_path, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    vtk_root = "VTK"

    vtu_file = None
    for root, dirs, files in os.walk(sim_path / vtk_root):
        for file in files:
            if file == "internal.vtu":
                vtu_file = os.path.join(root, file)
                break
        if vtu_file:
            break

    if vtu_file is None:
        raise FileNotFoundError("No se encontró el archivo internal.vtu dentro de VTK/")

    mesh = pv.read(vtu_file)

    # Velocidad U, posición Z
    sampled_z = mesh.sample_over_line(pointa=(0.5, 0.5, 0.0), pointb=(0.5, 0.5, 1.0), resolution=300)
    z = sampled_z.points[:, 2]
    Ux = sampled_z["U"][:, 0]

    # Velocidad W, posición X
    sampled_x = mesh.sample_over_line(pointa=(0.0, 0.5, 0.5), pointb=(1.0, 0.5, 0.5), resolution=300)
    x = sampled_x.points[:, 0]
    Uz = sampled_x["U"][:, 2]

    # Datos de referencia

    x_ref, W_ref, U_ref, z_ref = [], [], [], []

    if Re == 3200:
        x_ref = [0, 0.01075269825333181, 0.016897113997376003, 0.024577604378685773, 0.0399385851413052, 0.07066054666654395, 0.10138250819178268, 0.13517661899155237, 0.16436250587952575, 0.2012288831488088, 0.3010752581058349, 0.4024577077001264, 0.5023040826571525, 0.6036865322514441, 0.7004607579339391, 0.7987710582536998, 0.8387095847975137, 0.8663593970482218, 0.9016895824852567, 0.9201228297173895, 0.9400920343918052, 0.9569890897916901, 0.9677418466425132, 0.9784944862983538, 0.9892472431491768, 1]
        W_ref = [0, 0.06832298762102651, 0.10248454807027052, 0.1366459900506598, 0.1894410427675972, 0.2049689924802931, 0.1987577889014438, 0.1832298391887479, 0.16459634692105451, 0.1397515326056573, 0.07453419119987581, 0.040372749219486526, 0.027950342061787925, 0.006211188770242515, -0.024844710655149593, -0.06521759315209741, -0.09937891666363219, -0.15838529142827318, -0.28571419474712945, -0.36956514688945874, -0.41304345347254934, -0.35714285820061487, -0.2670809394171454, -0.18633541136095866, -0.09627349257748918, 0]
        
        U_ref = [0, -0.1292307775373278, -0.06769232322196117, -0.17846172879008027, -0.22153845901037872, -0.2676922997469037, -0.26461542398124993, -0.23384619682356655, -0.18461548032138764, -0.12000015024036692, -0.070769433738188, -0.03384622029862383, -0.012307855188475103, 0.0030767583903670293, 0.021538247734862237, 0.04615372336123835, 0.0799998262845758, 0.09230756409776397, 0.11692303972413964, 0.13538452906863485, 0.1692306319919723, 0.24307682412052745, 0.3507691191724196, 0.4553845384586581, 0.6307690393572243, 0.8369227674134749, 1]
        z_ref = [0, 0.007763974971321762, 0.013975178642150322, 0.021739153613471864, 0.029503128584793623, 0.04968939242891609, 0.07608697841272354, 0.1133540819688387, 0.14285709208477568, 0.177018653039905, 0.21583852789651325, 0.27950309896757947, 0.38664597726558947, 0.5046583731359073, 0.6055900477630887, 0.7003105779538699, 0.799689451663344, 0.8354036654501099, 0.8695651967880249, 0.9021738975910186, 0.9409937724476269, 0.9627328964438847, 0.9736024732506205, 0.9798136473042351, 0.9906832241109711, 0.9968944129731927, 1]
    
    elif Re == 5000:
        x_ref = [0, 0.009259294689546954, 0.0200617168575065, 0.03858030623660041, 0.06944450413085224, 0.10493826106669898, 0.13734564530814908, 0.16975314728717042, 0.2021605315286205, 0.3024691746849388, 0.402777817841257, 0.5077160200391702, 0.5509259441861513, 0.614197526321853, 0.6790124125423248, 0.7438271810252249, 0.7947531546457688, 0.83641977470798, 0.8703703452966284, 0.895061797802087, 0.9104938967492128, 0.9182099462227756, 0.9259259956963387, 0.932098741085132, 0.9413580946434645, 0.9552468895058209, 0.9706789884529468, 0.9783950379265096, 0.9861110874000726, 1]
        W_ref = [0, 0.04687504121102082, 0.09687498980201847, 0.15312508097849165, 0.1656250085216009, 0.15937498514540605, 0.1468750576022968, 0.13125005876645002, 0.11249998863786526, 0.05937508796341051, 0.028125090291716726, 0.012500091455869722, 0.009375020163132186, -0.00312490737997706, -0.015624954132366753, -0.034374905051670734, -0.04999990388751763, -0.06250018905846877, -0.08749992493540626, -0.13437492144294683, -0.1875001797452437, -0.22187489108183323, -0.2624999834224595, -0.3062499086372622, -0.35624997643754086, -0.3937498782761486, -0.33437495422549923, -0.25000017508863115, -0.1562501820735498, 0]

        U_ref = [0, -0.06790120004608213, -0.15123444017050514, -0.2314815430756738, -0.19444436431748602, -0.16666653911763096, -0.13271596852898238, -0.09876539794033423, -0.04938272840455982, -0.021604903204704762, -5.886878540195539e-8, 0.024691393636673054, 0.04012349258379899, 0.064814945089257, 0.10185188837230252, 0.1388888316553476, 0.21296295369658025, 0.3271606271903975, 0.44444443790346866, 0.5493827578389532, 0.7191358462573378, 1]
        z_ref = [0, 0.006250023376194846, 0.01562499883584687, 0.039062497089617065, 0.08281254151370071, 0.12343751464504625, 0.1687500351108584, 0.215625031618399, 0.30000004917382816, 0.3921875065425406, 0.5031250340398374, 0.6140625019324941, 0.689062484423631, 0.7843750130850812, 0.8890624874038631, 0.943749983329327, 0.9671874815830974, 0.9781249926891182, 0.9843749862629929, 0.9874999979510904, 0.9937499915249651, 1]
    
    # Interpolación cubica sobre los puntos de referencia
    Ux_interp_fun = interp1d(z, Ux, kind='cubic', fill_value="extrapolate")
    Uz_interp_fun = interp1d(x, Uz, kind='cubic', fill_value="extrapolate")

    Ux_interp = Ux_interp_fun(z_ref)
    Uz_interp = Uz_interp_fun(x_ref)

    # Errores cuadráticos normalizados (cuadrado de la norma L2 discreta) Esto se puede cambiar para cambiar el comportamiento de la función
    E_U = np.sum((Ux_interp - U_ref)**2) / len(U_ref)
    E_W = np.sum((Uz_interp - W_ref)**2) / len(W_ref)

    # Promedio de los dos errores
    error_medio = 0.5 * (E_U + E_W)

    print("Error U:", E_U)
    print("Error W:", E_W)
    print("Error medio:", error_medio)

    
    fig, ax = plt.subplots(figsize=(6, 6))

    # Ejes secundarios
    ax_u = ax.twiny()  # Para U(z), arriba
    ax_w = ax.twinx()  # Para W(x), derecha

    # U(z): curva simulada y puntos de referencia
    ax_u.plot(Ux, z, '--', label="U(z) simulada", color = "#ff7f0e")
    ax_u.scatter(U_ref, z_ref, color='k', marker='o', zorder=5, s = 10)
    ax_u.set_xlabel("U")
    ax_u.set_xlim(-1, 1)

    # W(x): curva simulada y puntos de referencia
    ax_w.plot(x, Uz, '--', label="W(x) simulada", color = '#1f77b4')
    ax_w.scatter(x_ref, W_ref, color='k', marker='o', zorder=5, s = 10, label = "Referencia")
    ax_w.set_ylabel("W", labelpad=15)
    ax_w.set_ylim(-1, 1)

    # Eje base: dominio físico
    ax.set_xlabel("X")
    ax.set_ylabel("Z")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.grid(True, linestyle="--", alpha=0.4)
    ax.minorticks_on()
    ax.grid(True, which='minor', linestyle=':', linewidth=0.5, alpha=0.4)

    plt.suptitle(f"Perfiles de velocidad para constantes: Ce = {Ce:.3f}, Ck = {Ck:.3f}", fontsize=12, y = 0.92)

    # Combinar leyendas de ambos ejes
    handles_u, labels_u = ax_u.get_legend_handles_labels()
    handles_w, labels_w = ax_w.get_legend_handles_labels()
    ax.legend(handles_u + handles_w, labels_u + labels_w, loc='lower right')

    # Ajustar layout para dejar espacio al título y etiquetas
    fig.subplots_adjust(top=0.8, right=0.8)
    # Guardar imagen
    output_dir = Path("output")
    output_dir_png = output_dir / "png"
    output_dir_svg = output_dir / "svg"
    output_dir_png.mkdir(exist_ok=True)
    output_dir_svg.mkdir(exist_ok=True)
    sim_name = sim_path.name
    plt.savefig(output_dir_png / f"perfiles{sim_name}.png")
    plt.savefig(output_dir_svg / f"perfiles{sim_name}.svg", format='svg')
    plt.close()
    
    return error_medio, E_U, E_W
