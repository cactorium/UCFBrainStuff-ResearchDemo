import processor

# braingerZone.py
# Objective: imitate research paper

from sklearn.cross_decomposition import CCA

import numpy as np
# import math

sensor_names = ['F3', 'FC6', 'P7', 'T8', 'F7', 'F8', 'T7', 'P8', 'AF4',
                'F4', 'AF3', 'O2', 'O1', 'FC5', 'X', 'Y']


def resize_and_shift(in_vec, sz):
  tmp = in_vec
  if tmp.size < sz:
    tmp = tmp - tmp.mean()
    tmp = np.append(tmp, np.zeros(sz - tmp.size))
  elif tmp.size > sz:
    tmp = tmp[0:sz]
    tmp = tmp - tmp.mean()
  else:
    tmp = tmp - tmp.mean()
  return tmp

TRAINING = 0
PROCESSING = 1
N_STIM_CYCLES = 9  # 200
SEQUENCE_SIZE = 134
NUM_FLASHERS = 16
NUM_CHANNELS = 16


# TODO: detect positive edge of sync_frame, to get actual sync_frame
class CvepProcessor(processor.PacketProcessor):
  def __init__(self):
    self.state = TRAINING
    self.t_data = {s: np.zeros(0) for s in sensor_names}
    self.t_sync_frames = []
    self.p_data = np.zeros(shape=(len(sensor_names), 0))
    self.p_sync_frames = []
    # self.corr_coeff --- probably only needs to only equal the
    # number of flashing squares???
    # self.corr_coeff = np.zeros((State.NUM_FLASHERS))
    # sequence_number - in training template, counter to indicate
    # which frame the base flasher is on
    # self.sequence_number = 0
    # sequence_iteration --- used for training template. counter to tell
    # how many cycles have been recorded for testing.
    # self.sequence_iteration = 0
    self.started = False
    self.seq_num = -1
    self.cca = None

    self.cca_template = None
    self.old_sync = False
    self.real_sync = False

  def process_training_data(self):
    last_start = [f for f in self.t_sync_frames if
                  (f + SEQUENCE_SIZE) < self.seq_num][-1]
    # last_end = sorted([f for f in self.t_sync_frames if f > last_start])[0]
    starts = [f for f in self.t_sync_frames if f <= last_start]
    ends = [sorted([f for f in self.t_sync_frames if f > start])[0]
            for start in starts]
    frame_pairs = zip(starts, ends)
    print "Frame pairs: ", frame_pairs
    # calculate CCA weights for it
    self.cca = CCA(n_components=1)
    x_t = np.zeros((len(sensor_names), SEQUENCE_SIZE*len(frame_pairs)))
    y_t = np.zeros((len(sensor_names), SEQUENCE_SIZE*len(frame_pairs)))
    # copy the data into an array for processing via CCA
    for idx, s in enumerate(sensor_names):
      for (f_idx, (st, ed)) in enumerate(frame_pairs):
        s_idx, e_idx = f_idx*SEQUENCE_SIZE, (f_idx+1)*SEQUENCE_SIZE
        x_t[idx][s_idx:e_idx] = resize_and_shift(
            self.t_data[s][st:ed], SEQUENCE_SIZE)
      x_avg = x_t[idx].reshape((SEQUENCE_SIZE, -1)).mean(1)
      y_t[idx] = np.tile(x_avg, len(frame_pairs))
      x_mag = np.dot(x_t[idx], x_t[idx])
      y_mag = np.dot(y_t[idx], y_t[idx])
      if x_mag != 0 and y_mag != 0:
        s_corr = np.dot(y_t[idx], x_t[idx])/(np.sqrt(x_mag * y_mag))
        print "%s correlation: %f" % (s, s_corr)
      else:
        print "%s no data" % s

    x = x_t.transpose()
    y = y_t.transpose()
    # print x.shape, y.shape
    self.cca.fit(x, y)
    print "CCA weights: "
    print self.cca.x_weights_

    cca_channel = self.cca.transform(x).flatten()
    self.cca_templ = cca_channel.reshape(
        (SEQUENCE_SIZE, len(frame_pairs))).mean(axis=1)
    cca_avg = np.tile(self.cca_templ, len(frame_pairs))
    cca_avg_mag = np.dot(cca_avg, cca_avg)

    cca_channel_mag = np.dot(cca_channel, cca_channel)

    cca_self_corr = np.dot(cca_channel, cca_avg)/(np.sqrt(
        np.multiply(cca_channel_mag, cca_avg_mag)))
    print "cca channel self corr: ", cca_self_corr
    #  train OCSVM on dataset
    raise TypeError("I don't know what I'm doing!")
    return cca_channel

  def process_training(self, data):
    packet, is_sync_frame = data
    if not is_sync_frame and not self.started:
      return
    if is_sync_frame:
      if not self.started:
        self.started = True
        self.seq_num = 0
        self.t_data = {s: np.zeros(0) for s in sensor_names}

      self.t_sync_frames.append(self.seq_num)
      if len(self.t_sync_frames) > N_STIM_CYCLES + 1:
          self.state = PROCESSING
          self.process_training_data()
    for s in sensor_names:
      if self.seq_num >= self.t_data[s].size:
        self.t_data[s] = np.append(
            self.t_data[s], np.zeros(SEQUENCE_SIZE))
      self.t_data[s][self.seq_num] = packet.sensors[s]['value']

  def read_mind(self, data):
      pass

  def process_frame(self, data):
    _, is_sync_frame = data
    self.real_sync = ((not self.old_sync) and is_sync_frame)
    self.old_sync = is_sync_frame
    if self.real_sync:
      print("sync")

    self.seq_num = self.seq_num + 1
    if self.state == TRAINING:
      return self.process_training(data)
    elif self.state == PROCESSING:
      return self.read_mind(data)

  def set_state(self, state):
    if state == PROCESSING:
      print "State changed to PROCESSING"
    else:
      print "State changed to TRAINING"

  def strip_data(self, packet, extra_data):
    is_sync_frame = extra_data
    return packet, is_sync_frame.value
