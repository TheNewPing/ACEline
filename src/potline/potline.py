"""
Potential optimization pipeline API.
"""

from .config_reader import ConfigReader
from .optimizer import Optimizer
from .lammps_runner import run_benchmark
from .lammps_analysis import run_properties_simulation

class PotLine():
    """
    Main class for running the optimization pipeline.

    Args:
    - config_path: path to the configuration file.
    - max_iter: maximum number of iterations for the optimization.
    - with_inference: flag to run the inference benchmark.
    - with_data_analysis: flag to run the data analysis on mechanical properties.
    """
    def __init__(self, config_path: str,
                 max_iter: int,
                 with_inference: bool,
                 with_data_analysis: bool,):
        self.config_reader = ConfigReader(config_path)
        self.max_iter: int = max_iter
        self.optimizer: Optimizer = self.config_reader.create_optimizer()
        self.with_inference: bool = with_inference
        self.with_data_analysis: bool = with_data_analysis

    def run(self) -> None:
        """
        Run the optimization pipeline.
        1. Optimize the potential, convert the results to yace format, print the final results.
        2. Run the inference benchmark.
        3. Run the data analysis on mechanical properties
        """
        yace_list: list[str] = self.optimizer.optimize(self.max_iter)
        self.optimizer.get_final_results()

        if self.with_inference:
            inf_config: dict = self.config_reader.get_inf_benchmark_config()
            for yace_path in yace_list:
                run_benchmark()
        if self.with_data_analysis:
            data_config: dict = self.config_reader.get_data_analysis_config()
            run_properties_simulation()
