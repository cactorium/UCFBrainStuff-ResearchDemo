# braingerZone.py
# Objective: imitate research paper
from emokit import emotiv
import gevent
import gevent.socket as gs

import numpy as np
import scipy.signal as spsig
import sys


class State(object):
  TRAINING = 0
  PROCESSING = 1
  WINDOw = 384
  NUM_CHANNELS = 16

  def __init__(self):
    # self.state = State.TRAINING
    self.state = State.PROCESSING
    self.raw_buf = np.zeros((2*State.WINDOW))
    self.idx = 0

  def process_frame(self, packet, is_sync_frame, chosen_val):
    sensor_names = ['F3', 'FC6', 'P7', 'T8', 'F7', 'F8', 'T7', 'P8', 'AF4',
                    'F4', 'AF3', 'O2', 'O1', 'FC5', 'X', 'Y']

    if self.state == State.TRAINING:
      pass
    elif self.state == State.PROCESSING:
      ref_avg = sum([packet.sensors[x]['value']
                     for x in sensor_names])/len(sensor_names)
      # average the two visual cortex electrodes
      avg_val = sum([packet.sensors[x]['value'] for x in ['O1', 'O2']])/2.0

      # subtract general EEG activity to accentuate visual cortex activity
      new_val = avg_val - ref_avg

      # fancy buffering trick to make the ring buffer easier to manage
      # basically by putting it in two places, it makes it possible
      # to get the last WINDOW frames of data without having to combine
      # two slices
      self.raw_buf[self.idx] = new_val
      self.raw_buf[(self.idx+State.WINDOW) % (2*State.WINDOW)] = new_val

      fft_data_raw = self.raw_buf[self.idx+1:self.idx+State.WINDOW+1]
      # remove DC offset
      fft_data = fft_data_raw - fft_data_raw.mean()
      fft = spsig.welch(fft_data, 128.0)
      print fft

      pass

    self.idx = (self.idx + 1) % State.WINDOW

  def set_state(self, state):
    if state == State.PROCESSING:
      print "State changed to PROCESSING"
    else:
      print "State changed to TRAINING"


def wait_for_user_input(state):
  while True:
    gs.wait_read(sys.stdin.fileno())
    ln = sys.stdin.readline()
    if ln.find('P') != -1:
      state.set_state(State.PROCESSING)
    elif ln.find('T') != -1:
      state.set_state(State.TRAINING)


def emotiv_loop(is_sync_frame_int, is_alive_int, chosen_val):
  state = State()
  headset = emotiv.Emotiv()

  state = State()
  gevent.spawn(headset.setup)
  gevent.sleep(0)
  gevent.spawn(wait_for_user_input, state)
  try:
    while is_alive_int.value == 1:
      packet = headset.dequeue()
      if (is_sync_frame_int.value == 1):
        state.process_frame(packet, True, chosen_val)
        is_sync_frame_int.value = 0
      else:
        state.process_frame(packet, False, chosen_val)
  except KeyboardInterrupt:
    headset.close()
  finally:
    headset.close()


def main():
  state = State()
  headset = emotiv.Emotiv()

  gevent.spawn(headset.setup)
  gevent.sleep(0)
  # gevent.spawn(wait_for_user_input, state)
  try:
    while True:
      packet = headset.dequeue()
      state.process_frame(packet)
  except KeyboardInterrupt:
    headset.close()
  finally:
    headset.close()


if __name__ == "__main__":
  main()
