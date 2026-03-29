from datetime import datetime
from typing import Any

PHASE_2_GROUP_ID = 'sri-lanka-news'


async def get_entity_timeline(
    driver,
    entity_name: str,
    group_id: str = PHASE_2_GROUP_ID,
    edge_types: list[str] | None = None,
) -> list[dict[str, Any]]:
    """Return all edges (current + invalidated) for an entity, sorted by valid_at."""
    edge_type_filter = ''
    params: dict[str, Any] = {
        'entity_name': entity_name,
        'group_id': group_id,
    }

    if edge_types:
        edge_type_filter = 'AND e.name IN $edge_types'
        params['edge_types'] = edge_types

    query = f"""
        MATCH (n:Entity {{group_id: $group_id}})-[e:RELATES_TO]-(m:Entity)
        WHERE n.name = $entity_name {edge_type_filter}
        RETURN e.uuid AS uuid,
               e.name AS relation,
               e.fact AS fact,
               e.valid_at AS valid_at,
               e.invalid_at AS invalid_at,
               e.expired_at AS expired_at,
               e.episodes AS episodes,
               n.name AS source,
               m.name AS target,
               e.attributes AS attributes
        ORDER BY e.valid_at ASC
    """

    return await driver.execute_query(query, **params)


async def find_contradictions(
    driver,
    group_id: str = PHASE_2_GROUP_ID,
    entity_name: str | None = None,
    since: datetime | None = None,
) -> list[dict[str, Any]]:
    """Find pairs of edges where a newer fact invalidated an older one."""
    entity_filter = 'AND n.name = $entity_name' if entity_name else ''
    time_filter = 'AND old_edge.expired_at >= $since' if since else ''

    params: dict[str, Any] = {'group_id': group_id}
    if entity_name:
        params['entity_name'] = entity_name
    if since:
        params['since'] = since

    query = f"""
        MATCH (n:Entity {{group_id: $group_id}})-[old_edge:RELATES_TO]->(m:Entity)
        WHERE old_edge.expired_at IS NOT NULL {entity_filter} {time_filter}

        MATCH (n)-[new_edge:RELATES_TO]->(m)
        WHERE new_edge.created_at >= old_edge.expired_at
          AND new_edge.expired_at IS NULL
          AND new_edge.name = old_edge.name

        RETURN n.name AS entity,
               m.name AS target,
               old_edge.name AS relation,
               old_edge.fact AS old_fact,
               old_edge.valid_at AS old_valid_at,
               old_edge.expired_at AS expired_at,
               old_edge.attributes AS old_attributes,
               new_edge.fact AS new_fact,
               new_edge.valid_at AS new_valid_at,
               new_edge.attributes AS new_attributes,
               old_edge.episodes AS old_sources,
               new_edge.episodes AS new_sources
        ORDER BY old_edge.expired_at DESC
    """

    return await driver.execute_query(query, **params)


async def find_recurring_patterns(
    driver,
    group_id: str = PHASE_2_GROUP_ID,
    min_occurrences: int = 2,
    entity_name: str | None = None,
) -> list[dict[str, Any]]:
    """Find relationships that recur across different years."""
    entity_filter = 'AND n.name = $entity_name' if entity_name else ''

    params: dict[str, Any] = {
        'group_id': group_id,
        'min_occurrences': min_occurrences,
    }
    if entity_name:
        params['entity_name'] = entity_name

    query = f"""
        MATCH (n:Entity {{group_id: $group_id}})-[e:RELATES_TO]->(m:Entity)
        WHERE e.valid_at IS NOT NULL {entity_filter}
        WITH n.name AS entity,
             m.name AS target,
             e.name AS relation,
             collect({{
                 fact: e.fact,
                 valid_at: e.valid_at,
                 attributes: e.attributes,
                 episodes: e.episodes,
                 year: date(e.valid_at).year
             }}) AS occurrences
        WHERE size(occurrences) >= $min_occurrences

        WITH entity, target, relation, occurrences,
             [o IN occurrences | o.year] AS years
        WHERE size(apoc.coll.toSet(years)) >= $min_occurrences

        RETURN entity, target, relation, occurrences
        ORDER BY size(occurrences) DESC
    """

    return await driver.execute_query(query, **params)


async def find_source_disagreements(
    driver,
    group_id: str = PHASE_2_GROUP_ID,
    target_name: str | None = None,
) -> list[dict[str, Any]]:
    """Find cases where different sources report different values for the same indicator."""
    target_filter = 'AND target.name = $target_name' if target_name else ''

    params: dict[str, Any] = {'group_id': group_id}
    if target_name:
        params['target_name'] = target_name

    query = f"""
        MATCH (source1:Entity {{group_id: $group_id}})-[e1:RELATES_TO {{name: 'REPORTS_VALUE'}}]->(target:Entity)
        MATCH (source2:Entity {{group_id: $group_id}})-[e2:RELATES_TO {{name: 'REPORTS_VALUE'}}]->(target)
        WHERE source1.uuid <> source2.uuid
          AND e1.expired_at IS NULL AND e2.expired_at IS NULL
          AND abs(duration.between(date(e1.valid_at), date(e2.valid_at)).months) <= 1
          {target_filter}

        RETURN target.name AS indicator,
               source1.name AS source_a,
               e1.fact AS claim_a,
               e1.attributes AS attrs_a,
               source2.name AS source_b,
               e2.fact AS claim_b,
               e2.attributes AS attrs_b,
               e1.valid_at AS date_a,
               e2.valid_at AS date_b
    """

    return await driver.execute_query(query, **params)
