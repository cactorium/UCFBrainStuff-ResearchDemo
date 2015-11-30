import zmq

from emotiv_loop import emotiv_loop
import ssvep_processor

import seniordesign_pb2 as sd


def wrap_cmd(tp):
  d, confidence = tp, 1.0
  ret = sd.ProcessingResults()
  ret.confidence = confidence
  if d == ssvep_processor.SD_BACKWARD:
    ret.direction = sd.SD_BACKWARD
  elif d == ssvep_processor.SD_FORWARD:
    ret.direction = sd.SD_FORWARD
  elif d == ssvep_processor.SD_LEFT:
    ret.direction = sd.SD_LEFT
  elif d == ssvep_processor.SD_RIGHT:
    ret.direction = sd.SD_RIGHT
  elif d == ssvep_processor.SD_NEUTRAL:
    ret.direction = sd.SD_NEUTRAL
  else:
    ret.direction = sd.SD_NEUTRAL
  return ret


class MockData(object):
  def __init__(self, val):
    self.value = val


def main():
  context = zmq.Context()
  socket = context.socket(zmq.PUB)
  socket.bind('tcp://127.0.0.1:9000')

  # NOTE: This doesn't correctly work because the process_frame doesn't
  # currently return values. To be fixed soon!
  def send_msg(val):
    socket.send(wrap_cmd(val).SerializeToString())
    print val

  loop_data = MockData(True)
  emotiv_loop(ssvep_processor.SsvepProcessor(), loop_data, None, False,
              send_msg)


if __name__ == "__main__":
  main()
