"""
interface to neo4j graph database
"""


import logging
log = logging.getLogger(__name__)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(levelname)s: %(module)s.%(funcName)s: %(lineno)d\n%(message)s')
handler.setFormatter(formatter)
log.addHandler(handler)
# enable logging here
#log.setLevel(logging.DEBUG)
log.setLevel(logging.ERROR)

from py2neo import Graph

from queries import EVENT_TYPE_QUERY, EVENT_INST_QUERY, RELATION_TYPE_QUERY, RELATION_INST_QUERY

GRAPH = Graph('http://neo4j:nature@localhost:47470/db/data/')




def get_event_types(rules):
    query = EVENT_TYPE_QUERY.format(parse_group(rules, 've'))
    log.debug(query)
    response = GRAPH.cypher.post(query)
    result = reclist2obj(response.content)
    log.debug(result)
    return result


def get_event_inst(node_ids):
    query = EVENT_INST_QUERY.format(node_ids)
    log.debug(query)
    result = GRAPH.cypher.execute(query)
    log.debug(result)
    return result


def get_relation_types(rules):
    operands = [parse_group(rules['event_1'], 've1'),
                parse_group(rules['event_2'], 've2'),
                parse_group(rules['relation'], 'r')]
    where = ' AND\n    '.join(operands)
    query = RELATION_TYPE_QUERY.format(where)
    log.debug(query)
    response = GRAPH.cypher.post(query)
    result = reclist2obj(response.content)
    log.debug(result)
    return result


def get_relation_inst(node_ids):
    log.debug('')
    query = RELATION_INST_QUERY.format(id1=node_ids[0], id2=node_ids[1])
    log.debug(query)
    result = GRAPH.cypher.execute(query)
    log.debug(result)
    return result


def reclist2obj(record_list):
    """
    Convert Neo4py RecordList to a list of 'Javascript objects'
    for consumption by DataTables

    Example output:

    [{u'event1': u'Increase',
      u'event2': u'Decrease',
      u'nodeId1': 70270,
      u'nodeId2': 76396,
      u'relation': u'COOCCURS',
      u'relationCount': 3,
      u'relationId': 110822,
      u'variable1': u'temperature',
      u'variable2': u'temperature'},
      ...
    ]
    """
    keys = record_list['columns']
    return [dict(zip(keys, record))
            for record in record_list['data']]


# parse query-builder rules

# TODO: error handling (e.g. unknown operator)


def parse_group(rules, neo4j_id):
    """
    parse query-builder group
    """
    operands = []

    for rule in rules['rules']:
        if rule.get('rules'):
            operand = parse_group(rule, neo4j_id)
        else:
            operand = parse_rule(rule, neo4j_id)

        operands.append(operand)

    condition = ' ' + rules['condition'] + ' '
    operands_str = condition.join(operands)

    if len(operands) > 1:
        operands_str = '( ' + operands_str + ' )'

    return operands_str


# TODO: escape special symbols in regex

def parse_rule(rule, neo4j_id):
    """
    parse query-builder rule
    """
    operand_str = None
    field, operator, type, value = rule['field'], rule['operator'], \
                                   rule['type'], rule['value']
    if field == 'variable':
        if 'equal' in operator:
            operand_str = '{}.subStr = "{}"'.format(neo4j_id, value)
        elif 'begins_with_word' in operator:
            operand_str = r'{}.subStr =~ "^{}(\\W.*|$)"'.format(neo4j_id, value)
        elif 'contains_word' in operator:
            operand_str = r'{}.subStr =~ "(^|.*\\W){}(\\W.*|$)"'.format(neo4j_id,
                                                                        value)
        elif 'ends_with_word' in operator:
            operand_str = r'{}.subStr =~ "(^|.*\\W){}$"'.format(neo4j_id, value)
        elif 'begins_with_string' in operator:
            operand_str = '{}.subStr STARTS WITH "{}"'.format(neo4j_id, value)
        elif 'contains_string' in operator:
            operand_str = '{}.subStr CONTAINS "{}"'.format(neo4j_id, value)
        elif 'ends_with_string' in operator:
            operand_str = '{}.subStr ENDS WITH "{}"'.format(neo4j_id, value)
    elif field == 'event':
        if operator == 'equal':
            operand_str = '{}:Var{}'.format(neo4j_id, value)
    elif field == 'cooccurrence':
        if operator == 'equals':
            operand_str = '{}.n = {}'.format(neo4j_id, value)
        elif operator == 'greater':
            operand_str = '{}.n > {}'.format(neo4j_id, value)
        elif operator == 'less':
            operand_str = '{}.n < {}'.format(neo4j_id, value)

    if operator.startswith('not_'):
        operand_str = 'NOT ' + operand_str

    return operand_str
