import numpy as np

import time

import braingerZone as bz

SPEED_UP = 8


class TestData(object):
  def __init__(self):
    self.sensors = dict()

  def populate(self, l):
    self.sensors = {s: {'value': l[idx]}
                    for (idx, s) in enumerate(bz.sensor_names)}


def main():
  test_state = bz.State()
  # slice off the first set, it's all zeros
  data = np.load("EEGsample1.npy")[0:]
  d_len, n_sensors = data.shape
  chosen = None
  for i in range(0, d_len):
    is_sync = i % 134 == 0
    new_packet = TestData()
    new_packet.populate(data[i])
    if is_sync:
      print "sync"
    test_state.process_frame(new_packet, i % 134 == 0, chosen)
    time.sleep(1.0/(SPEED_UP*128))

if __name__ == "__main__":
  main()
