import cPickle

import sys
import time


def main(p):
  if len(sys.argv) < 2:
    print '%s <file-name>' % sys.argv[0]
    return
  data = cPickle.load(open(sys.argv[1], 'rb'))
  for d in data:
    p.process_frame(d)
    time.sleep(1/(256*4.0))
