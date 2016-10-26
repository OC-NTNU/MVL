"""
Cypher queries
"""

# TODO: remove hard-coded LIMIT cases
# TODO: lower case relation name: lower?


# ------------------------------------------------------------------------------
# Event queries
# ------------------------------------------------------------------------------


EVENT_TYPE_QUERY = '''
MATCH
    (v:VariableType) <-[:HAS_VAR]- (e:EventType)
WHERE
    {where}
WITH
    e.n AS eventCount,
    CASE
        WHEN "IncreaseType" IN labels(e) THEN "Increase"
        WHEN "DecreaseType" IN labels(e) THEN "Decrease"
        ELSE "Change"
    END AS eventType,
    v.subStr AS variableType
RETURN
    eventCount,
    eventType,
    variableType
    ORDER BY eventCount DESC
    LIMIT 500
'''


# No need to check for instances, because:
# if there is an EventType, there must be at least one corresponding EventInst

EVENT_TYPE_WITH_SPECIAL_QUERY = '''
MATCH
    (v:VariableType) <-[:TENTAILS_VAR*]-
    (vs:VariableType) <-[:HAS_VAR]- (e:EventType)
WHERE
    {where}
WITH
    e.n AS eventCount,
    CASE
        WHEN "IncreaseType" IN labels(e) THEN "Increase"
        WHEN "DecreaseType" IN labels(e) THEN "Decrease"
        ELSE "Change"
    END AS eventType,
    vs.subStr AS variableType
RETURN
    eventCount,
    eventType,
    variableType
    ORDER BY eventCount DESC
    LIMIT 500
'''

EVENT_TYPE_WITH_GENERAL_QUERY = '''
MATCH
    (v:VariableType) -[:TENTAILS_VAR*]->
    (vg:VariableType) <-[:HAS_VAR]- (e:EventType)
WHERE
    {where}
WITH
    e.n AS eventCount,
    CASE
        WHEN "IncreaseType" IN labels(e) THEN "Increase"
        WHEN "DecreaseType" IN labels(e) THEN "Decrease"
        ELSE "Change"
    END AS eventType,
    vg.subStr AS variableType
RETURN
    eventCount,
    eventType,
    variableType
    ORDER BY eventCount DESC
    LIMIT 500
'''

EVENT_INST_QUERY = '''
MATCH
    (v:VariableType) <-[:HAS_VAR]- (e:{event}Inst)
    <-[:HAS_EVENT]- (s:Sentence) <-[:HAS_SENT]- (a:Article)
WHERE
    v.subStr = "{var}"
WITH
    CASE
        WHEN "IncreaseInst" IN labels(e) THEN "Increase"
        WHEN "DecreaseInst" IN labels(e) THEN "Decrease"
        ELSE "Change"
    END AS event,
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
    LIMIT 500
'''

# ------------------------------------------------------------------------------
# Relations queries
# ------------------------------------------------------------------------------

# Cooccurrence relation is non-directed.

COOCCURS_TYPE_QUERY = '''
MATCH
    (v1:VariableType) <-[:HAS_VAR]- (et1:EventType)
    -[r:COOCCURS]-
    (et2:EventType) -[:HAS_VAR]-> (v2:VariableType)
WHERE
    {where}
WITH
    CASE
        WHEN "IncreaseType" IN labels(et1) THEN "Increase"
        WHEN "DecreaseType" IN labels(et1) THEN "Decrease"
        ELSE "Change"
    END AS event1,
    v1.subStr AS variable1,
    id(et1) AS nodeId1,

    CASE
        WHEN "IncreaseType" IN labels(et2) THEN "Increase"
        WHEN "DecreaseType" IN labels(et2) THEN "Decrease"
        ELSE "Change"
    END AS event2,
    v2.subStr AS variable2,
    id(et2) AS nodeId2,

    type(r) as relation,
    r.n as relationCount,
    id(r) as relationId
RETURN
    relationCount,
    relation,
    event1,
    variable1,
    event2,
    variable2,
    nodeId1,
    nodeId2,
    relationId
    ORDER BY relationCount DESC
    LIMIT 500

'''

# Causal relation is directed

CAUSES_TYPE_QUERY = '''
MATCH
    (v1:VariableType) <-[:HAS_VAR]- (et1:EventType)
    -[r:CAUSES]->
    (et2:EventType) -[:HAS_VAR]-> (v2:VariableType)
WHERE
    {where}
WITH
    CASE
        WHEN "IncreaseType" IN labels(et1) THEN "Increase"
        WHEN "DecreaseType" IN labels(et1) THEN "Decrease"
        ELSE "Change"
    END AS event1,
    v1.subStr AS variable1,
    id(et1) AS nodeId1,

    CASE
        WHEN "IncreaseType" IN labels(et2) THEN "Increase"
        WHEN "DecreaseType" IN labels(et2) THEN "Decrease"
        ELSE "Change"
    END AS event2,
    v2.subStr AS variable2,
    id(et2) AS nodeId2,

    type(r) as relation,
    r.n as relationCount,
    id(r) as relationId
RETURN
    relationCount,
    relation,
    event1,
    variable1,
    event2,
    variable2,
    nodeId1,
    nodeId2,
    relationId
    ORDER BY relationCount DESC
    LIMIT 500
'''

RELATION_INST_QUERY = '''
WHERE
    v1.subStr = "{var1}" AND v2.subStr = "{var2}"
WITH
    CASE
        WHEN "IncreaseInst" IN labels(ei1) THEN "Increase"
        WHEN "DecreaseInst" IN labels(ei1) THEN "Decrease"
        ELSE "Change"
    END AS event1,
    ei1.charOffsetBegin as eventBegin1,
    ei1.charOffsetEnd as eventEnd1,

    CASE
        WHEN "IncreaseInst" IN labels(ei2) THEN "Increase"
        WHEN "DecreaseInst" IN labels(ei2) THEN "Decrease"
        ELSE "Change"
    END AS event2,
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
    LIMIT 500
'''

# cooccurrence relation is non-directed
COOCCURS_INST_QUERY = '''
MATCH
    (v1:VariableType) <-[:HAS_VAR]- (ei1:{event1}Inst)
    <-[:HAS_EVENT]- (s:Sentence) -[:HAS_EVENT]->
    (ei2:{event2}Inst) -[:HAS_VAR]-> (v2:VariableType),
    (s) <-[:HAS_SENT]- (a:Article)
    ''' + RELATION_INST_QUERY

# causal relation is directed
CAUSES_INST_QUERY = '''
MATCH
    (v1:VariableType) <-[:HAS_VAR]- (ei1:{event1}Inst)
    <-[:HAS_CAUSE]- (:CausationInst) -[:HAS_EFFECT]->
    (ei2:{event2}Inst) -[:HAS_VAR]-> (v2:VariableType),
    (ei1) <-[:HAS_EVENT]- (s:Sentence) <-[:HAS_SENT]- (a:Article)
    ''' + RELATION_INST_QUERY
