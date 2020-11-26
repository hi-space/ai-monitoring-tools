import time

def pdb_trace(func):

    def wrapper(*args, **kwargs):
        ret_values = None
        try:
            print('pdb (trace): %s' % func.__qualname__)
            ret_values = func(*args, **kwargs)
        except Exception as e:
            print(e)
            import pdb; pdb.set_trace()

        return ret_values

    return wrapper

def pdb_pm(func):

    def wrapper(*args, **kwargs):
        ret_values = None
        try:
            print('pdb (post_mortem): %s' % func.__qualname__)
            ret_values = func(*args, **kwargs)
        except Exception as e:
            print(e)
            import pdb; pdb.post_mortem()

        return ret_values

    return wrapper