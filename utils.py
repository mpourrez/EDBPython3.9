import time
import numpy as np
from scipy import stats

image_dataset_directory = "workloads/coco-dataset-val2017"  # image dataset (coco)

def current_milli_time():
    return round(time.time() * 1000)

def get_avg_without_outlier(data_list):
    # return sum(data_list) / len(data_list)
    if np.std(data_list) == 0:
        return sum(data_list) / len(data_list)
    z = np.abs(stats.zscore(data_list))
    avg = 0
    count = 0
    for i in range(0, len(data_list)):
        if z[i] > -3 and z[i] < 3:
            avg += data_list[i]
            count += 1
        else:
            print("This is outlier: {}".format(data_list[i]))
    if count == 0:
        return 0
    return avg / count


def get_std_without_outlier(data_list):
    if len(data_list) == 0:
        return 0
    if np.std(data_list) == 0:
        return sum(data_list) / len(data_list)
    z = np.abs(stats.zscore(data_list))
    avg = 0
    count = 0
    list_without_outliers = []
    for i in range(0, len(data_list)):
        if z[i] > -3 and z[i] < 3:
            list_without_outliers.append(data_list[i])
            count += 1
        else:
            print("This is outlier: {}".format(data_list[i]))

    a = 1.0 * np.array(list_without_outliers)
    n = len(a)
    m, se = np.mean(a), stats.sem(a)
    h = se * stats.t.ppf((1 + 0.95) / 2., n - 1)
    return h