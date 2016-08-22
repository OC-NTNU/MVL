"""
Cypher queries
"""

# TODO: remove hard-coded LIMIT cases
# TODO: lower case relation name: lower?

EVENT_TYPE_QUERY = '''
MATCH
    (ve:VarEvent)
WITH
    ve.n AS eventCount,
    CASE
        WHEN "VarIncrease" IN labels(ve) THEN "Increase"
        WHEN "VarDecrease" IN labels(ve) THEN "Decrease"
        ELSE "Change"
    END AS event,
    ve.subStr AS variable,
    id(ve) AS nodeId
WHERE
    {}
RETURN
    eventCount,
    event,
    variable,
    nodeId
    ORDER BY eventCount DESC
    LIMIT 500
'''

# EVENT_INST_QUERY = '''
# MATCH
#     (ve:VarEvent) -[:INST]-> (e:Event) <-[:HAS_EVENT]- (s:Sentence)
#     <-[:HAS_SENT]- (a:Article)
# WHERE
#     id(ve) IN {}
# WITH
#     CASE
#         WHEN "VarIncrease" IN labels(ve) THEN "Increase"
#         WHEN "VarDecrease" IN labels(ve) THEN "Decrease"
#         ELSE "Change"
#     END AS event,
#     e.charOffsetBegin as eventBegin,
#     e.charOffsetEnd as eventEnd,
#     e.extractName as eventPattern,
#     s.charOffsetBegin as sentBegin,
#     s.sentChars as sentence,
#     a.doi as doi,
#     a.author as author,
#     a.title as title,
#     a.year as year,
#     a.journal as journal,
#     a.volume as volume
# RETURN
#     event,
#     eventBegin,
#     eventEnd,
#     eventPattern,
#     sentBegin,
#     sentence,
#     doi,
#     author,
#     title,
#     year,
#     journal,
#     volume
#     ORDER BY year DESC
#     LIMIT 500
# '''

EVENT_INST_QUERY = '''
MATCH
    (ve:VarEvent) -[:INST]-> (e:Event) <-[:HAS_EVENT]- (s:Sentence)
    <-[:HAS_SENT]- (a:Article)
WHERE
    id(ve) IN {}
WITH
    CASE
        WHEN "VarIncrease" IN labels(ve) THEN "Increase"
        WHEN "VarDecrease" IN labels(ve) THEN "Decrease"
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

RELATION_TYPE_QUERY = '''
MATCH
    (ve1:VarEvent) -[r:COOCCURS]- (ve2:VarEvent)
WITH
    CASE
        WHEN "VarIncrease" IN labels(ve1) THEN "Increase"
        WHEN "VarDecrease" IN labels(ve1) THEN "Decrease"
        ELSE "Change"
    END AS event1,
    ve1.subStr AS variable1,
    id(ve1) AS nodeId1,

    CASE
        WHEN "VarIncrease" IN labels(ve2) THEN "Increase"
        WHEN "VarDecrease" IN labels(ve2) THEN "Decrease"
        ELSE "Change"
    END AS event2,
    ve2.subStr AS variable2,
    id(ve2) AS nodeId2,

    type(r) as relation,
    r.n as relationCount,
    id(r) as relationId
WHERE
    {}
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

# RELATION_INST_QUERY = '''
# MATCH
#     (ve1:VarEvent) -[:INST]-> (e1:Event) <-[:HAS_EVENT]- (s:Sentence)
#     -[:HAS_EVENT]-> (e2:Event) <-[:INST]- (ve2:VarEvent),
#     (s) <-[:HAS_SENT]- (a:Article)
# WHERE
#     id(ve1) = {id1} AND id(ve2) = {id2}
# WITH
#     CASE
#         WHEN "VarIncrease" IN labels(ve1) THEN "Increase"
#         WHEN "VarDecrease" IN labels(ve1) THEN "Decrease"
#         ELSE "Change"
#     END AS event1,
#     e1.charOffsetBegin as eventBegin1,
#     e1.charOffsetEnd as eventEnd1,
#
#     CASE
#         WHEN "VarIncrease" IN labels(ve2) THEN "Increase"
#         WHEN "VarDecrease" IN labels(ve2) THEN "Decrease"
#         ELSE "Change"
#     END AS event2,
#     e2.charOffsetBegin as eventBegin2,
#     e2.charOffsetEnd as eventEnd2,
#
#     s.charOffsetBegin as sentBegin,
#     s.sentChars as sentence,
#
#     a.doi as doi,
#     a.author as author,
#     a.title as title,
#     a.year as year,
#     a.journal as journal,
#     a.volume as volume
# RETURN
#     event1,
#     eventBegin1,
#     eventEnd1,
#     event2,
#     eventBegin2,
#     eventEnd2,
#     sentBegin,
#     sentence,
#     doi,
#     author,
#     title,
#     year,
#     journal,
#     volume
#     ORDER BY year DESC
#     LIMIT 500
# '''

RELATION_INST_QUERY = '''
MATCH
    (ve1:VarEvent) -[:INST]-> (e1:Event) <-[:HAS_EVENT]- (s:Sentence)
    -[:HAS_EVENT]-> (e2:Event) <-[:INST]- (ve2:VarEvent),
    (s) <-[:HAS_SENT]- (a:Article)
WHERE
    id(ve1) = {id1} AND id(ve2) = {id2}
WITH
    CASE
        WHEN "VarIncrease" IN labels(ve1) THEN "Increase"
        WHEN "VarDecrease" IN labels(ve1) THEN "Decrease"
        ELSE "Change"
    END AS event1,
    e1.charOffsetBegin as eventBegin1,
    e1.charOffsetEnd as eventEnd1,

    CASE
        WHEN "VarIncrease" IN labels(ve2) THEN "Increase"
        WHEN "VarDecrease" IN labels(ve2) THEN "Decrease"
        ELSE "Change"
    END AS event2,
    e2.charOffsetBegin as eventBegin2,
    e2.charOffsetEnd as eventEnd2,

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