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
    result = get_event_types(**request.get_json())
    # TODO: serialize to Json from generator instead of list
    result = [dict(r) for r in result]
    json = dumps(result, encoding='utf-8')
    return Response(response=json,
                    status=200,
                    mimetype="application/json")


@app.route('/event-inst', methods=['POST'])
def event_inst():
    pay_load = request.get_json()
    sources = get_event_inst(pay_load['event'], pay_load['var'])

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
    types = get_relation_types(rules)
    rel_ids = set()
    records = []

    # FIXME relationId hack
    # This is to prevent the same COOCCURS relation,
    # which is non-directed, to show up twice in the returned relation types.
    # I can not find a way to express this in a Cypher query.
    # Earlier I used "WHERE id(et1) < id(et2)", but that is wrong.
    # For example, these two settings should give the same results:
    # 1) Event 1: variable is diatom, Event 2: no restrictions;
    # 2) Event 2: no restrictions, Event 2: variable is diatom.
    # However, when using "id(et1) < id(et2)" only one of them will work!
    for typ in types:
        if not typ['relationId'] in rel_ids:
            rel_ids.add(typ['relationId'])
            records.append(dict(typ))

    response = dumps(records, encoding='utf-8')
    return Response(response=response,
                    status=200,
                    mimetype="application/json")


@app.route('/relation-inst', methods=['POST'])
def relation_inst():
    pay_load = request.get_json()
    instances = get_relation_inst(
        event1=pay_load['event1'],
        event2=pay_load['event2'],
        var1=pay_load['var1'],
        var2=pay_load['var2'],
        relation=pay_load['relation'])
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
