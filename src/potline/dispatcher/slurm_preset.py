"""
Preset job slurm.
"""

from pathlib import Path
from enum import Enum

class SupportedModel(Enum):
    """
    Supported models.
    """
    PACE = "pacemaker"
    MACE = "mace"
    GRACE = "grace"

class JobType(Enum):
    """
    Supported job types.
    """
    FIT = 'fit'
    INF = 'inf'
    DEEP = 'deep'
    SIM = 'sim'
    WATCH = 'watch'

class SlurmCluster(Enum):
    """
    Supported clusters.
    """
    SNELLIUS = 'snellius'
    HABROK = 'habrok'

class CommandsName(Enum):
    """
    Supported command names.
    """
    TF_GPU_TEST = 'tf_gpu_test.py'
    PYT_GPU_TEST = 'pyt_gpu_test.py'
    CONDA_PACE = 'conda_pace.sh'
    CONDA_MACE = 'conda_mace.sh'
    CONDA_GRACE = 'conda_grace.sh'
    MOD_MPI = 'module_mpi.sh'
    MOD_SIM = 'module_prop_sim.sh'
    MOD_MKL = 'module_mkl.sh'

def make_base_options(job: str, model: str, out_path: Path, slurm_opts: dict,
                      dependency: int | None = None) -> dict:
    """
    Make the base options for the job.
    """
    options = {
        'chdir': str(out_path),
        'job_name': f"{job}_{model}",
        'output': f"{str(out_path)}/{job}_%j.out",
        'error': f"{str(out_path)}/{job}_%j.err",
        **slurm_opts,
    }
    if dependency is not None:
        options['dependency'] = f"afterok:{dependency}"

    print("opt: ")
    print(options)

    return options

def make_array_options(job: str, model: str, out_path: Path,
                       slurm_opts: dict, array_ids: list[int],
                       dependency: int | None = None) -> dict:
    """
    Make the array options for the job.
    """
    out_job_path: str = f"{str(out_path)}/%a"
    return {
        **make_base_options(job, model, out_path, slurm_opts, dependency),
        'chdir': out_job_path,
        'output': f"{out_job_path}/{job}_%A_%a.out",
        'error': f"{out_job_path}/{job}_%A_%a.err",
        'array': array_ids,
    }

def get_slurm_options(cluster: str, job_type: str, out_path: Path,
                      model: str, slurm_opts: dict,
                      array_ids: list[int] | None = None,
                      dependency: int | None = None) -> dict:
    """
    Get the SLURM options for the job.
    """
    if job_type not in JobType._value2member_map_: # pylint: disable=protected-access
        raise ValueError(f"Job type {job_type} is not supported.")
    if model not in SupportedModel._value2member_map_: # pylint: disable=protected-access
        raise ValueError(f"Model {model} is not supported.")
    if cluster not in SlurmCluster._value2member_map_: # pylint: disable=protected-access
        raise ValueError(f"Cluster {cluster} is not supported.")

    if job_type == JobType.WATCH.value:
        return make_base_options(job_type, model, out_path, slurm_opts, dependency)

    if not array_ids:
        raise ValueError("Array ids must be provided for array jobs.")
    return make_array_options(job_type, model, out_path, slurm_opts, array_ids, dependency)
