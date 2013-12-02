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

    results = []
    if sources:
      sources = sources.split(",")
      headlines = gen.generate(sources, 2)

      results = [{'headline':headline, 'hash': hashlib.sha1(headline + "-" + salt).hexdigest()} for headline in headlines]

    return jsonify(headlines=results)
