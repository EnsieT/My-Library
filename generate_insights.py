import json
from collections import Counter, defaultdict

with open('library_data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

books = data['books']

# Basic stats
total_books = len(books)
read_books = [b for b in books if b['status'] == 'read']
to_read = [b for b in books if b['status'] == 'to-read']
in_collection = [b for b in books if b['in_collection']]
with_reviews = [b for b in books if b.get('review')]
tracked = [b for b in books if b.get('tracking_status')]

print('=' * 60)
print("JIGAR'S READING INSIGHTS")
print('=' * 60)
print()

# Overall Stats
print('📚 LIBRARY OVERVIEW')
print(f'Total Books Tracked: {total_books}')
print(f'Books Read: {len(read_books)} ({len(read_books)*100//total_books}%)')
print(f'To Read List: {len(to_read)}')
print(f'In Collection: {len(in_collection)}')
print(f'Books with Reviews: {len(with_reviews)}')
print(f'Lent/Lost Books: {len(tracked)}')
print()

# Rating analysis
ratings = [b['rating'] for b in read_books if b['rating'] > 0]
if ratings:
    avg_rating = sum(ratings) / len(ratings)
    rating_dist = Counter(ratings)
    print('⭐ RATING PATTERNS')
    print(f'Average Rating: {avg_rating:.2f}/5')
    print(f'Most Common Rating: {rating_dist.most_common(1)[0][0]} stars ({rating_dist.most_common(1)[0][1]} books)')
    print(f'5-Star Reads: {rating_dist.get(5, 0)} books')
    print(f'4-Star Reads: {rating_dist.get(4, 0)} books')
    print(f'3-Star Reads: {rating_dist.get(3, 0)} books')
    print(f'1-2 Star Reads: {rating_dist.get(1, 0) + rating_dist.get(2, 0)} books')
    print()

# Genre analysis
genres = []
for b in read_books:
    if b.get('classifications'):
        for c in b['classifications']:
            genres.append(c['main'])
genre_count = Counter(genres)
print('📖 GENRE PREFERENCES (Top 5)')
for genre, count in genre_count.most_common(5):
    pct = count * 100 / len(read_books)
    print(f'  {genre}: {count} books ({pct:.1f}%)')
print()

# Author loyalty
authors = [b['author'] for b in books]
author_count = Counter(authors)
print('✍️ FAVORITE AUTHORS (Multiple Books)')
for author, count in author_count.most_common(15):
    if count > 1:
        print(f'  {author}: {count} books')
print()

# Reading by year
years = defaultdict(int)
for b in read_books:
    if b.get('date_read'):
        year = b['date_read'].split('/')[0]
        if year and year.isdigit():
            years[year] += 1
if years:
    print('📅 READING BY YEAR (Last 5 Years)')
    for year in sorted(years.keys(), reverse=True)[:5]:
        print(f'  {year}: {years[year]} books')
    best_year = max(years.items(), key=lambda x: x[1])
    print(f'  🏆 Best Year: {best_year[0]} with {best_year[1]} books!')
    print()

# Page count analysis
pages = [int(b['pages']) for b in read_books if b.get('pages') and str(b['pages']).isdigit()]
if pages:
    total_pages = sum(pages)
    avg_pages = total_pages / len(pages)
    print('📄 PAGE STATISTICS')
    print(f'  Total Pages Read: {total_pages:,}')
    print(f'  Average Book Length: {int(avg_pages)} pages')
    print(f'  Longest Book: {max(pages)} pages')
    print(f'  Shortest Book: {min(pages)} pages')
    print()

# Tracking status
if tracked:
    print('📍 BOOK TRACKING (Lent/Lost)')
    for b in tracked:
        print(f'  • {b["title"][:40]}: {b["tracking_status"]}')
    print()

# Five star favorites
five_star = [b for b in read_books if b['rating'] == 5]
if five_star:
    print(f'🌟 YOUR 5-STAR FAVORITES ({len(five_star)} books)')
    for b in five_star[:10]:
        print(f'  • {b["title"]} - {b["author"]}')
    if len(five_star) > 10:
        print(f'  ... and {len(five_star) - 10} more!')
    print()

# Disappointments
one_two_star = [b for b in read_books if b['rating'] in [1, 2]]
if one_two_star:
    print('😔 BOOKS THAT DISAPPOINTED')
    for b in one_two_star[:5]:
        print(f'  • {b["title"]} ({b["rating"]}⭐)')
    print()

# Quick insights
print('💡 QUICK INSIGHTS')
if len(read_books) > 0:
    review_rate = len(with_reviews) * 100 / len(read_books)
    print(f'  • You write reviews for {review_rate:.0f}% of books you read')
    
if in_collection:
    collection_rate = len(in_collection) * 100 / total_books
    print(f'  • You physically own {collection_rate:.0f}% of your tracked books')
    
if genre_count:
    top_genre = genre_count.most_common(1)[0]
    print(f'  • {top_genre[0]} is clearly your jam ({top_genre[1]} books!)')
    
if avg_rating:
    if avg_rating > 3.5:
        print(f'  • You are a positive reader (avg {avg_rating:.1f}⭐) - you pick books you enjoy!')
    elif avg_rating < 3:
        print(f'  • You are a discerning critic (avg {avg_rating:.1f}⭐)')
        
if pages:
    avg_pages_per_book = sum(pages) / len(pages)
    if avg_pages_per_book > 400:
        print(f'  • You prefer substantial reads (avg {int(avg_pages_per_book)} pages)')
    elif avg_pages_per_book < 250:
        print(f'  • You like concise books (avg {int(avg_pages_per_book)} pages)')

print()
print('=' * 60)
