"""
Pacemaker wrapper for fitting ACE potentials using XPOT in HPC.
"""

from __future__ import annotations

import subprocess
from pathlib import Path
from collections.abc import Callable

import yaml
import numpy as np
import pandas as pd
from xpot import maths

from .model import PotModel, RawLosses, POTENTIAL_TEMPLATE_PATH, CONFIG_NAME, Losses
from ..dispatcher import DispatcherFactory, SupportedModel
from ..utils import gen_from_template

LAST_POTENTIAL_NAME: str = 'output_potential.yaml'

class PotPACE(PotModel):
    """
    PACE implementation.
    Requires pacemaker.
    """
    def dispatch_fit(self,
                     dispatcher_factory: DispatcherFactory,
                     deep: bool = False):
        commands: list[str] = [
            f'cd {self._out_path}',
            ' '.join(['pacemaker', str(self._config_filepath)] +
                     ([f'-p {str(self._out_path / LAST_POTENTIAL_NAME)}']
                      if deep else []))
        ]
        self._dispatcher = dispatcher_factory.create_dispatcher(
            commands, self._out_path, SupportedModel.PACE.value)
        self._dispatcher.dispatch()

    def collect_loss(self) -> Losses:
        if self._dispatcher is None:
            raise ValueError("Dispatcher not set.")
        self._dispatcher.wait()
        return self._validate_errors(self._calculate_errors())

    def lampify(self) -> Path:
        """
        Convert the model YAML to YACE format.

        Returns:
            Path: The path to the YACE file.
        """
        subprocess.run(['pace_yaml2yace', '-o',
                        str(self._yace_path),
                        str(self._out_path / LAST_POTENTIAL_NAME)],
                        check=True)
        return self._yace_path

    def create_potential(self) -> Path:
        """
        Create the potential in YACE format.

        Returns:
            Path: The path to the potential.
        """
        potential_values: dict = {
            'pstyle': 'pace',
            'yace_path': str(self._yace_path),
        }
        gen_from_template(POTENTIAL_TEMPLATE_PATH, potential_values, self._lmp_pot_path)
        return self._lmp_pot_path

    def set_config_maxiter(self, maxiter: int):
        """
        Set the maximum number of iterations in the configuration file.
        """
        with self._config_filepath.open('r', encoding='utf-8') as file:
            config = yaml.safe_load(file)

        config['fit']['maxiter'] = maxiter

        with self._config_filepath.open('w', encoding='utf-8') as file:
            yaml.safe_dump(config, file)

    def _collect_raw_errors(self) -> pd.DataFrame:
        """
        Collect errors from the fitting process.
        """
        errors_filepath: Path = self._out_path / "test_pred.pckl.gzip"
        df = pd.read_pickle(errors_filepath, compression="gzip")
        return df

    def _calculate_errors(self) -> RawLosses:
        """
        Validate the potential from pickle files produced by :code:`pacemaker`
        during the fitting process.

        Returns
        -------
        dict
            The errors as a dictionary of lists.
        """
        errors = self._collect_raw_errors()

        n_per_structure = errors["NUMBER_OF_ATOMS"].values.tolist()

        ref_energy = errors["energy_corrected"].values.tolist()
        pred_energy = errors["energy_pred"].values.tolist()

        energy_diff = [pred - ref for pred, ref in zip(pred_energy, ref_energy)]

        ref_forces = np.concatenate(errors["forces"].to_numpy(), axis=None)
        pred_forces = np.concatenate(
            errors["forces_pred"].to_numpy(), axis=None
        )
        forces_diff = [pred - ref for pred, ref in zip(pred_forces, ref_forces)]

        return RawLosses(energy_diff, forces_diff, n_per_structure)

    def _validate_errors(
        self,
        errors: RawLosses,
        metric: Callable = maths.get_rmse,
        n_scaling: float = 1,
    ) -> Losses:
        """
        Calculate the training and validation error values specific to the loss
        function of XPOT from the MLP.
        """
        energy_diff = (
            errors.energies
            / np.array(errors.atom_counts) ** n_scaling
        )
        return Losses(metric(energy_diff), metric(errors.forces))

    @staticmethod
    def from_path(out_path):
        """
        Create a model from a path.
        """
        return PotPACE(out_path / CONFIG_NAME, out_path)
