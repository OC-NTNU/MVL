"""
interface to neo4j graph database
"""

import logging

log = logging.getLogger(__name__)
handler = logging.StreamHandler()
formatter = logging.Formatter(
    '%(levelname)s: %(module)s.%(funcName)s: %(lineno)d\n%(message)s')
handler.setFormatter(formatter)
log.addHandler(handler)
# enable logging here
# log.setLevel(logging.DEBUG)
log.setLevel(logging.ERROR)

from queries import EVENT_TYPE_QUERY, EVENT_INST_QUERY, RELATION_TYPE_QUERY, \
    RELATION_INST_QUERY

from flask import current_app as app

from neo4j.v1 import CypherError


def run_query(query):
    log.debug(query)

    try:
        session = app.config['NEO4J_DRIVER'].session()
    except Exception as err:
        # e.g. socket.gaierror
        log.error(err)
        raise err

    try:
        result = session.run(query)
    except CypherError as err:
        log.error(err)
        raise err
        # TODO: raised exception should ultimately results in a 500 response
    finally:
        session.close()

    # wrap result generator to allow logging
    for record in result:
        log.debug(record)
        yield record


def get_event_types(rules):
    query = EVENT_TYPE_QUERY.format(parse_group(rules, 've'))
    return run_query(query)


def get_event_inst(node_ids):
    query = EVENT_INST_QUERY.format(node_ids)
    return run_query(query)


def get_relation_types(rules):
    operands = [parse_group(rules['event_1'], 've1'),
                parse_group(rules['event_2'], 've2'),
                parse_group(rules['relation'], 'r')]
    where = ' AND\n    '.join(operands)
    query = RELATION_TYPE_QUERY.format(where)
    return run_query(query)


def get_relation_inst(node_ids):
    query = RELATION_INST_QUERY.format(id1=node_ids[0], id2=node_ids[1])
    return run_query(query)


# parse query-builder rules

# TODO: error handling (e.g. unknown operator)


def parse_group(rules, neo4j_id):
    """
    parse query-builder group
    """
    operands = []

    for rule in rules.get('rules', []):
        if rule.get('rules'):
            operand = parse_group(rule, neo4j_id)
        else:
            operand = parse_rule(rule, neo4j_id)

        operands.append(operand)

    condition = ' ' + rules.get('condition', '') + ' '
    operands_str = condition.join(operands)

    if len(operands) > 1:
        operands_str = '( ' + operands_str + ' )'

    # if rules is empty, return TRUE, so query remains well-formed
    return operands_str or 'TRUE'


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
            operand_str = r'{}.subStr =~ "(^|.*\\W){}(\\W.*|$)"'.format(
                neo4j_id,
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
