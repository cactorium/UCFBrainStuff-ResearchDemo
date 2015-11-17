# braingerZone.py
# Objective: imitate research paper
from emokit import emotiv
import gevent
import gevent.socket as gs

import numpy as np
import sys
# import math

sensor_names = ['F3', 'FC6', 'P7', 'T8', 'F7', 'F8', 'T7', 'P8', 'AF4',
                'F4', 'AF3', 'O2', 'O1', 'FC5', 'X', 'Y']


class State(object):
  TRAINING = 0
  PROCESSING = 1
  N_STIM_CYCLES = 10
  SEQUENCE_SIZE = int(63*128/60)+1  # 135
  NUM_FLASHERS = 16

  def __init__(self):
    self.state = State.TRAINING
    self.t_data = dict()  # dictionary of np_arrays
    self.t_sync_frames = []
    self.p_data = dict()  # np.zeros((State.SEQUENCE_SIZE))
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

  def process_training_data(self):
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
