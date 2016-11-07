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


def get_event_types(rules, search_type):
    event_pat = build_event_type_pattern(search_type)
    event_where = parse_group(rules)
    event_with = build_with_clause(search_type)

    query = EVENT_TYPE_QUERY.format(
        event_pat=event_pat,
        event_where=event_where,
        event_with=event_with,
        limit=500)

    return run_query(query)


def get_event_inst(event_direction, variable_string):
    query = EVENT_INST_QUERY.format(event_direction=event_direction,
                                    variable_string=variable_string,
                                    limit=500)
    return run_query(query)


# TODO seting of max_length
def build_event_type_pattern(search_type, i=None, max_length=3):
    i = '' if i is None else str(i)

    if search_type == 'with_special':
        pattern = EVENT_TYPE_SPEC_PAT
    elif search_type == 'with_general':
        pattern = EVENT_TYPE_GEN_PAT
    else:
        pattern = EVENT_TYPE_DIRECT_PAT

    return pattern.format(i=i, max_length=max_length).strip()


def build_relation_pattern(rules):
    relation = rules['rules'][0]['id'].upper()
    direction = '>' if relation == 'CAUSES' else ''
    where = parse_group(rules)

    return EVENT_TYPE_REL_PAT.format(relation=relation,
                                     direction=direction,
                                     where=where).strip()


def build_with_clause(search_type, i=None):
    i = '' if i is None else str(i)

    if search_type == 'with_special':
        pattern = EVENT_TYPE_SPEC_WITH
    elif search_type == 'with_general':
        pattern = EVENT_TYPE_GEN_WITH
    else:
        pattern = EVENT_TYPE_DIRECT_WITH

    return pattern.format(i=i).strip()


def get_relation_types(event_1, event_2, relation):
    event_1_pat = build_event_type_pattern(event_1['search_type'], 1)
    event_2_pat = build_event_type_pattern(event_2['search_type'], 2)
    relation_pat = build_relation_pattern(**relation)

    event_1_where = parse_group(event_1['rules'], 1)
    event_2_where = parse_group(event_2['rules'], 2)
    rel_where = parse_group(relation['rules'])

    event_1_with = build_with_clause(event_1['search_type'], 1)
    event_2_with = build_with_clause(event_2['search_type'], 2)

    # FIXME hack related to the one in  mvl.relation_types()
    relation_type = relation['rules']['rules'][0]['id'].upper()
    if relation_type == 'COOCCURS':
        limit = 900
    else:
        limit = 500

    query = REL_TYPE_QUERY.format(
        event_1_pat=event_1_pat,
        event_2_pat=event_2_pat,
        relation_pat=relation_pat,
        event_1_where=event_1_where,
        event_2_where=event_2_where,
        rel_where=rel_where,
        event_1_with=event_1_with,
        event_2_with=event_2_with,
        limit=limit)

    return run_query(query)


def get_relation_inst(event1, event2, variable1, variable2, relation):
    if relation == 'COOCCURS':
        query = COOCCURS_INST_MATCH
    elif relation == 'CAUSES':
        query = CAUSES_INST_MATCH

    query += RELATION_INST_QUERY

    query = query.format(event1=event1,
                         event2=event2,
                         variable1=variable1,
                         variable2=variable2,
                         limit=500)
    return run_query(query)


# parse query-builder rules

# TODO: error handling (e.g. unknown operator)


def parse_group(rules, i=None):
    """
    parse query-builder group
    """
    operands = []

    for rule in rules.get('rules', []):
        if rule.get('rules'):
            operand = parse_group(rule, i)
        else:
            operand = parse_rule(rule, i)

        operands.append(operand)

    condition = ' ' + rules.get('condition', '') + ' '
    operands_str = condition.join(operands)

    if len(operands) > 1:
        operands_str = '( ' + operands_str + ' )'

    # if rules is empty, return TRUE, so query remains well-formed
    return operands_str or 'TRUE'


# TODO: escape special symbols in regex

def parse_rule(rule, i=None):
    """
    parse query-builder rule
    """
    i = '' if i is None else str(i)

    meta_var = 'v' + i
    meta_event = 'e' + i
    meta_rel = 'r' + i

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
            operand_str = '{}.direction = "{}"'.format(meta_event, value)
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
