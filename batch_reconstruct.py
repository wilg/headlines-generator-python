import sys
from generator import HeadlineGenerator
import json
import os
import hashlib

# Import search headlines
archive = open("batch.txt")
search_headlines = archive.read().split("\n")
archive.close()

gen = HeadlineGenerator()
results = []
i = 0
total = len(search_headlines)

for headline in search_headlines:
  print(str(i) + " / " + str(total))
  try:

    # Reconstruct it
    h = gen.reconstruct(headline, None)
    results.append({'headline':str(h), 'sources': h.fragment_hashes()})

    # Dump everything to JSON
    outfile = open("batch_out.json", 'w')
    outfile.write(json.dumps({'headlines': results}))
    outfile.close()

    print("  -> Reconstructed " + str(h))

  except Exception, e:
    print("  -> Couldn't reconstruct " + headline)
    print("  -> " + str(e))
    pass
  i += 1
