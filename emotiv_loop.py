# braingerZone.py
# Objective: imitate research paper
from emokit import emotiv
import gevent

import copy
import time
import cPickle


sensor_names = ['F3', 'FC6', 'P7', 'T8', 'F7', 'F8', 'T7', 'P8', 'AF4',
                'F4', 'AF3', 'O2', 'O1', 'FC5', 'X', 'Y']


def emotiv_loop(processor, loop_data, extra_data, record_packets):
  headset = emotiv.Emotiv()

  gevent.spawn(headset.setup)
  gevent.sleep(0)
  # gevent.spawn(wait_for_user_input, state)
  packets = []
  alive, chosen = loop_data
  try:
    while alive.value:
      packet = headset.dequeue()
      if record_packets:
        data = processor.strip_data(packet, extra_data)
        packets.append(copy.deepcopy(data))

      if processor is not None:
        result = processor.process_frame(data)
        if result is not None:
          chosen.value = int(result)
  except KeyboardInterrupt:
    headset.close()
  finally:
    headset.close()
    if record_packets:
      fw = open('recording' + str(int(time.time())) + '.pickle', 'wb')
      cPickle.dump(packets, fw)
      fw.close()


def main():
  emotiv_loop(None, None, True)

if __name__ == "__main__":
  main()
