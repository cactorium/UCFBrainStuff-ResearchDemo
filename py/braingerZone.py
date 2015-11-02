#braingerZone.py
#Objective: imitate research paper
from emokit import emotiv
import gevent
import gevent.socket as gs

import numpy as np
import sys
import math


class State(object):
  TRAINING = 0
  PROCESSING = 1
  N_STIM_CYCLES = 10
  SEQUENCE_SIZE = 128
  NUM_FLASHERS = 16

  def __init__(self):
    self.state = State.TRAINING
    self.training_data = np.zeroes((State.SEQUENCE_SIZE))
    self.processing_data = np.zeroes((State.SEQUENCE_SIZE))
    #self.corr_coeff --- probably only needs to only equal the number of flashing squares???
    self.corr_coeff = np.zeros((State.NUM_FLASHERS))
    #sequence_number - in training template, counter to indicate which frame the base flasher is on
    self.sequence_number = 0
    #sequence_iteration --- used for training template. counter to tell
    #how many cycles have been recorded for testing.
    self.sequence_iteration = 0

  def process_frame(self, packet):

    #note: Only using one of these sensors. Either O1 or O2, as they're closest to visual cortex.
    #sensor_names = ['F3', 'FC6', 'P7', 'T8', 'F7', 'F8', 'T7', 'P8', 'AF4', 'F4',
    #                'AF3', 'O2', 'O1', 'FC5', 'X', 'Y']

    #Condition: status = training. Go through like ten flash cycles (10 seconds) and average
    #           cycle voltages (10 points to average for each of the 128 recordings)
    if self.state == State.TRAINING:
      #TODO TODO TODO --- make Training begin at first flash of base flasher
      if self.sequence_number < State.SEQUENCE_SIZE:
        #add latest voltage value to proper index of training_data array
        #TODO: make sure packet.sensors['01']['value'] is getting the one voltage I need
        self.training_data[self.sequence_number] += packet.sensors['O1']['value']
        self.sequence_number += 1
      #case: reached the end of a 1-second cycle. If that wasn't the 10th cycle,
      #      start another cycle.
      #TODO: make sure we're starting at the
      #same time as the beginning of a flash sequence for the test. If the timing is off,
      #wait for the next flash 0 of the base flasher.
      #TODO TODO TODO --- make Training begin at first flash of base flasher
      elif self.sequence_iteration < State.N_STIM_CYCLES:
        self.sequence_number = 0
        self.sequence_iteration += 1
        self.training_data[self.sequence_number] += packet.sensors['O1']['value']
        self.sequence_number += 1

      #if you get here, you've recorded 10 cycles. Time to end training.
      else:
        self.sequence_number = 0
        self.sequence_iteration = 0
        #Finish the averaging by dividing by 10
        self.training_data /= State.N_STIM_CYCLES
        #Switch to processing mode!
        self.state = State.PROCESSING

    #condition: status = processing. TODO: Every time the base flasher cycles to zero, make
    #           sure that the refreshing processing template is indexed at 0 then.
    elif self.state == State.PROCESSING:
      #TODO TODO TODO --- make Processing begin indexed at 0 at first flash of base flasher
      #In this same statement, check for flash 0 of base flasher
      if self.sequence_number >= State.SEQUENCE_SIZE:
        self.sequence_number = 0

      self.processing_data[self.sequence_number] = packet.sensors['O1']['value']
      self.sequence_number += 1

      #now, find correlation coefficients for all 16 flashers.
      #NOTE: maybe make sure the array is filled and still filling first?
      for x in range(0, State.NUM_FLASHERS):
        training_data_dot = np.dot(self.training_data, self.training_data)
        processing_data_dot = np.dot(self.processing_data, self.processing_data)
        training_processing_dot = np.dot(self.training_data, self.processing_data)
        self.corr_coeff[x] = training_processing_dot / math.sqrt(
            training_data_dot * processing_data_dot)
        #rotate array by 3 for the 3-frame lag, 16 times, recalculate each time
        #TODO am I rolling in the right direction?
        np.roll(self.training_data, -3)
      #Roll back to base frame
      np.roll(self.training_data, 48)

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
      gevent.sleep(0)
  except KeyboardInterrupt:
    headset.close()
  finally:
    headset.close()


if __name__ == "__main__":
  main()
