import json
from collections import Counter, defaultdict

with open('library_data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

books = data['books']

# Group books by time periods (excluding 2013)
periods = {
    'Early Years (2014-2017)': [],
    'Middle Years (2018-2021)': [],
    'Recent Years (2022-2026)': []
}

for b in books:
    if b['status'] == 'read' and b.get('date_read'):
        year = b['date_read'].split('/')[0]
        if year.isdigit() and year != '2013':
            year_int = int(year)
            if 2014 <= year_int <= 2017:
                periods['Early Years (2014-2017)'].append(b)
            elif 2018 <= year_int <= 2021:
                periods['Middle Years (2018-2021)'].append(b)
            elif 2022 <= year_int <= 2026:
                periods['Recent Years (2022-2026)'].append(b)

print('=' * 80)
print("HOW JIGAR'S READING TASTE HAS EVOLVED")
print('=' * 80)
print()

# ===== GENRE EVOLUTION =====
print('📚 GENRE PREFERENCES BY PERIOD')
print('-' * 80)
print()

for period_name, period_books in periods.items():
    if not period_books:
        continue
    
    print(f"{period_name} ({len(period_books)} books)")
    
    genres = []
    for b in period_books:
        if b.get('classifications'):
            for c in b['classifications']:
                genres.append(c['main'])
    
    genre_count = Counter(genres)
    total = len(period_books)
    
    for genre, count in genre_count.most_common():
        pct = (count / total) * 100
        bar = '█' * int(pct / 5)
        print(f"  {genre:25} {count:3} books ({pct:5.1f}%) {bar}")
    print()

print('💡 GENRE EVOLUTION INSIGHT:')
# Calculate genre shifts
early_genres = Counter()
middle_genres = Counter()
recent_genres = Counter()

for b in periods['Early Years (2014-2017)']:
    if b.get('classifications'):
        for c in b['classifications']:
            early_genres[c['main']] += 1

for b in periods['Middle Years (2018-2021)']:
    if b.get('classifications'):
        for c in b['classifications']:
            middle_genres[c['main']] += 1

for b in periods['Recent Years (2022-2026)']:
    if b.get('classifications'):
        for c in b['classifications']:
            recent_genres[c['main']] += 1

early_total = sum(early_genres.values())
middle_total = sum(middle_genres.values())
recent_total = sum(recent_genres.values())

if early_total > 0 and recent_total > 0:
    # Check Fiction trend
    early_fiction_pct = (early_genres.get('Fiction', 0) / early_total) * 100
    recent_fiction_pct = (recent_genres.get('Fiction', 0) / recent_total) * 100
    
    if abs(early_fiction_pct - recent_fiction_pct) > 10:
        if recent_fiction_pct > early_fiction_pct:
            print(f"   📖 Reading MORE Fiction: {early_fiction_pct:.0f}% → {recent_fiction_pct:.0f}%")
        else:
            print(f"   📖 Reading LESS Fiction: {early_fiction_pct:.0f}% → {recent_fiction_pct:.0f}%")
    
    # Check Non-Fiction trend
    early_nf_pct = (early_genres.get('Non-Fiction', 0) / early_total) * 100
    recent_nf_pct = (recent_genres.get('Non-Fiction', 0) / recent_total) * 100
    
    if abs(early_nf_pct - recent_nf_pct) > 10:
        if recent_nf_pct > early_nf_pct:
            print(f"   📰 Reading MORE Non-Fiction: {early_nf_pct:.0f}% → {recent_nf_pct:.0f}%")
        else:
            print(f"   📰 Reading LESS Non-Fiction: {early_nf_pct:.0f}% → {recent_nf_pct:.0f}%")

print()
print()

# ===== CATEGORY/SUBGENRE EVOLUTION =====
print('🎭 DETAILED CATEGORY EVOLUTION')
print('-' * 80)
print()

for period_name, period_books in periods.items():
    if not period_books:
        continue
    
    print(f"{period_name}")
    
    categories = []
    for b in period_books:
        if b.get('category'):
            categories.append(b['category'])
    
    cat_count = Counter(categories)
    
    for cat, count in cat_count.most_common(10):
        print(f"  {cat[:50]:50} {count:2} books")
    print()

print('💡 CATEGORY INSIGHT:')
# Find new interests
early_cats = set()
recent_cats = set()

for b in periods['Early Years (2014-2017)']:
    if b.get('category'):
        early_cats.add(b['category'])

for b in periods['Recent Years (2022-2026)']:
    if b.get('category'):
        recent_cats.add(b['category'])

new_interests = recent_cats - early_cats
faded_interests = early_cats - recent_cats

if new_interests:
    print("   ✨ NEW interests in recent years:")
    for cat in list(new_interests)[:5]:
        print(f"      • {cat}")

if faded_interests:
    print("   👋 Categories you've MOVED AWAY from:")
    for cat in list(faded_interests)[:5]:
        print(f"      • {cat}")

print()
print()

# ===== AUTHOR LOYALTY EVOLUTION =====
print('✍️ AUTHOR PREFERENCES BY PERIOD')
print('-' * 80)
print()

for period_name, period_books in periods.items():
    if not period_books:
        continue
    
    print(f"{period_name}")
    
    authors = [b['author'] for b in period_books]
    author_count = Counter(authors)
    
    multi_book_authors = [(a, c) for a, c in author_count.most_common() if c > 1]
    
    if multi_book_authors:
        for author, count in multi_book_authors[:8]:
            print(f"  {author[:40]:40} {count} books")
    else:
        print("  (No repeat authors this period)")
    print()

print('💡 AUTHOR EVOLUTION INSIGHT:')

# Find constantly loved authors
early_authors = Counter([b['author'] for b in periods['Early Years (2014-2017)']])
middle_authors = Counter([b['author'] for b in periods['Middle Years (2018-2021)']])
recent_authors = Counter([b['author'] for b in periods['Recent Years (2022-2026)']])

consistent_loves = []
for author in set(early_authors.keys()) & set(middle_authors.keys()) & set(recent_authors.keys()):
    total = early_authors[author] + middle_authors[author] + recent_authors[author]
    if total >= 3:
        consistent_loves.append((author, total))

if consistent_loves:
    consistent_loves.sort(key=lambda x: x[1], reverse=True)
    print("   💚 Authors you've CONSISTENTLY read across all periods:")
    for author, count in consistent_loves[:5]:
        print(f"      • {author} ({count} books total)")

# New author discoveries
new_authors_recent = set(recent_authors.keys()) - set(early_authors.keys()) - set(middle_authors.keys())
if new_authors_recent and recent_authors:
    new_with_multi = [(a, recent_authors[a]) for a in new_authors_recent if recent_authors[a] > 1]
    if new_with_multi:
        new_with_multi.sort(key=lambda x: x[1], reverse=True)
        print("   🆕 NEW author discoveries (recent period, multiple books):")
        for author, count in new_with_multi[:5]:
            print(f"      • {author} ({count} books)")

print()
print()

# ===== PAGE LENGTH PREFERENCES =====
print('📏 BOOK LENGTH PREFERENCES BY PERIOD')
print('-' * 80)
print()

for period_name, period_books in periods.items():
    if not period_books:
        continue
    
    pages = [int(b['pages']) for b in period_books if b.get('pages') and str(b['pages']).isdigit()]
    
    if pages:
        avg = sum(pages) / len(pages)
        longest = max(pages)
        shortest = min(pages)
        
        print(f"{period_name}")
        print(f"  Average length: {int(avg)} pages")
        print(f"  Longest: {longest} pages | Shortest: {shortest} pages")
        
        # Categorize by length
        short = len([p for p in pages if p < 250])
        medium = len([p for p in pages if 250 <= p < 400])
        long_books = len([p for p in pages if p >= 400])
        
        print(f"  Short (<250): {short} | Medium (250-400): {medium} | Long (400+): {long_books}")
        print()

print('💡 PAGE LENGTH INSIGHT:')
early_pages = [int(b['pages']) for b in periods['Early Years (2014-2017)'] 
               if b.get('pages') and str(b['pages']).isdigit()]
recent_pages = [int(b['pages']) for b in periods['Recent Years (2022-2026)'] 
                if b.get('pages') and str(b['pages']).isdigit()]

if early_pages and recent_pages:
    early_avg = sum(early_pages) / len(early_pages)
    recent_avg = sum(recent_pages) / len(recent_pages)
    
    if recent_avg > early_avg + 50:
        print(f"   📚 Reading LONGER books: {int(early_avg)} → {int(recent_avg)} pages avg")
    elif recent_avg < early_avg - 50:
        print(f"   ⚡ Reading SHORTER books: {int(early_avg)} → {int(recent_avg)} pages avg")
    else:
        print(f"   ➡️  Consistent length preference: ~{int(recent_avg)} pages avg")

print()
print('=' * 80)
