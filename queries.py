"""
Cypher queries
"""

# TODO: remove hard-coded LIMIT cases
# TODO: lower case relation name: lower?


# -------------------------------------------------------------------------------
# Event types query
# -------------------------------------------------------------------------------

# Motivation for use of UNWIND:
#   1. Reuse of event type query for relation type query
#   2. Proper sorting (in contrast with UNION)
# cf. https://neo4j.com/blog/cypher-union-query-using-collect-clause/


EVENT_TYPE_DIRECT = '''
OPTIONAL MATCH
    (v:VariableType) <-[:HAS_VAR]- (e:EventType)
WHERE
    {where}
WITH
    collect(id(e)) as eventsDirect'''

EVENT_TYPE_WITH_SPEC = '''
OPTIONAL MATCH
    (v:VariableType) <-[:TENTAILS_VAR*]-
    (VariableType) <-[:HAS_VAR]- (e:EventType)
WHERE
    {where}
WITH
    eventsDirect,
    collect(id(e)) as eventsSpec'''

EVENT_TYPE_WITHOUT_SPEC = '''
    , [] as eventsSpec'''

EVENT_TYPE_WITH_GEN = '''
OPTIONAL MATCH
    (v:VariableType) -[:TENTAILS_VAR*]->
    (VariableType) <-[:HAS_VAR]- (e:EventType)
WHERE
    {where}
WITH
	eventsDirect,
	eventsSpec,
	collect(id(e)) as eventsGen'''

EVENT_TYPE_WITHOUT_GEN = '''
	, [] as eventsGen'''

EVENT_TYPE_UNWIND = '''
UNWIND
	eventsDirect + eventsSpec + eventsGen as eventId
MATCH
	(v:VariableType) <-[:HAS_VAR]- (e:EventType)
WHERE
	id(e) = eventId
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
    LIMIT 500'''

# -------------------------------------------------------------------------------
# Event instances query
# -------------------------------------------------------------------------------

EVENT_INST_QUERY = '''
MATCH
    (v:VariableType) <-[:HAS_VAR]- (e:{event_direction}Inst)
    <-[:HAS_EVENT]- (s:Sentence) <-[:HAS_SENT]- (a:Article)
WHERE
    v.subStr = "{variable_string}"
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
    LIMIT 500
'''

# ------------------------------------------------------------------------------
# Relations type query
# ------------------------------------------------------------------------------


RELATION_TYPE_QUERY = '''
{event_type_1_query}
WITH
    eventsDirect + eventsSpec + eventsGen AS eventTypeIds1
{event_type_2_query}
WITH
    eventTypeIds1,
    eventsDirect + eventsSpec + eventsGen AS eventTypeIds2
UNWIND
    eventTypeIds1 as id1
MATCH
    (v1:VariableType) <-[:HAS_VAR]- (et1:EventType)
    -[r:{relation}]-{direction}
    (et2:EventType) -[:HAS_VAR]-> (v2:VariableType)
WHERE
    {where} AND
    id(et1) = id1 AND
    id(et2) IN eventTypeIds2
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

    type(r) AS relation,
    r.n AS relationCount,
    id(r) AS relationId,
    et1.n AS eventCount1,
    et2.n AS eventCount2
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
    LIMIT 500'''



# ------------------------------------------------------------------------------
# Relations type query
# ------------------------------------------------------------------------------


# cooccurrence relation is non-directed
COOCCURS_INST_MATCH = '''
MATCH
    (v1:VariableType) <-[:HAS_VAR]- (ei1:{event1}Inst)
    <-[:HAS_EVENT]- (s:Sentence) -[:HAS_EVENT]->
    (ei2:{event2}Inst) -[:HAS_VAR]-> (v2:VariableType),
    (s) <-[:HAS_SENT]- (a:Article)
    '''

# causal relation is directed
CAUSES_INST_MATCH = '''
MATCH
    (v1:VariableType) <-[:HAS_VAR]- (ei1:{event1}Inst)
    <-[:HAS_CAUSE]- (:CausationInst) -[:HAS_EFFECT]->
    (ei2:{event2}Inst) -[:HAS_VAR]-> (v2:VariableType),
    (ei1) <-[:HAS_EVENT]- (s:Sentence) <-[:HAS_SENT]- (a:Article)
    '''

RELATION_INST_QUERY = '''
WHERE
    v1.subStr = "{variable1}" AND v2.subStr = "{variable2}"
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

