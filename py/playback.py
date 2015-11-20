import cPickle

import sys

# import braingerZone


def main():
  if len(sys.argv) < 2:
    print '%s <file-name>' % sys.argv[0]
    return
  data = cPickle.load(open(sys.argv[1], 'rb'))
  for d in data:
    pass

if __name__ == "__main__":
  main()
