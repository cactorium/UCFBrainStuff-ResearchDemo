import zmq

import braingerZone

import seniordesign_pb2 as sd


def wrap_cmd(tp):
  d, confidence = tp
  ret = sd.ProcessingResults()
  ret.confidence = confidence
  if d == braingerZone.BACKWARD:
    ret.direction = sd.BACKWARD
  elif d == braingerZone.FORWARD:
    ret.direction = sd.FORWARD
  elif d == braingerZone.LEFT:
    ret.direction = sd.LEFT
  elif d == braingerZone.RIGHT:
    ret.direction = sd.RIGHT
  elif d == braingerZone.NEUTRAL:
    ret.direction = sd.NEUTRAL
  return ret


def main():
  context = zmq.Context()
  socket = context.socket(zmq.PUB)
  socket.bind('ipc://pc_cmds')

  def send_msg(val):
    socket.send_string(wrap_cmd(val).SerializeToString())

  while True:
    braingerZone.emotiv_loop(None, None, None, send_msg)


if __name__ == "__main__":
  main()
