# braingerZone.py
# Objective: imitate research paper
from emokit import emotiv
import gevent

import time
import cPickle


def emotiv_loop(is_sync_frame_int, is_alive_int, chosen_val):
  headset = emotiv.Emotiv()

  gevent.spawn(headset.setup)
  gevent.sleep(0)
  packets = []
  sync_frames = []
  seq_num = 0
  try:
    while is_alive_int.value == 1:
      packet = headset.dequeue()
      packets.append(packet)
      if is_sync_frame_int.value == 1:
        print "sync"
        sync_frames.append(seq_num)
        is_sync_frame_int.value = 0
  except KeyboardInterrupt:
    headset.close()
  finally:
    headset.close()
    fw = open('recording' + str(int(time.time())) + '.pickle', 'wb')
    cPickle.dump((packets, sync_frames), fw)
    fw.close()


def main():
  headset = emotiv.Emotiv()

  gevent.spawn(headset.setup)
  gevent.sleep(0)
  try:
    while True:
      packet = headset.dequeue()
      print packet
  except KeyboardInterrupt:
    headset.close()
  finally:
    headset.close()


if __name__ == "__main__":
  main()
