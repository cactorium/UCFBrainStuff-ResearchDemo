import processor

# braingerZone.py
# Objective: imitate research paper
import matplotlib.pyplot as plt

import numpy as np
import scipy.signal as spsig


sensor_names = ['F3', 'FC6', 'P7', 'T8', 'F7', 'F8', 'T7', 'P8', 'AF4',
                'F4', 'AF3', 'O2', 'O1', 'FC5', 'X', 'Y']


def calculate_eeg_val(packet):
  vld_vals = [packet.sensors[x]['value']
              for x in sensor_names] # if packet.sensors[x]['quality'] > 5]
  ref_avg = 0
  if len(vld_vals) > 0:
      ref_avg = sum(vld_vals)/float(len(vld_vals))
  # average the two visual cortex electrodes
  vld_data = [packet.sensors[x]['value'] for x in ['O1', 'O2']]# if
             # packet.sensors[x]['quality'] > 5]
  avg_val = 0.0
  if len(vld_data) > 0:
    avg_val = sum(vld_data)/float(len(vld_data))
    # ref_avg = 0

  # subtract general EEG activity to accentuate visual cortex activity
  return avg_val - ref_avg


def plot_fft(buf):
  f, fft = spsig.welch(buf, fs=128.0, nfft=512)
#  f, fft = spsig.welch(buf, fs=128.0)
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

TRAINING = 0
PROCESSING = 1
WINDOW = 384
NUM_CHANNELS = 16


class SsvepProcessor(processor.PacketProcessor):

  def __init__(self):
    self.state = TRAINING
    self.state = PROCESSING
    self.raw_buf = np.zeros((2*WINDOW))
    self.training_buf = np.zeros(0)
    self.idx = 0
    plt.ion()
    plt.show()

  def process_frame(self, data):
    packet = data
    if self.state == TRAINING:
      self.training_buf = np.append(self.training_buf,
                                    [calculate_eeg_val(packet)])
      # print self.idx
      if self.idx % 256 == 255:
          print 'base line plot!'
          plot_fft(self.training_buf - self.training_buf.mean())
      self.idx = self.idx + 1
    elif self.state == PROCESSING:
      new_val = calculate_eeg_val(packet)

      # fancy buffering trick to make the ring buffer easier to manage
      # basically by putting it in two places, it makes it possible
      # to get the last WINDOW frames of data without having to combine
      # two slices
      self.raw_buf[self.idx] = new_val
      self.raw_buf[(self.idx+WINDOW) % (2*WINDOW)] = new_val

      fft_data_raw = self.raw_buf[self.idx+1:self.idx+WINDOW+1]
      # remove DC offset

      fft_data = fft_data_raw - fft_data_raw.mean()
      if self.idx % 64 == 0:
        plot_fft(fft_data)

      self.idx = (self.idx + 1) % WINDOW

  def set_state(self, state):
    if state == PROCESSING:
      print "State changed to PROCESSING"
    else:
      print "State changed to TRAINING"

  def get_record_data(self, packet, extra_data):
    is_sync_frame = extra_data
    return packet, is_sync_frame
