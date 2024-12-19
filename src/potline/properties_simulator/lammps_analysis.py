"""
Properties simulation.
"""

from pathlib import Path
import shutil

from ..config_reader import PropConfig
from ..model import PotModel
from ..dispatcher import DispatcherManager

PROPERTIES_BENCH_DIR_NAME: str = 'properties_bench'
SUBMIT_SCRIPT_NAME: str = 'submit.sh'
PROP_BENCH_TEMPLATE_PATH: Path = Path(__file__).parent / 'template'
SUBMIT_TEMPLATE_PATH: Path = PROP_BENCH_TEMPLATE_PATH / SUBMIT_SCRIPT_NAME

_N_CPU: int = 1

class PropertiesSimulator():
    """
    Class for running the LAMMPS properties simulations.

    Args:
        - config: configuration for the simulations
        - model_list: models to simulate
        - dispatcher_manager: manager for dispatching simulation jobs
    """
    def __init__(self, config: PropConfig, model_list: list[PotModel],
                 dispatcher_manager: DispatcherManager):
        self._config = config
        self._model_list = model_list
        self._dispatcher_manager = dispatcher_manager
        self._lammps_params = model_list[0].get_lammps_params()
        self._out_path = self._config.sweep_path / PROPERTIES_BENCH_DIR_NAME
        self._out_path.mkdir(exist_ok=True)

        self._sim_cmd: str = ' '.join(
            [str(cmd) for cmd in [
                'srun', SUBMIT_SCRIPT_NAME,
                f'"{config.lammps_bin_path} {self._lammps_params}"',
                config.lammps_inps_path, config.pps_python_path, config.ref_data_path,
                config.email, _N_CPU]])

        for i, model in enumerate(self._model_list):
            iter_path = self._out_path / str(i)
            iter_path.mkdir(exist_ok=True)
            shutil.copy(SUBMIT_TEMPLATE_PATH, iter_path)
            shutil.copy(model.get_pot_path(), iter_path)

    def run(self):
        self._dispatcher_manager.set_job([self._sim_cmd],
                                         self._out_path,
                                         self._config.job_config,
                                         list(range(1,len(self._model_list)+1)))
        self._dispatcher_manager.dispatch_job()
