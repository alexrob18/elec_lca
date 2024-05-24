import pandas as pd
import shutil
from pathlib import Path
import numpy as np
import json
import os
import sys
from math import log10, floor, ceil
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
import matplotlib as mpl
import matplotlib.gridspec as grid_spec
# from sklearn.neighbors import KernelDensity
# import seaborn as sns


def create_all_load_zone_image(
        df,
        output_dir,
        list_zone,
        chart_title,
        val_name,
        subplot_config=(4, 3),
        label_x="",
        label_y="",
        subplot_pre_title="",
        color="#440154FF",
        own_y_axis=False
):
    data = df.copy()

    fig = data.plot.line(x="period", y="value")
    fig.show


if __name__ == "__main__":
    df = pd.read_csv(r"C:\Users\RobertsonA\Documents\temp\results.csv")
    print(df)
