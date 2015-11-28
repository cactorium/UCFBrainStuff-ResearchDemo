# braingerZone.py
# Objective: imitate research paper
from emokit import emotiv
import gevent

import time
import cPickle


sensor_names = ['F3', 'FC6', 'P7', 'T8', 'F7', 'F8', 'T7', 'P8', 'AF4',
                'F4', 'AF3', 'O2', 'O1', 'FC5', 'X', 'Y']


def main():
  headset = emotiv.Emotiv()

  gevent.spawn(headset.setup)
  gevent.sleep(0)
  # gevent.spawn(wait_for_user_input, state)
  packets = []
  try:
    while True:
      packet = headset.dequeue()
      packets.append(packet)
  except KeyboardInterrupt:
    headset.close()
  finally:
    headset.close()
    fw = open('recording' + str(int(time.time())) + '.pickle', 'wb')
    cPickle.dump(packets, fw)
    fw.close()


if __name__ == "__main__":
  main()
