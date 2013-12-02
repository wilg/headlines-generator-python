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

@app.route('/')
def hello():
    sources = request.args.get('sources', '')
# sha1
    results = []
    if sources:
      sources = sources.split(",")
      headlines = gen.generate(sources, 2)

      results = [{'headline':headline, 'hash': hashlib.sha1(headline + "-" + salt).hexdigest()} for headline in headlines]

    return jsonify(headlines=results)
