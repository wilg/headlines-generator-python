import sys
from generator import HeadlineGenerator

# Accept args for different dictionaries
dicts = sys.argv
dicts.pop(0)

# Import depth
depth = int(dicts.pop(0))

gen = HeadlineGenerator()
results = gen.generate(dicts, depth, '')

for result in results:
    print result