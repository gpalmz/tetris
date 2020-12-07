import json

import click

from tetris.model.hyperparameters import tune_move_selector_params
from common.util.np import NumpyJsonEncoder


@click.command()
@click.option("--iter-count", default=20, help="Number of iterations or (sets of parameters attempted) of random hyperparameter search; larger values will return more accurate yet slower results.")
@click.option("--sample-count", default=50, help="Number of samples tried per each hyperparameter set; larger values will return more accurate yet slower results. Must be greater than 5.")
@click.option("--path", default="../config/params.json", help="Output file for new params in JSON format.")
def tune(iter_count, sample_count, path):
    with open(path, "w") as f:
        json.dump(tune_move_selector_params(iter_count, sample_count), f, cls=NumpyJsonEncoder)
        


if __name__ == "__main__":
    tune()