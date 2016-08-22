from flask import Flask, render_template, request, Response
from flask_bootstrap import Bootstrap
from json import dumps

from model import get_event_types, get_event_inst, get_relation_types, \
    get_relation_inst
from soa import stand_off_to_inline

from neo4j.v1 import GraphDatabase, basic_auth

# SOURCE_LINK = ' '.join(u'''
# <a target="_blank"
#    href="http://dx.doi.org/{row[doi]}"
#    data-toggle="popover"
#    data-trigger="hover"
#    data-placement="left"
#    data-title="{row[title]}"
#    data-content="{row[author]},<br><br> {row[journal]}:{row[volume]}, {row[year]}."
#    <span class="glyphicon glyphicon-file"></span>
# </a>
# '''.split())

SOURCE_LINK = ' '.join(u'''
<a target="_blank"
   href="http://dx.doi.org/{row[doi]}"
   data-toggle="popover"
   data-trigger="hover"
   data-placement="left"
   data-title="TITLE"
   data-content="{row[citation]}"
   <span class="glyphicon glyphicon-file"></span>
</a>
'''.split())


EVENT = ' '.join(u'''
span class="{event}"
data-toggle="popover"
data-trigger="hover"
data-content={pattern}
'''.split())

app = Flask(__name__)
app.config.from_pyfile('mvl.cfg')


def init_neo4j_connection(app):
    server_url = app.config.get('NEO4J_URL', 'bolt://localhost:7687')
    encrypted = app.config.get('NEO4J_ENCRYPTED', True)
    user = app.config.get('NEO4J_USER', 'neo4j')
    password = app.config.get('NEO4J_PASSWORD')

    auth = basic_auth(user, password) if password else None
    driver = GraphDatabase.driver(server_url,
                                  encrypted=encrypted,
                                  auth=auth)
    app.config['NEO4J_DRIVER'] = driver


@app.route('/')
def search():
    return render_template('mvl.html')


@app.route('/event-types', methods=['POST'])
def event_types():
    rules = request.get_json()
    result = get_event_types(rules)
    # TODO: serialize to Json from generator instead of list
    result = [dict(r) for r in result]
    json = dumps(result, encoding='utf-8')
    return Response(response=json,
                    status=200,
                    mimetype="application/json")


@app.route('/event-inst', methods=['POST'])
def event_inst():
    pay_load = request.get_json()
    node_ids = pay_load['node_ids']
    sources = get_event_inst(node_ids)

    # mark up sentences with variables
    sentences = []

    for row in sources:
        stand_off = [(row['eventBegin'] - row['sentBegin'],
                      row['eventEnd'] - row['sentBegin'],
                      EVENT.format(event=row['event'],
                                   pattern=row['eventPattern']))]
        sent = stand_off_to_inline(row['sentence'], stand_off)
        source = SOURCE_LINK.format(row=row)
        sentences.append([sent, row['year'], source])

    response = dumps(dict(data=sentences),
                     encoding='utf-8')

    return Response(response=response,
                    status=200,
                    mimetype="application/json")


@app.route('/relation-types', methods=['POST'])
def relation_types():
    rules = request.get_json()
    result = get_relation_types(rules)
    # TODO: serialize to Json from generator instead of list
    result = [dict(r) for r in result]
    response = dumps(result, encoding='utf-8')
    return Response(response=response,
                    status=200,
                    mimetype="application/json")


@app.route('/relation-inst', methods=['POST'])
def relation_inst():
    pay_load = request.get_json()
    node_ids = pay_load['node_ids']
    instances = get_relation_inst(node_ids)
    records = []

    for inst in instances:
        # create sentence with mark-up for events
        stand_off = [(inst['eventBegin1'] - inst['sentBegin'],
                      inst['eventEnd1'] - inst['sentBegin'],
                      'span class="{}"'.format(inst['event1'])),
                     (inst['eventBegin2'] - inst['sentBegin'],
                      inst['eventEnd2'] - inst['sentBegin'],
                      'span class="{}"'.format(inst['event2']))]
        sent = stand_off_to_inline(inst['sentence'], stand_off)
        # create formatted citation linked to source webpage
        source = SOURCE_LINK.format(row=inst)
        record = dict(sentence=sent,
                      year=inst['year'],
                      source=source)
        records.append(record)

    response = dumps(records, encoding='utf-8')

    return Response(response=response,
                    status=200,
                    mimetype="application/json")


Bootstrap(app)
init_neo4j_connection(app)

if __name__ == '__main__':
    app.run(port=5400)
