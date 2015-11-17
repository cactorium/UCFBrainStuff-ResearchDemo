# braingerZone.py
# Objective: imitate research paper
from emokit import emotiv
import gevent
import gevent.socket as gs

from sklearn.cross_decomposition import CCA

import numpy as np
import sys
import math

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


class State(object):
  TRAINING = 0
  PROCESSING = 1
  N_STIM_CYCLES = 10
  SEQUENCE_SIZE = int(63*128/60)  # 135
  NUM_FLASHERS = 16

  def __init__(self):
    self.state = State.TRAINING
    self.t_data = dict()  # dictionary of np_arrays
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

  def process_training_data(self):
    last_start = [f for f in self.t_sync_frames if
                  (f + State.SEQUENCE_SIZE) < self.seq_num][-1]
    last_end = sorted([f for f in self.t_sync_frames if f > last_start])[0]
    starts = [f for f in self.t_sync_frames if f < last_start]
    ends = [sorted([f for f in self.t_sync_frames if f > start])[0]
            for start in starts]
    frame_pairs = zip(starts, ends)
    print "Frame pairs: ", frame_pairs
    # find the most prominent channel
    best_channel, best_corr = None, None    # luckily None < all numbers
    for s in sensor_names:
      cur_set = self.t_data[s]
      # average across all the other frames
      avg = np.zeros(State.SEQUENCE_SIZE)
      for start, end in frame_pairs:
        tmp = resize_and_shift(cur_set[start:end], avg.size)
        avg = avg + tmp

      avg = avg * 1.0/len(frame_pairs)
      channel = resize_and_shift(cur_set[last_start:last_end], avg.size)
      channel_mag, avg_mag = np.dot(channel, channel), np.dot(avg, avg)
      cur_corr = np.dot(avg, channel)/math.sqrt(channel_mag, avg_mag)
      if cur_corr > best_corr:
        best_channel, best_corr = s, cur_corr

    print "Best channel %s with corr %f" % (best_channel, best_corr)
    # calculate CCA weights for it
    self.cca = CCA(n_components=1)
    x_t = np.zeros((len(sensor_names), State.SEQUENCE_SIZE*len(frame_pairs)))
    y_t = np.zeros((1, State.SEQUENCE_SIZE*len(frame_pairs)))
    # copy the data into an array for processing via CCA
    for idx, s in enumerate(sensor_names):
      for (f_idx, (s, e)) in enumerate(frame_pairs):
        s_idx, e_idx = f_idx*State.SEQUENCE_SIZE, (f_idx*1)*State.SEQUENCE_SIZE
        x_t[idx][s_idx:e_idx] = resize_and_shift(
            self.t_data[s][s:e], State.SEQUENCE_SIZE)
        if s == best_channel:
          y_t[s_idx:e_idx] = x_t[idx][s_idx:e_idx]

    x = x_t.transpose()
    y = y_t.transpose()
    self.cca.fit(x, y)
    print "CCA weights: "
    print self.cca.x_weights_
    # train OCSVM on dataset
    raise "I don't know what I'm doing!"

  def process_training(self, packet, is_sync_frame):
    if not is_sync_frame and not self.started:
      return
    if is_sync_frame:
      if not self.started:
        self.started = True
        self.seq_num = 0
        self.training_data = dict()

      self.t_sync_frames.extend(self.seq_num)
      if len(self.t_sync_frames) > State.N_STIM_CYCLES:
          self.state = State.PROCESSING
          self.process_training_data()
    for s in sensor_names:
      if self.seq_num >= self.t_data[s].size:
        self.t_data[s] = np.append(
            self.t_data[s], np.zeros(State.SEQUENCE_SIZE))
      self.t_data[s][self.seq_num] = packet.sensors[s]['value']

  def read_mind(self, packet, is_sync_frame):
      """
      #TODO TODO TODO --- make Processing begin indexed at 0 at first flash of
      # base flasher
      #In this same statement, check for flash 0 of base flasher
      if is_sync_frame:
        self.sequence_number = 0
      if self.sequence_number >= State.SEQUENCE_SIZE:
        self.sequence_number = 0

      self.processing_data[self.sequence_number] = packet.sensors['O1']['value']
      self.sequence_number += 1

      #now, find correlation coefficients for all 16 flashers.
      for x in range(0, State.NUM_FLASHERS):
        training_data_dot = np.dot(self.training_data, self.training_data)
        np.roll(self.training_data, -int(128/15*x))
        processing_data_dot = np.dot(self.processing_data, self.processing_data)
        training_processing_dot = np.dot(
            self.training_data, self.processing_data)
        self.corr_coeff[x] = training_processing_dot / math.sqrt(
            training_data_dot * processing_data_dot)
        #rotate array by 128/15 for the 4-frame lag, 16 times, recalculate each
        # time
        #TODO am I rolling in the right direction?
        np.roll(self.training_data, int(128/15*x))
      #Roll back to base frame
      print "max frame %d" % np.argmax(self.corr_coeff)
      """
      pass

  def process_frame(self, packet, is_sync_frame):
    self.seq_num = self.seq_num + 1
    # note: Only using one of these sensors. Either O1 or O2, as they're
    # closest to visual cortex.
    # Condition: status = training. Go through like ten flash cycles
    #       (10 seconds) and average cycle voltages (10 points to average for
    #       each of the 128 recordings)
    if self.state == State.TRAINING:
      self.process_training(self, packet, is_sync_frame)
    elif self.state == State.PROCESSING:
      self.read_mind(self, packet, is_sync_frame)

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


def emotiv_loop(is_sync_frame_int, is_alive_int):
  state = State()
  headset = emotiv.Emotiv()

  gevent.spawn(headset.setup)
  gevent.sleep(0)
  gevent.spawn(wait_for_user_input, state)
  try:
    while is_alive_int == 1:
      print is_sync_frame_int
      packet = headset.dequeue()
      state.process_frame(packet, is_sync_frame_int == 1)
  except KeyboardInterrupt:
    headset.close()
  finally:
    headset.close()


def main():
  state = State()
  headset = emotiv.Emotiv()

  gevent.spawn(headset.setup)
  gevent.sleep(0)
  gevent.spawn(wait_for_user_input, state)
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
