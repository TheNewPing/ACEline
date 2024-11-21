"""
CLI script for running PotLine.
"""

from argparse import Namespace, ArgumentParser
from pathlib import Path

from potline import PotLine

if __name__ == '__main__':
    def parse_args() -> Namespace:
        """
        Parse the command line arguments.
        """
        parser: ArgumentParser = ArgumentParser(description='Process some parameters.')
        parser.add_argument('--config', type=str, default='src/data/config.hjson',
                            help='Path to the config file')
        parser.add_argument('--iterations', type=int, default=1, help='Number of iterations')
        parser.add_argument('--nofitting', action='store_false', help='Disable potential fitting')
        parser.add_argument('--noconversion', action='store_false', help='Disable yace conversion')
        parser.add_argument('--noinference', action='store_false', help='Disable inference benchmark')
        parser.add_argument('--noproperties', action='store_false', help='Disable properties simulation')
        parser.add_argument('--nohpc', action='store_false', help='Disable HPC mode')
        parser.add_argument('--fitted', type=str, default=None, help='Path to the fitted potential')
        return parser.parse_args()

    args: Namespace = parse_args()

    potline = PotLine(Path(args.config),
                      args.iterations,
                      args.nofitting,
                      args.noconversion,
                      args.noinference,
                      args.noproperties,
                      args.nohpc,
                      Path(args.fitted) if args.fitted else None)

    potline.run_local()
