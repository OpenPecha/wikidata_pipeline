import json

from wikidata_pipeline.wikidata_bdrc_utils import get_wikidata_metadata


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
