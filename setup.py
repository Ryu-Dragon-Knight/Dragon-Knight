try:
    import multiprocessing
except ImportError:
    pass

import setuptools

setuptools.setup(name='Dragon Knight',
                 setup_requires=['ryu>3.22'],
                 pbr=True)
