import json

import requests


def get_qid(work_id):
    """
    Returns the Wikidata QID for a given BDRC work_id.
    If not found, returns None.
    """
    query = f"""
    SELECT ?item WHERE {{
      ?item wdt:P2477 \"{work_id}\" .
    }}
    """
    url = "https://query.wikidata.org/sparql"
    headers = {"Accept": "application/json"}
    try:
        response = requests.get(
            url, params={"query": query}, headers=headers, timeout=10
        )
        response.raise_for_status()
        data = response.json()
        results = data.get("results", {}).get("bindings", [])
        if results:
            return results[0]["item"]["value"].split("/")[-1]
        else:
            print(f"No Wikidata QID found for BDRC work_id: {work_id}")
    except Exception as e:
        print(f"Error fetching QID for {work_id}: {e}")
    return None


def get_wikidata_entity(qid):
    """
    Returns the Wikidata entity data for a given QID.
    If not found, returns None.
    """
    url = f"https://www.wikidata.org/wiki/Special:EntityData/{qid}.json"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error fetching Wikidata entity for QID {qid}: {e}")
        return None


def extract_useful_fields_from_entity(entity_json, qid, language="en", properties=None):
    """
    Extracts label, description, aliases, and specified property values from Wikidata entity JSON.
    Handles missing fields gracefully.
    """
    try:
        entity = entity_json["entities"][qid]
        label = entity.get("labels", {}).get(language, {}).get("value", "")
        description = entity.get("descriptions", {}).get(language, {}).get("value", "")
        aliases = [a["value"] for a in entity.get("aliases", {}).get(language, [])]
        result = {"label": label, "description": description, "aliases": aliases}
        # Extract specified properties if provided
        if properties:
            claims = entity.get("claims", {})
            for prop in properties:
                prop_values = []
                if prop in claims:
                    for claim in claims[prop]:
                        mainsnak = claim.get("mainsnak", {})
                        datavalue = mainsnak.get("datavalue", {})
                        value = datavalue.get("value")
                        # For entity references, extract the QID
                        if isinstance(value, dict) and "id" in value:
                            prop_values.append(value["id"])
                        else:
                            prop_values.append(value)
                result[prop] = prop_values
        return result
    except Exception as e:
        print(f"Error extracting fields from entity for QID {qid}: {e}")
        return {"qid": qid, "label": "", "description": "", "aliases": []}


def get_wikidata_metadata(work_id, language="en", properties=None):
    """
    Combines the above functions to return useful metadata for a BDRC work_id.
    Returns None if not found or on error.
    """
    qid = get_qid(work_id)
    if not qid:
        print(f"No QID found for work_id: {work_id}")
        return None
    entity = get_wikidata_entity(qid)
    if not entity:
        print(f"No Wikidata entity found for QID: {qid}")
        return None
    return extract_useful_fields_from_entity(entity, qid, language, properties)


def main():
    work_id = "WA0RK0529"
    metadata = get_wikidata_metadata(
        work_id, language="en", properties=["P31", "P4969", "P1476"]
    )
    print(json.dumps(metadata, indent=2, ensure_ascii=False))
    author_id = "P1215"
    author_metadata = get_wikidata_metadata(
        author_id, language="en", properties=["P31", "P4969", "P1476"]
    )
    print(json.dumps(author_metadata, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
