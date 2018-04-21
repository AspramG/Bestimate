import matplotlib.pyplot as plt
import numpy as np
import sys

from utilities import load_data
from utilities.constants import *

def show_histogram(dataset):

    filename = get_filtered_dataset_filename(dataset)
    data = load_data.load_json(filename)

    if data is None:
        return

    y = [datapoint[TIMESPENT_FIELD_KEY] / SECONDS_IN_HOUR for datapoint in data]

    max_hours = int(input("Please input the maximum number of hours to display in the histogram: "))

    plt.figure(figsize=(12, 7))
    plt.hist(y, bins = max_hours * 12, range = (0, max_hours - 1 / SECONDS_IN_HOUR))
    plt.xticks(np.arange(0, max_hours + 1, 1))
    plt.xlim(0, max_hours)
    plt.xlabel("Time spent, hours")
    plt.ylabel("Number of records")

    load_data.create_folder_if_needed(STATISTICS_FOLDER)
    filename = get_statistics_image_filename(dataset, LABEL_DISTRIBUTION_STAT)
    plt.savefig(filename, bbox_inches=PLOT_BBOX_INCHES)

    print("Label distribution histogram saved at %s" % filename)

show_histogram(sys.argv[1])