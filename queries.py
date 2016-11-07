"""
Cypher queries
"""

# TODO: remove hard-coded LIMIT cases
# TODO: lower case relation name: lower?


# -------------------------------------------------------------------------------
# Event types query
# -------------------------------------------------------------------------------

EVENT_TYPE_DIRECT_PAT = '''
    (v{i}:VariableType) <-[:HAS_VAR]- (e{i}:EventType)'''

EVENT_TYPE_DIRECT_WITH = '''
    v{i} as varType{i},
    e{i} as eventType{i}'''

EVENT_TYPE_SPEC_PAT = '''
    (v{i}:VariableType) <-[:TENTAILS_VAR*0..{max_length}]- (vs{i}:VariableType)
    <-[:HAS_VAR]- (e{i}:EventType)'''

EVENT_TYPE_SPEC_WITH = '''
    vs{i} as varType{i},
    e{i} as eventType{i}'''

EVENT_TYPE_GEN_PAT = '''
    (v{i}:VariableType) -[:TENTAILS_VAR*0..{max_length}]-> (vg{i}:VariableType)
    <-[:HAS_VAR]- (e{i}:EventType)'''

EVENT_TYPE_GEN_WITH = '''
    vg{i} as varType{i},
    e{i} as eventType{i}'''

EVENT_TYPE_REL_PAT = '''
    (e1) -[r:{relation}]-{direction} (e2)'''


EVENT_TYPE_QUERY = '''
MATCH
    {event_pat}
WHERE
    {event_where}
WITH DISTINCT
    {event_with}
WITH
    varType.subStr as variable,
    eventType.n AS eventCount,
    eventType.direction as event
RETURN
    eventCount,
    event,
    variable
    ORDER BY eventCount DESC
    LIMIT {limit}'''

# -------------------------------------------------------------------------------
# Event instances query
# -------------------------------------------------------------------------------

EVENT_INST_QUERY = '''
MATCH
    (v:VariableType) <-[:HAS_VAR]- (e:EventInst)
    <-[:HAS_EVENT]- (s:Sentence) <-[:HAS_SENT]- (a:Article)
WHERE
    v.subStr = "{variable_string}" AND
    e.direction = "{event_direction}"
WITH
    "{event_direction}" as event,
    e.charOffsetBegin as eventBegin,
    e.charOffsetEnd as eventEnd,
    e.extractName as eventPattern,
    s.charOffsetBegin as sentBegin,
    s.sentChars as sentence,
    a.doi as doi,
    a.year as year,
    a.citation as citation
RETURN
    event,
    eventBegin,
    eventEnd,
    eventPattern,
    sentBegin,
    sentence,
    doi,
    year,
    citation
    ORDER BY year DESC
    LIMIT {limit}
'''

# ------------------------------------------------------------------------------
# Relation types query
# ------------------------------------------------------------------------------

REL_TYPE_QUERY = '''
MATCH
    {event_1_pat},
    {event_2_pat},
    {relation_pat}
WHERE
    {event_1_where} AND
    {event_2_where} AND
    {rel_where}
WITH DISTINCT
    {event_1_with},
    {event_2_with},
    r
WITH
    varType1.subStr AS variable1,
    eventType1.direction as event1,
    eventType1.n AS eventCount1,
    id(eventType1) AS nodeId1,

    varType2.subStr AS variable2,
    eventType2.direction as event2,
    eventType2.n AS eventCount2,
    id(eventType2) AS nodeId2,

    type(r) AS relation,
    r.n AS relationCount,
    id(r) AS relationId
RETURN
    relationCount,
    relation,
    event1,
    variable1,
    event2,
    variable2,
    nodeId1,
    nodeId2,
    relationId,
    eventCount1,
    eventCount2
    ORDER BY relationCount DESC
    LIMIT {limit}'''

# ------------------------------------------------------------------------------
# Relation instances query
# ------------------------------------------------------------------------------

# cooccurrence relation is non-directed
COOCCURS_INST_MATCH = '''
MATCH
    (v1:VariableType) <-[:HAS_VAR]- (ei1:EventInst)
    <-[:HAS_EVENT]- (s:Sentence) -[:HAS_EVENT]->
    (ei2:EventInst) -[:HAS_VAR]-> (v2:VariableType),
    (s) <-[:HAS_SENT]- (a:Article)
    '''

# causal relation is directed
CAUSES_INST_MATCH = '''
MATCH
    (v1:VariableType) <-[:HAS_VAR]- (ei1:EventInst)
    <-[:HAS_CAUSE]- (:CausationInst) -[:HAS_EFFECT]->
    (ei2:EventInst) -[:HAS_VAR]-> (v2:VariableType),
    (ei1) <-[:HAS_EVENT]- (s:Sentence) <-[:HAS_SENT]- (a:Article)
    '''

RELATION_INST_QUERY = '''
WHERE
    v1.subStr = "{variable1}" AND
    v2.subStr = "{variable2}"
WITH
    ei1.direction as event1,
    ei1.charOffsetBegin as eventBegin1,
    ei1.charOffsetEnd as eventEnd1,

    ei2.direction as event2,
    ei2.charOffsetBegin as eventBegin2,
    ei2.charOffsetEnd as eventEnd2,

    s.charOffsetBegin as sentBegin,
    s.sentChars as sentence,

    a.doi as doi,
    a.year as year,
    a.citation as citation
RETURN
    event1,
    eventBegin1,
    eventEnd1,
    event2,
    eventBegin2,
    eventEnd2,
    sentBegin,
    sentence,
    doi,
    year,
    citation
    ORDER BY year DESC
    LIMIT {limit}
'''
