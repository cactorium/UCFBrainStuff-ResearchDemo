# braingerZone.py
# Objective: imitate research paper
from emokit import emotiv
import gevent
import gevent.socket as gs

import matplotlib.pyplot as plt

import numpy as np
import scipy.signal as spsig
import sys

import time
import cPickle


sensor_names = ['F3', 'FC6', 'P7', 'T8', 'F7', 'F8', 'T7', 'P8', 'AF4',
                'F4', 'AF3', 'O2', 'O1', 'FC5', 'X', 'Y']


def calculate_eeg_val(packet):
  vld_vals = [packet.sensors[x]['value']
              for x in sensor_names if packet.sensors[x]['quality'] > 5]
  ref_avg = 0
  if len(vld_vals) > 0:
      ref_avg = sum(vld_vals)/float(len(vld_vals))
  # average the two visual cortex electrodes
  vld_data = [packet.sensors[x]['value'] for x in ['O1', 'O2'] if
              packet.sensors[x]['quality'] > 5]
  avg_val = 0.0
  if len(vld_data) > 0:
    avg_val = sum(vld_data)/float(len(vld_data))
    # ref_avg = 0

  # subtract general EEG activity to accentuate visual cortex activity
  return avg_val - ref_avg


def plot_fft(buf):
  f, fft = spsig.welch(buf, fs=128.0, nfft=512)
  print 'plot!'
  plt.clf()
  plt.plot(f, fft)
  plt.xlim([4, 20])
  plt.ylim([0, 120])
  # plt.ylim([0.5e-3, 1])
  plt.xlabel('frequency [Hz]')
  plt.ylabel('PSD [V**2/Hz]')
  # plt.specgram(fft_data, NFFT=256, Fs=128, noverlap=128)
  plt.draw()


class State(object):
  TRAINING = 0
  PROCESSING = 1
  WINDOW = 484
  NUM_CHANNELS = 16

  def __init__(self):
    self.state = State.TRAINING
    self.state = State.PROCESSING
    self.raw_buf = np.zeros((2*State.WINDOW))
    self.training_buf = np.zeros(0)
    self.idx = 0
    plt.ion()
    plt.show()

  def process_frame(self, packet, is_sync_frame, chosen_val):
    if self.state == State.TRAINING:
      self.training_buf = np.append(self.training_buf,
                                    [calculate_eeg_val(packet)])
      # print self.idx
      if self.idx % 256 == 255:
          print 'base line plot!'
          plot_fft(self.training_buf - self.training_buf.mean())
      self.idx = self.idx + 1
    elif self.state == State.PROCESSING:
      new_val = calculate_eeg_val(packet)

      # fancy buffering trick to make the ring buffer easier to manage
      # basically by putting it in two places, it makes it possible
      # to get the last WINDOW frames of data without having to combine
      # two slices
      self.raw_buf[self.idx] = new_val
      self.raw_buf[(self.idx+State.WINDOW) % (2*State.WINDOW)] = new_val

      fft_data_raw = self.raw_buf[self.idx+1:self.idx+State.WINDOW+1]
      # remove DC offset

      fft_data = fft_data_raw - fft_data_raw.mean()
      if self.idx % 64 == 0:
        plot_fft(fft_data)

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
