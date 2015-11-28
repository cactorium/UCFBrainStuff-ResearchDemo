import processor


class SsvepProcessor(processor.PacketProcessor):
  def __init__(self):
    pass

  def process_frame(self, packet):
    print packet
    # TODO
    pass
