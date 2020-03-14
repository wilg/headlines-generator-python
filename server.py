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

@app.route('/', methods=['GET', 'POST'])
def generate():

    params = None
    if request.method == 'POST':
      params = request.form
    else:
      params = request.args

    logger.info("received request " + request.url)

    sources = params.get('sources', '')
    seed_word = params.get('seed_word', '')
    reconstruct = params.get('reconstruct', False)
    age = params.get('age', None)
    depth = int(params.get('depth', 2))
    count = int(params.get('count', 10))
    length_max = int(params.get('length_max', 140))

    if count > 100:
      count = 100

    results = []
    if sources or age:
      sources = sources.split(",")
      sources = list(filter(None, sources))
      headlines = []

      if age:
        headlines = gen.generate_recent(int(age), sources, depth, seed_word, count, length_max)
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
