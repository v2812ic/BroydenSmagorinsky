# Smagorinsky optimizer
---
## How to Use

1. **Set your simulation parameters:**

   - Edit the `caseData.json` file to define the desired configuration for your simulation.

2. **Run the simulation:**

   - Once configured, launch the simulation with:
     ```bash
     ./runCase.sh
     ```

---

## Virtual Environment Setup

You need to create a virtual environment in the project folder named `venv`, with the following Python packages installed:

```
numpy
scipy
matplotlib
pyvista
path
subprocess
os
classy_blocks
threading
tqdm
time
csv
json
pandas
re
shutil
```

> Some additional modules may be required. If you encounter import errors, make sure to install any missing packages with `pip`.

The environment activates automatically while running the bash script.

---

## Known Issues & Recommendations

While known bugs have been addressed, the program **might still crash** under certain conditions:

- **Smagorinsky constant > 0.2:**
  - This can lead to instability. Increasing the number of cells typically resolves this.

- **Non-convergent cell size / timestep combination:**
  - Make sure your cell size and timestep are selected to ensure convergence and stability.
