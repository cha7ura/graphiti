from typing import Any


async def get_topic_page(
    driver,
    topic_name: str,
    group_ids: list[str] | None = None,
) -> list[dict[str, Any]]:
    """Get all claims, protocols, studies, and products related to a topic."""
    group_filter = 'AND n.group_id IN $group_ids' if group_ids else ''

    params: dict[str, Any] = {'topic_name': topic_name}
    if group_ids:
        params['group_ids'] = group_ids

    query = f"""
        MATCH (g:Guest)-[e:RELATES_TO {{name: 'MAKES_CLAIM'}}]->(t:Topic)
        WHERE t.name = $topic_name {group_filter}
        OPTIONAL MATCH (g)-[ref:RELATES_TO {{name: 'REFERENCES_STUDY'}}]->(s:Study)
        OPTIONAL MATCH (t)-[rel:RELATES_TO {{name: 'RELATES_TO'}}]->(sub:Topic)
        RETURN g.name AS guest,
               e.fact AS fact,
               e.attributes AS claim_attributes,
               e.episodes AS episodes,
               s.name AS study_name,
               s.attributes AS study_attributes,
               sub.name AS related_topic,
               rel.attributes AS relation_attributes
        ORDER BY g.name
    """

    return await driver.execute_query(query, **params)


async def get_guest_profile(
    driver,
    guest_name: str,
) -> list[dict[str, Any]]:
    """Get a guest's full profile — appearances, claims, protocols, recommendations."""
    query = """
        MATCH (g:Guest {name: $guest_name})-[e:RELATES_TO]->(target)
        RETURN e.name AS relation,
               e.fact AS fact,
               e.attributes AS attributes,
               e.episodes AS episodes,
               target.name AS target_name,
               labels(target) AS target_labels
        ORDER BY e.name, e.valid_at ASC
    """

    return await driver.execute_query(query, guest_name=guest_name)


async def find_agreements_and_disagreements(
    driver,
    topic_name: str | None = None,
) -> list[dict[str, Any]]:
    """Find topics where multiple guests agree or disagree."""
    topic_filter = 'AND t.name = $topic_name' if topic_name else ''

    params: dict[str, Any] = {}
    if topic_name:
        params['topic_name'] = topic_name

    query = f"""
        MATCH (g:Guest)-[e:RELATES_TO {{name: 'MAKES_CLAIM'}}]->(t:Topic)
        WHERE e.expired_at IS NOT NULL {topic_filter}

        MATCH (g2:Guest)-[e2:RELATES_TO {{name: 'MAKES_CLAIM'}}]->(t)
        WHERE e2.created_at >= e.expired_at
          AND e2.expired_at IS NULL
          AND g2.uuid <> g.uuid

        RETURN t.name AS topic,
               g.name AS original_guest,
               e.fact AS original_claim,
               e.attributes AS original_attributes,
               g2.name AS contradicting_guest,
               e2.fact AS contradicting_claim,
               e2.attributes AS contradicting_attributes,
               e.expired_at AS expired_at
        ORDER BY e.expired_at DESC
    """

    return await driver.execute_query(query, **params)


async def get_cross_podcast_insights(
    driver,
    guest_name: str,
) -> list[dict[str, Any]]:
    """Find what a guest said across different podcast appearances."""
    query = """
        MATCH (g:Guest {name: $guest_name})-[a:RELATES_TO {name: 'APPEARS_ON'}]->(p:Podcast)
        MATCH (g)-[e:RELATES_TO {name: 'MAKES_CLAIM'}]->(t:Topic)
        RETURN p.name AS podcast,
               a.attributes AS appearance_attributes,
               t.name AS topic,
               e.fact AS claim,
               e.attributes AS claim_attributes,
               e.valid_at AS valid_at
        ORDER BY p.name, e.valid_at ASC
    """

    return await driver.execute_query(query, guest_name=guest_name)


async def get_most_referenced_studies(
    driver,
    group_ids: list[str] | None = None,
    limit: int = 20,
) -> list[dict[str, Any]]:
    """Find studies referenced by the most guests across podcasts."""
    group_filter = 'AND g.group_id IN $group_ids' if group_ids else ''

    params: dict[str, Any] = {'limit': limit}
    if group_ids:
        params['group_ids'] = group_ids

    query = f"""
        MATCH (g:Guest)-[e:RELATES_TO {{name: 'REFERENCES_STUDY'}}]->(s:Study)
        {group_filter}
        WITH s, count(DISTINCT g) AS guest_count,
             collect(DISTINCT g.name) AS citing_guests,
             collect(DISTINCT e.attributes) AS reference_contexts
        RETURN s.name AS study_name,
               s.attributes AS study_attributes,
               guest_count,
               citing_guests,
               reference_contexts
        ORDER BY guest_count DESC
        LIMIT $limit
    """

    return await driver.execute_query(query, **params)


async def get_protocol_comparison(
    driver,
    topic_name: str,
) -> list[dict[str, Any]]:
    """Find all protocols related to a topic and compare across guests."""
    query = """
        MATCH (g:Guest)-[e:RELATES_TO {name: 'DESCRIBES_PROTOCOL'}]->(p:Protocol)
        MATCH (p)-[:RELATES_TO {name: 'RELATES_TO'}]->(t:Topic)
        WHERE t.name = $topic_name
        RETURN g.name AS guest,
               p.name AS protocol_name,
               p.attributes AS protocol_attributes,
               e.fact AS description,
               e.attributes AS edge_attributes
        ORDER BY g.name
    """

    return await driver.execute_query(query, topic_name=topic_name)
