import time

profiled_mean_api_exec_time = {}

class ProfileInfo():

    def __init__(self, mean_exec_time, api_call_count):
        self.mean_exec_time = mean_exec_time
        self.api_call_count = api_call_count 

def time_profiler(func, time_taken_filter=1e-4):

    def wrapper(*args, **kwargs):
        t1 = time.time()
        ret_values = func(*args, **kwargs)
        t2 = time.time()
        time_taken = t2 - t1
        if time_taken > time_taken_filter:
            if func.__qualname__ not in profiled_mean_api_exec_time:
                profiled_mean_api_exec_time[func.__qualname__] = ProfileInfo(t2 - t1, 1)
            else:
                profiled_mean_api_exec_time[func.__qualname__].api_call_count += 1
                N = profiled_mean_api_exec_time[func.__qualname__].api_call_count
                profiled_mean_api_exec_time[func.__qualname__].mean_exec_time = profiled_mean_api_exec_time[func.__qualname__].mean_exec_time * (N - 1) / N + (t2 - t1) / N
            # print(func.__qualname__, '-->', t2-t1, 's')

        return ret_values

    return wrapper

def exit_and_show_profiled_results(app):
    print('[*] mean API execution time')
    for api_func_name, profile_info in profiled_mean_api_exec_time.items():
        print('Function: %s' % api_func_name)
        print('\___ mean exec time: %.5f seconds' % profile_info.mean_exec_time)

    import sys; sys.exit()

def register_time_profiler_and_exec(app):

    import signal; signal.signal(signal.SIGINT, lambda signal, frame: exit_and_show_profiled_results(app))

    app.exec_()