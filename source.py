from peewee import *
import os
import pw_database_url
import logging
import operator
from timeit import default_timer as timer

logger = logging.getLogger('peewee')
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler())

if os.environ.get('DATABASE_URL', None):
  config = pw_database_url.config()
else:
  config = {
        'engine': 'peewee.PostgresqlDatabase',
        'name': 'headlines_development',
        'host': 'localhost',
        'port': 5432,
        'password': None,
        'user': None,
    }

db = PostgresqlDatabase(config['name'], host=config['host'], port=config['port'], password=config['password'], user=config['user'])
db.get_conn().set_client_encoding('UTF8')
db.connect()

class SourceHeadline(Model):
  id = IntegerField()
  name = TextField()
  source_id = CharField()
  created_at = DateTimeField()
  updated_at = DateTimeField()
  published_at = DateTimeField()

  class Meta:
    database = db
    db_table = 'source_headlines'

  @classmethod
  def random(klass, sources, amount):
    start = timer()

    items = []
    if os.environ.get('PULL_SOURCES_RANDOMLY', False):
      clauses = [SourceHeadline.source_id == source for source in sources]
      items = SourceHeadline.select().where(reduce(operator.or_, clauses)).order_by(fn.Random()).limit(amount)
      items.execute()
    else:
      for source in sources:
        subset = SourceHeadline.select().where(SourceHeadline.source_id == source).order_by(fn.Random()).limit(amount / len(sources))
        subset.execute()
        items += [item for item in subset]

    logger.info("-> query time for " + str(amount) + " headlines " + str(timer() - start))
    return items

