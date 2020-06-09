import threading
import h5py
import numpy as np

ochlv_type = np.dtype(
    [('timestamp', 'uint64'), ('open', 'float_'), ('high', 'float_'), ('low', 'float_'), ('close', 'float_'),
     ('volume', 'float_')])

class File(h5py.File):

    def __init__(self, name,  mode=None, driver=None,
                 libver=None, userblock_size=None, swmr=False,
                 rdcc_nslots=None, rdcc_nbytes=None, rdcc_w0=None,
                 track_order=None,
                 **kwds):
        h5py.File.__init__(self, name, mode=mode, swmr=swmr, libver='latest')

    # def close(self):
    #     pass

    def destroy(self):
        super().close()

    def create_dataset(self, name='ohlcv', shape=None, dtype=ochlv_type, data=None):
        if not self.get('ohlcv'):
            super().create_dataset(name, shape=shape, dtype=dtype, data=data)

    def get_create_ohlcv(self, freq):
        if not self.get('ohlcv'):
            if freq == '1d':
                self.create_dataset(shape=(366,))
            if freq == '1m':
                self.create_dataset(shape=(366 * 1440,))
            if freq == '5m':
                self.create_dataset(shape=(366 * 288,))
            if freq in ['60min','1h']:
                self.create_dataset(shape=(366 * 24,))

        return self.get('ohlcv')

    def get_ohlcv(self):
        return self.get('ohlcv')
