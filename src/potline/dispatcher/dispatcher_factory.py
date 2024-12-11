"""
dispatcher factory
"""

from pathlib import Path

from .dispatcher import Dispatcher
from .local import LocalDispatcher
from .slurm import SlurmDispatcher, get_slurm_commands, get_slurm_options

class DispatcherFactory():
    """
    Dispatcher factory.
    """
    def __init__(self,
                 job_type: str,
                 cluster: str | None = None):
        self._job_type = job_type
        self._cluster = cluster

    def create_dispatcher(self, commands: list[str], out_path: Path,
                          model: str | None = None,
                          n_cpu: int | None = None,
                          email: str | None = None) -> Dispatcher:
        """
        Create a dispatcher based on the options.

        Returns:
            Dispatcher: the dispatcher to use.
        """
        options: dict | None = None
        tot_cmds: list[str] = commands

        if self._cluster:
            options = get_slurm_options(self._cluster, self._job_type, out_path, model, n_cpu, email)
            tot_cmds = get_slurm_commands(self._cluster, self._job_type, model) + commands
            return SlurmDispatcher(tot_cmds, options)

        print(f"Build dispatcher with: {self._cluster}, {self._job_type}, \
              {out_path}, {model}, {n_cpu}, {email}")
        print(f"Options: {options}")
        print(f"Commands: {tot_cmds}")

        return LocalDispatcher(tot_cmds, options)
