"""
CLI entry point for running model conversion.
"""

from argparse import Namespace
from pathlib import Path

from potline.utils import parse_config, get_model_trackers, filter_best_loss
from potline.config_reader import ConfigReader

if __name__ == '__main__':
    args: Namespace = parse_config()
    config_path: Path = Path(args.config).resolve()
    opt_config = ConfigReader(config_path).get_optimizer_config()
    gen_config = ConfigReader(config_path).get_general_config()

    tracker_list = get_model_trackers(gen_config.sweep_path, gen_config.model_name)
    best_trackers = filter_best_loss(tracker_list, opt_config.energy_weight, gen_config.best_n_models)

    for tracker in best_trackers:
        tracker.model.lampify()
        tracker.model.create_potential()
