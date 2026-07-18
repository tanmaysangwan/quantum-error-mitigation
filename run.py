import sys  # Reads the requested experiment name.

from experiments.noise_demos.amplitude_damping_demo import main as amplitude  
from experiments.noise_demos.bell_state_demo import main as bell  
from experiments.noise_demos.coherent_gate_error_demo import main as coherent  
from experiments.noise_demos.combined_noise_demo import main as combined  
from experiments.noise_demos.depolarizing_noise_demo import main as depolarizing  
from experiments.noise_demos.ghz_demo import main as ghz  
from experiments.noise_demos.phase_damping_demo import main as phase  
from experiments.noise_demos.readout_error_demo import main as readout  
from src.mitigation.mem_demo import main as mem  
from src.mitigation.zne import main as zne
from src.mitigation.pec import main as pec
from src.mitigation.cdr import main as cdr

EXPERIMENTS = {
    "bell": bell,
    "ghz": ghz,
    "depolarizing": depolarizing,
    "readout": readout,
    "phase": phase,
    "amplitude": amplitude,
    "coherent": coherent,
    "combined": combined,
    "mem": mem,
    "zne": zne,
    "pec": pec,
    "cdr": cdr,
}  # Maps short names to experiment entry points.


def main():
    if len(sys.argv) != 2:  # Require exactly one experiment name.
        print("Usage: python run.py <experiment>")
        print("\nAvailable experiments:")
        for name in EXPERIMENTS:
            print(f"  - {name}")
        return

    experiment = sys.argv[1].lower()  # Read the requested experiment name.

    if experiment not in EXPERIMENTS:  # Reject unknown names.
        print(f"Unknown experiment: {experiment}")
        return

    EXPERIMENTS[experiment]()  # Run the selected experiment.


if __name__ == "__main__":
    main()