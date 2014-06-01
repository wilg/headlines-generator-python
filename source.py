from peewee import *
import os
import pw_database_url

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
    return SourceHeadline.select().where(SourceHeadline.source_id << sources).order_by(fn.Random()).limit(amount)
