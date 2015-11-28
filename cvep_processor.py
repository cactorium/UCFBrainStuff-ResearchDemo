import processor


class CvepProcessor(processor.PacketProcessor):
  def __init__(self):
    pass

  def get_record_data(self, packet, extra_data):
    is_sync_frame = extra_data
    return packet, is_sync_frame

  def process_frame(self, data):
    packet, is_sync_frame = data
    # TODO
    pass
