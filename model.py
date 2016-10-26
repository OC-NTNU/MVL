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
log.setLevel(logging.ERROR)
log.setLevel(logging.DEBUG)

from queries import *

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


def get_event_types(rules, with_special, with_general):
    where = parse_group(rules)
    sub_query = EVENT_TYPE_QUERY.format(where=where)
    parts = [sub_query]

    if with_special:
        sub_query = EVENT_TYPE_WITH_SPECIAL_QUERY.format(where=where)
        parts.append(sub_query)

    if with_general:
        sub_query = EVENT_TYPE_WITH_GENERAL_QUERY.format(where=where)
        parts.append(sub_query)

    query = 'UNION ALL'.join(parts)

    return run_query(query)


def get_event_inst(event, var):
    query = EVENT_INST_QUERY.format(event=event, var=var)
    return run_query(query)


def get_relation_types(rules):
    operands = [parse_group(rules['event_1'], meta_var='v1', meta_event='et1'),
                parse_group(rules['event_2'], meta_var='v2', meta_event='et2'),
                parse_group(rules['relation'])]
    where = ' AND\n    '.join(operands)
    relation = rules['relation']['rules'][0]['id'].upper()

    if relation == 'COOCCURS':
        query = COOCCURS_TYPE_QUERY.format(where=where)
    elif relation == 'CAUSES':
        query = CAUSES_TYPE_QUERY.format(where=where)
    # TODO: error handling

    return run_query(query)


def get_relation_inst(event1, event2, var1, var2, relation):
    if relation == 'COOCCURS':
        query = COOCCURS_INST_QUERY.format(event1=event1, event2=event2,
                                           var1=var1, var2=var2)
    elif relation == 'CAUSES':
        query = CAUSES_INST_QUERY.format(event1=event1, event2=event2,
                                         var1=var1, var2=var2)
    # TODO: error handling
    return run_query(query)


# parse query-builder rules

# TODO: error handling (e.g. unknown operator)


def parse_group(rules, meta_var='v', meta_event='e', meta_rel='r'):
    """
    parse query-builder group
    """
    operands = []

    for rule in rules.get('rules', []):
        if rule.get('rules'):
            operand = parse_group(rule, meta_var, meta_event, meta_rel)
        else:
            operand = parse_rule(rule, meta_var, meta_event, meta_rel)

        operands.append(operand)

    condition = ' ' + rules.get('condition', '') + ' '
    operands_str = condition.join(operands)

    if len(operands) > 1:
        operands_str = '( ' + operands_str + ' )'

    # if rules is empty, return TRUE, so query remains well-formed
    return operands_str or 'TRUE'


# TODO: escape special symbols in regex

def parse_rule(rule, meta_var='v', meta_event='et', meta_rel='r'):
    """
    parse query-builder rule
    """
    operand_str = None
    field, operator, type, value = rule['field'], rule['operator'], \
                                   rule['type'], rule['value']
    if field == 'variable':
        if 'equal' in operator:
            operand_str = '{}.subStr = "{}"'.format(meta_var, value)
        elif 'begins_with_word' in operator:
            operand_str = r'{}.subStr =~ "^{}(\\W.*|$)"'.format(meta_var, value)
        elif 'contains_word' in operator:
            operand_str = r'{}.subStr =~ "(^|.*\\W){}(\\W.*|$)"'.format(
                meta_var, value)
        elif 'ends_with_word' in operator:
            operand_str = r'{}.subStr =~ "(^|.*\\W){}$"'.format(
                meta_var, value)
        elif 'begins_with_string' in operator:
            operand_str = '{}.subStr STARTS WITH "{}"'.format(meta_var, value)
        elif 'contains_string' in operator:
            operand_str = '{}.subStr CONTAINS "{}"'.format(meta_var, value)
        elif 'ends_with_string' in operator:
            operand_str = '{}.subStr ENDS WITH "{}"'.format(meta_var, value)
    elif field == 'event':
        if 'equal' in operator:
            operand_str = '{}:{}Type'.format(meta_event, value)
    elif field in ['cooccurs', 'causes']:
        if operator == 'equals':
            operand_str = '{}.n = {}'.format(meta_rel, value)
        elif operator == 'greater':
            operand_str = '{}.n > {}'.format(meta_rel, value)
        elif operator == 'less':
            operand_str = '{}.n < {}'.format(meta_rel, value)

    if operator.startswith('not_'):
        operand_str = 'NOT ' + operand_str

    return operand_str
