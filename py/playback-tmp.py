import cPickle

import sys
import time

import braingerZone


def main():
  if len(sys.argv) < 2:
    print '%s <file-name>' % sys.argv[0]
    return
  data = cPickle.load(open(sys.argv[1], 'rb'))
  state = braingerZone.State()
  for d in data:
    state.process_frame(d, True, None)
    time.sleep(1/(256*4.0))

if __name__ == "__main__":
  main()
