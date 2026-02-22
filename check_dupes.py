import json, re
from collections import defaultdict

data = json.load(open('library_data.json', 'r', encoding='utf-8'))
books = data['books']

def norm(t):
    return re.sub(r'\s*\([^)]*\)\s*$', '', t).strip().lower()

groups = defaultdict(list)
for b in books:
    key = (norm(b['title']), b['author'].lower())
    groups[key].append(b)

print('=== DUPLICATE GROUPS ===')
dupe_count = 0
extra = 0
for key, blist in sorted(groups.items()):
    if len(blist) > 1:
        dupe_count += 1
        extra += len(blist) - 1
        print(f"\nGroup: {key[0]} by {key[1]} ({len(blist)} entries)")
        for b in blist:
            print(f"  Title: {b['title']}")
            r = "Yes" if b.get('review') else "No"
            print(f"    Status={b['status']}, Rating={b['rating']}, Owned={b['owned']}, Review={r}, DateRead={b.get('date_read','')}, Pages={b.get('pages','')}")

print(f"\nTotal groups with dupes: {dupe_count}")
print(f"Total extra entries: {extra}")
