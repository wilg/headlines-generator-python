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
    depth = int(request.args.get('depth', 2))

    results = []
    if sources:
      sources = sources.split(",")
      headlines = gen.generate(sources, depth)

      results = [{'headline':str(headline), 'sources': headline.fragment_hashes(), 'hash': hashlib.sha1(str(headline) + "-" + salt).hexdigest()} for headline in headlines]

    return jsonify(headlines=results)
