import urllib3
urllib3.disable_warnings()

import os
from flask import Flask
from flask import jsonify
from flask import request
from generator import HeadlineGenerator
import hashlib

import logging
logger = logging.getLogger('server')
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler())

app = Flask(__name__)
app.debug = True

gen = HeadlineGenerator()

salt = os.getenv('HEADLINE_INJECTION_SALT', '')

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

@app.route('/')
def generate():

    logger.info("received request " + request.url)

    sources = request.args.get('sources', '')
    seed_word = request.args.get('seed_word', '')
    reconstruct = request.args.get('reconstruct', False)
    age = request.args.get('age', None)
    depth = int(request.args.get('depth', 2))
    count = int(request.args.get('count', 10))
    length_max = int(request.args.get('length_max', 140))

    if count > 100:
      count = 100

    results = []
    if sources or age:
      sources = sources.split(",")
      headlines = []

      if age:
        headlines = gen.generate_recent(int(age), depth, seed_word, count, length_max)
      elif reconstruct:
        headlines = [gen.reconstruct(reconstruct, sources)]
      else:
        headlines = gen.generate(sources, depth, seed_word, count, length_max)

      results = [{
          'headline':unicode(headline),
          'sources': headline.fragment_hashes(),
          'hash': hashlib.sha1((unicode(headline) + "-" + salt).encode('utf-8')).hexdigest()
        } for headline in headlines]

    return jsonify(headlines=results)
