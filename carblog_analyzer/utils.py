import os

def check_dir(path):
    """
    It checks whether directory of input path is exists.
    If not, it creates directory

    Arguments
    ---------
    path : file path
    """
    dirname = os.path.dirname(os.path.abspath(path))
    if not os.path.exists(dirname):
        os.makedirs(dirname)
        print('Created {}'.format(dirname))
