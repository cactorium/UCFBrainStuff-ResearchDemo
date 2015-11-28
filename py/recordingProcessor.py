# braingerZone.py
# Objective: imitate research paper
from emokit import emotiv
import gevent
import gevent.socket as gs

import matplotlib.pyplot as plt

import numpy as np
import scipy.signal as spsig
import sys

import copy
import time
import cPickle


def emotiv_loop(is_sync_frame_int, is_alive_int, chosen_val):
  headset = emotiv.Emotiv()

  gevent.spawn(headset.setup)
  gevent.sleep(0)
  packets = []
  seq_num = 0
  try:
    while is_alive_int.value == 1:
      packet = headset.dequeue()
      packets.append(copy.deepcopy(packet))
      print seq_num
      seq_num = seq_num + 1
  except KeyboardInterrupt:
    headset.close()
  finally:
    headset.close()
    fw = open('recording' + str(int(time.time())) + '.pickle', 'wb')
    cPickle.dump(packets, fw)
    fw.close()


def main():
  state = State()
  headset = emotiv.Emotiv()

  gevent.spawn(headset.setup)
  gevent.sleep(0)
  # gevent.spawn(wait_for_user_input, state)
  packets = []
  try:
    while True:
      packet = headset.dequeue()
      packets.append(packet)
      state.process_frame(packet)
  except KeyboardInterrupt:
    headset.close()
  finally:
    headset.close()
    fw = open('recording' + str(int(time.time())) + '.pickle', 'wb')
    cPickle.dump(packets, fw)
    fw.close()


if __name__ == "__main__":
  main()
