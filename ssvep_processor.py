import processor

# braingerZone.py
# Objective: imitate research paper
import matplotlib.pyplot as plt

import numpy as np
import scipy.signal as spsig


sensor_names = ['F3', 'FC6', 'P7', 'T8', 'F7', 'F8', 'T7', 'P8', 'AF4',
                'F4', 'AF3', 'O2', 'O1', 'FC5', 'X', 'Y']

SD_FORWARD = 0
SD_BACKWARD = 1
SD_RIGHT = 2
SD_LEFT = 3
SD_NEUTRAL = 4

FFT_THRESHOLD = 15 #Because why not
COMMAND_THRESHOLD = 5 #4 Consecutive wins and we're gonna send it

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
  #print 'plot!'
  '''
  seconds = fft[0::2]
  thirds = fft[0::3]
  fourths = fft[0::4]
  seconds = np.append(seconds, np.zeros(fft.size - seconds.size))
  thirds = np.append(thirds, np.zeros(fft.size - thirds.size))
  fourths = np.append(fourths, np.zeros(fft.size - fourths.size))
  '''
  # fft = fft + seconds/2 + thirds/4 + fourths/8
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
    self.validCommandCount = 0
    self.currWinner = SD_NEUTRAL
    self.prevWinner = SD_NEUTRAL
    self.commands = [SD_FORWARD, SD_BACKWARD, SD_RIGHT, SD_LEFT ]
    #self.bucketsFor8Hz = [ 7.75, 8, 8.25 ]
    #self.bucketsFor10Hz = [ 9.75, 10, 10.25 ]
    #self.bucketsFor12Hz = [ 11.75, 12, 12.25 ]
    #self.bucketsFor14Hz = [ 13.75, 14, 14.25 ]
    self.bucketsFor8Hz = [ 7.25, 7.5, 7.75, 8, 8.25, 8.5, 8.75 ]
    self.bucketsFor10Hz = [ 9.25, 9.5, 9.75, 10, 10.25, 10.5, 10.75 ]
    self.bucketsFor12Hz = [ 11.25, 11.5, 11.75, 12, 12.25, 12.5, 12.75 ]
    self.bucketsFor14Hz = [ 13.25, 13.5, 13.75, 14, 14.25, 14.5, 14.75 ]
    plt.ion()
    plt.show()

  def calculatePeaks(self, f, fft):
    scores = [0,0,0,0]
    scoresValid = False

    #Calculate the Scores for Each Frequency
    scores[SD_FORWARD] = self.calculateScore(f, fft, self.bucketsFor8Hz  , 1.0)
    scores[SD_BACKWARD] = self.calculateScore(f, fft, self.bucketsFor10Hz, 1.05)
    scores[SD_LEFT] = self.calculateScore(f, fft, self.bucketsFor12Hz    , 1.1)
    scores[SD_RIGHT] = self.calculateScore(f, fft, self.bucketsFor14Hz   , 1.15)

    #Return the Best Score
    for i in scores:
        if (i > 0):
            scoresValid = True

    if (scoresValid):
        print "Scores = ", scores
        return scores.index(max(scores))
    else:
        return SD_NEUTRAL

  def calculateScore(self, f, fft, buckets, handicap):
    valuesUsed = 0
    tmpList = [0] * len(buckets)
    avgFftVal = 0

    #Find FFT Values
    for i in buckets:
        if (i in f):
            indx1 = buckets.index(i)
            indx2 = f.index(i)
            tmpList[indx1] = fft[indx2]

    #Average the values in the bucket
    for i in tmpList:
        if ( i > (FFT_THRESHOLD / handicap)):
            avgFftVal = avgFftVal + i
            valuesUsed = valuesUsed + 1

    if (valuesUsed == 0):
        return 0
    else:
        avgFftVal = avgFftVal / valuesUsed

    #Calculate Score
    if (avgFftVal > (FFT_THRESHOLD / handicap)):
        score = avgFftVal - (FFT_THRESHOLD / handicap)
    else:
        score = 0

    return score

  def process_frame(self, data):
    retVal = SD_NEUTRAL
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
      if self.idx % 32 == 0:
        plot_fft(fft_data)
        f, fft = spsig.welch(fft_data, fs=128.0, nfft=512)
        winner = self.calculatePeaks(f.tolist(), fft.tolist())
        if (not winner == SD_NEUTRAL):
            print "WINNER = ", winner
            self.currWinner = winner

            if (self.prevWinner == self.currWinner):
                self.validCommandCount = self.validCommandCount + 1
            else:
                self.validCommandCount = 0

            if (self.validCommandCount >= COMMAND_THRESHOLD):
                print "SENDING COMMAND", [8,10,12,14][winner]
                retVal = winner

            self.prevWinner = self.currWinner
        else:
            print "WINNER = NEUTRAL"

      self.idx = (self.idx + 1) % WINDOW
      return retVal

  def set_state(self, state):
    if state == PROCESSING:
      print "State changed to PROCESSING"
    else:
      print "State changed to TRAINING"

  def get_record_data(self, packet, extra_data):
    is_sync_frame = extra_data
    return packet, is_sync_frame
