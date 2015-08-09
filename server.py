import os
from flask import Flask
from flask import jsonify
from flask import request
from generator import HeadlineGenerator
import hashlib

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

    sources = request.args.get('sources', '')
    seed_word = request.args.get('seed_word', '')
    reconstruct = request.args.get('reconstruct', False)
    age = request.args.get('age', None)
    depth = int(request.args.get('depth', 2))

    results = []
    if sources or age:
      sources = sources.split(",")
      headlines = []

      if age:
        headlines = gen.generate_recent(int(age), depth, seed_word)
      elif reconstruct:
        headlines = [gen.reconstruct(reconstruct, sources)]
      else:
        headlines = gen.generate(sources, depth, seed_word)

      results = [{
          'headline':unicode(headline),
          'sources': headline.fragment_hashes(),
          'hash': hashlib.sha1((unicode(headline) + "-" + salt).encode('utf-8')).hexdigest()
        } for headline in headlines]

    return jsonify(headlines=results)
