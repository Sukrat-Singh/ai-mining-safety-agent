from langchain_core.documents import Document

def record_to_text(record):
    fields = [
        f"Date: {record.get('date')}",
        f"Mine: {record.get('mine')}",
        f"Owner: {record.get('owner')}",
        f"State: {record.get('state')}",
        f"District: {record.get('district')}",
        f"Persons Killed: {record.get('persons_killed')}",
        f"Narrative: {record.get('narrative')}",
    ]
    return "\n".join([f for f in fields if f is not None])

def clean_metadata(meta: dict):
    simple_meta = {}
    for k, v in meta.items():
        # Skip nested structures (lists, dicts)
        if isinstance(v, (str, int, float, bool)) or v is None:
            simple_meta[k] = v
        else:
            simple_meta[k] = str(v)  # fallback, convert complex to string
    return simple_meta

def records_to_documents(df):
    docs = []
    for _, row in df.iterrows():
        text = record_to_text(row)
        meta = clean_metadata(row.to_dict())
        docs.append(Document(page_content=text, metadata=meta))
    return docs
