from ctypes import Array
import multiprocessing
from multiprocessing import shared_memory
from multiprocessing.managers import SyncManager

import numpy as np
import constants


class SharedMemoryManager():
    def __init__(self):
        array_size = constants.TT_SIZE

        self.shm_tt_killers = shared_memory.SharedMemory(create=True, size=array_size*np.uint64().itemsize)
        self.tt_killers = np.ndarray((array_size,), dtype=np.uint64, buffer=self.shm_tt_killers.buf)
        self.tt_killers.fill(0)

        self.shm_tt_scores = shared_memory.SharedMemory(create=True, size=array_size*np.uint64().itemsize)
        self.tt_scores = np.ndarray((array_size,), dtype=np.uint64, buffer=self.shm_tt_scores.buf)
        self.tt_scores.fill(0)

        self.shm_process_status = shared_memory.SharedMemory(create=True, size=constants.PROCESS_COUNT*np.int16().itemsize)
        self.process_status = np.ndarray((constants.PROCESS_COUNT,), dtype=np.int16, buffer=self.shm_process_status.buf)
        self.process_status.fill(0)


    def reset_tables(self):
        self.process_status.fill(0)
        self.tt_killers.fill(0)
        self.tt_scores.fill(0)

    def close(self):
        self.shm_tt_killers.close()
        self.shm_tt_killers.unlink()
        self.shm_tt_scores.close()
        self.shm_tt_scores.unlink()
        self.shm_process_status.close()
        self.shm_process_status.unlink()