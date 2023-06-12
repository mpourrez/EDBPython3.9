import matplotlib.pyplot as plt
from app_statistics import *

def draw_fault_free_resource_comparisons():
    app_statistics = {}
    apps = ['FFT', 'FPO-SIN']
        # , 'FPO-SQRT', 'SORT', 'DD', 'IPERF',
        #     'IP', 'SA', 'ST', 'IC-A-CPU', 'IC-S-CPU', 'OD-CPU', 'PS', 'AE']

    for app in apps:
        app_stat = AppFaultStatistics(app, 'No-Fault')
        app_statistics[app] = app_stat.get_resource_summary_matrix()

    fig, ax = plt.subplots()

    for app in apps:
        summary_matrix = app_statistics[app]
        cpu_users = []
        times = []
        index = 0
        for key in summary_matrix.keys():
            value = summary_matrix[key]
            cpu_users.append(value.cpu_user)
            times.append(index)
            index += 1
        ax.plot(times, cpu_users, label=app)

    plt.show()


if __name__ == '__main__':
    # app_fault_statistics = AppFaultStatistics('AE', 'CTXS-10000')
    # app_fault_statistics.plot_resource_with_residual('CPU', 'SYS', show_injection_times=False)
    # draw_fault_free_comparisons()
    # app_statistic = AppStatistics('AE')
    draw_fault_free_resource_comparisons()
