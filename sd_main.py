import seniordesign_pb2

from grpc.beta import implementations


def main():
  channel = implementations.insecure_channel('localhost', 500042)
  stub = seniordesign_pb2.beta_create_ResultsReceiver_stub(channel)

if __name__ == "__main__":
  main()
