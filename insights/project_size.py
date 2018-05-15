import math
import matplotlib.pyplot as plt
import numpy as np
import sys

from preprocess import projects
from utilities import load_data
from utilities.constants import *

def show_histogram(dataset):

    filename = get_filtered_dataset_filename(dataset)
    data = load_data.load_json(filename)

    if data is None:
        return

    project_issue_counts = projects.get_issue_counts(data)
    issue_counts = [c[1] for c in project_issue_counts]
    
    min_size = min(issue_counts)
    max_size = max(issue_counts)

    need_upper_limit = input("Would you like to put a constraint on the maximum project size displayed? (y/n) ") == "y"
    if need_upper_limit:
        upper_limit = int(input("Please enter the upper project size limit: "))

    if need_upper_limit:
        max_size = min(upper_limit, max_size)

    suggested_number_of_bins = [i for i in range(5, 30) if (max_size - min_size) % i == 0]
    print("Suggested number of bins is:", *suggested_number_of_bins)
    bins = int(input("Please input the number of bins: "))

    plt.figure(figsize=(12, 7))
    plt.hist(issue_counts, bins = bins, range = (min_size, max_size))
    step = (max_size - min_size) / bins
    plt.xticks(np.arange(min_size, max_size + 1, step))
    plt.xlim(min_size, max_size)
    plt.xlabel("Number of issues in project")
    plt.ylabel("Number of projects")

    load_data.create_folder_if_needed(STATISTICS_FOLDER)
    filename = get_statistics_image_filename(dataset, PROJECT_SIZE_STAT)
    plt.savefig(filename, bbox_inches=PLOT_BBOX_INCHES)

    print("Project size histogram saved at %s" % filename)

show_histogram(sys.argv[1])