import zmq

from emotiv_loop import emotiv_loop
import ssvep_processor

import seniordesign_pb2 as sd


def wrap_cmd(tp):
  d, confidence = tp, 1.0
  ret = sd.ProcessingResults()
  ret.confidence = confidence
  if d == ssvep_processor.BACKWARD:
    ret.direction = sd.BACKWARD
  elif d == ssvep_processor.FORWARD:
    ret.direction = sd.FORWARD
  elif d == ssvep_processor.LEFT:
    ret.direction = sd.LEFT
  elif d == ssvep_processor.RIGHT:
    ret.direction = sd.RIGHT
  elif d == ssvep_processor.NEUTRAL:
    ret.direction = sd.NEUTRAL
  return ret


class MockData(object):
  def __init__(self, val):
    self.value = val


def main():
  context = zmq.Context()
  socket = context.socket(zmq.PUB)
  socket.bind('tcp://localhost:9000')

  # NOTE: This doesn't correctly work because the process_frame doesn't
  # currently return values. To be fixed soon!
  def send_msg(val):
    socket.send_string(wrap_cmd(val).SerializeToString())
    print val

  loop_data = MockData(True)
  emotiv_loop(ssvep_processor.SsvepProcessor(), loop_data, None, False,
              send_msg)


if __name__ == "__main__":
  main()
