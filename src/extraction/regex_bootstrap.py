# src/extraction/regex_bootstrap.py
import re
from src.storage.schema import AccidentRecord, Victim

# Pattern to split record blocks
REC_SPLIT = re.compile(r"\n\s*\d+\.\s*Date\s*-\s*", re.I)

FIELD_PATS = {
    "date": re.compile(r"Date\s*-\s*([0-9/.-]+)", re.I),
    "time": re.compile(r"Time\s*-\s*([0-9:. ]+)", re.I),
    "mine": re.compile(r"Mine\s*-\s*(.+?)\n", re.I),
    "owner": re.compile(r"Owner\s*-\s*(.+?)\n", re.I),
    "district": re.compile(r"Dist\.\s*-\s*(.+?),", re.I),
    "state": re.compile(r"State\s*-\s*([A-Za-z .-]+)", re.I),
    "persons": re.compile(r"Person\(s\)\s*Killed\s*:(.+?)(?:\n\n|\Z)", re.I | re.S)
}

VICTIM_PAT = re.compile(
    r"\d+\.\s*([^,]+),\s*([^,]+),\s*(Male|Female),\s*(\d+)\s*Years",
    re.I
)

def split_records(text: str):
    parts = REC_SPLIT.split("\n" + text)
    blocks = [parts[i+1] for i in range(0, len(parts)-1, 2)]
    return blocks

def parse_victims(block: str):
    victims = []
    m = FIELD_PATS["persons"].search(block)
    if not m:
        return victims
    for name, role, gender, age in VICTIM_PAT.findall(m.group(1)):
        victims.append(
            Victim(name=name.strip(), role=role.strip(), gender=gender.strip(), age=int(age))
        )
    return victims

def parse_block(block: str, source_file: str) -> AccidentRecord:
    vals = {
        key: (FIELD_PATS[key].search(block).group(1).strip()
              if FIELD_PATS[key].search(block) else None)
        for key in FIELD_PATS
    }

    victims = parse_victims(block)
    persons_killed = max(len(victims), 1 if vals["persons"] else 0)

    return AccidentRecord(
        date=vals["date"] or "",
        time=vals["time"],
        mine=vals["mine"],
        owner=vals["owner"],
        district=vals["district"],
        state=vals["state"],
        code=None,
        cause=None,
        narrative=block.strip(),
        prevention=None,
        persons_killed=persons_killed,
        victims=victims,
        source_doc=source_file,
        page_span=[]
    )
