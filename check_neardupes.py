import json, re
from collections import defaultdict

d = json.load(open('library_data.json','r',encoding='utf-8'))
groups = defaultdict(list)
for b in d['books']:
    t = re.sub(r'\s*\([^)]*\)\s*$','',b['title']).strip().lower()
    t = t.split(':')[0].strip()
    key = (t, b['author'].lower())
    groups[key].append(b)

print("=== NEAR-DUPLICATES (by base title before colon) ===")
count = 0
for k,v in sorted(groups.items()):
    if len(v) > 1:
        count += 1
        print(f"\n{k[0]} by {k[1]} ({len(v)} entries)")
        for b in v:
            print(f"  {b['title']} | status={b['status']} rating={b['rating']} owned={b['owned']} review={'Y' if b.get('review') else 'N'}")
print(f"\nTotal near-dup groups: {count}")
