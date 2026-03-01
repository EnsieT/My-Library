import json
from collections import Counter, defaultdict
from datetime import datetime

with open('library_data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

books = data['books']
read_books = [b for b in books if b['status'] == 'read' and b.get('date_read')]

# Filter out 2013 for trend analysis
recent_books = [b for b in read_books if b.get('date_read') and not b['date_read'].startswith('2013')]

print('=' * 70)
print("JIGAR'S READING PATTERNS & TRENDS")
print('=' * 70)
print()

# ===== RATING TRENDS OVER TIME =====
print('📊 RATING TRENDS BY YEAR (Excluding 2013)')
print('-' * 70)

rating_by_year = defaultdict(list)
for b in recent_books:
    if b.get('date_read') and b.get('rating') and b['rating'] > 0:
        year = b['date_read'].split('/')[0]
        if year.isdigit():
            rating_by_year[year].append(b['rating'])

for year in sorted(rating_by_year.keys(), reverse=True)[:10]:
    ratings = rating_by_year[year]
    avg = sum(ratings) / len(ratings)
    dist = Counter(ratings)
    print(f"{year}: Avg {avg:.2f}/5 | Books: {len(ratings)} | 5⭐:{dist.get(5,0)} 4⭐:{dist.get(4,0)} 3⭐:{dist.get(3,0)} 2⭐:{dist.get(2,0)} 1⭐:{dist.get(1,0)}")

print()
print('💡 RATING TREND INSIGHT:')
if len(rating_by_year) > 1:
    years_sorted = sorted(rating_by_year.keys())
    early_avg = sum(rating_by_year[years_sorted[0]]) / len(rating_by_year[years_sorted[0]])
    recent_avg = sum(rating_by_year[years_sorted[-1]]) / len(rating_by_year[years_sorted[-1]])
    
    if recent_avg > early_avg + 0.3:
        print(f"   ↗️  Your ratings are TRENDING UP ({early_avg:.2f} → {recent_avg:.2f})")
        print("   You're either picking better books or becoming more generous!")
    elif recent_avg < early_avg - 0.3:
        print(f"   ↘️  Your ratings are TRENDING DOWN ({early_avg:.2f} → {recent_avg:.2f})")
        print("   You're becoming more critical or reading outside your comfort zone!")
    else:
        print(f"   ➡️  Your ratings are CONSISTENT ({early_avg:.2f} → {recent_avg:.2f})")
        print("   You have stable taste over the years!")

print()
print()

# ===== GENRE + RATING CORRELATION =====
print('🎭 HOW YOU RATE DIFFERENT GENRES')
print('-' * 70)

genre_ratings = defaultdict(list)
for b in read_books:
    if b.get('classifications') and b.get('rating') and b['rating'] > 0:
        for c in b['classifications']:
            genre_ratings[c['main']].append(b['rating'])

genre_stats = []
for genre, ratings in genre_ratings.items():
    avg = sum(ratings) / len(ratings)
    count = len(ratings)
    five_star_pct = (ratings.count(5) / count) * 100 if count > 0 else 0
    low_pct = ((ratings.count(1) + ratings.count(2)) / count) * 100 if count > 0 else 0
    genre_stats.append((genre, avg, count, five_star_pct, low_pct))

genre_stats.sort(key=lambda x: x[1], reverse=True)

for genre, avg, count, five_pct, low_pct in genre_stats:
    print(f"{genre:25} Avg: {avg:.2f}/5 | {count:3} books | 5⭐: {five_pct:.0f}% | 1-2⭐: {low_pct:.0f}%")

print()
print('💡 GENRE RATING INSIGHT:')
if genre_stats:
    best_genre = genre_stats[0]
    worst_genre = genre_stats[-1]
    print(f"   🏆 You rate {best_genre[0]} highest (avg {best_genre[1]:.2f}/5)")
    print(f"   😐 You rate {worst_genre[0]} lowest (avg {worst_genre[1]:.2f}/5)")
    
    # Find genre with most 5-stars
    genre_with_most_5stars = max(genre_stats, key=lambda x: x[3])
    if genre_with_most_5stars[3] > 10:
        print(f"   ⭐ {genre_with_most_5stars[3]:.0f}% of your {genre_with_most_5stars[0]} reads are 5-star!")

print()
print()

# ===== READING PATTERNS BY MONTH =====
print('📅 READING PATTERNS BY MONTH (Excluding 2013)')
print('-' * 70)

books_by_month = defaultdict(int)
books_by_month_detail = defaultdict(list)

for b in recent_books:
    if b.get('date_read'):
        parts = b['date_read'].split('/')
        if len(parts) >= 2 and parts[1].isdigit():
            month = int(parts[1])
            books_by_month[month] += 1
            books_by_month_detail[month].append(b['title'])

months = ['', 'January', 'February', 'March', 'April', 'May', 'June', 
          'July', 'August', 'September', 'October', 'November', 'December']

print("Month-by-month breakdown:")
for month_num in range(1, 13):
    count = books_by_month.get(month_num, 0)
    bar = '█' * (count // 2)
    print(f"{months[month_num]:12} {count:3} books {bar}")

print()
print('💡 MONTHLY READING INSIGHT:')
if books_by_month:
    busiest_month = max(books_by_month.items(), key=lambda x: x[1])
    slowest_month = min(books_by_month.items(), key=lambda x: x[1])
    
    print(f"   📚 Busiest: {months[busiest_month[0]]} ({busiest_month[1]} books)")
    print(f"   📉 Slowest: {months[slowest_month[0]]} ({slowest_month[1]} books)")
    
    # Seasonal patterns
    winter = books_by_month.get(12, 0) + books_by_month.get(1, 0) + books_by_month.get(2, 0)
    spring = books_by_month.get(3, 0) + books_by_month.get(4, 0) + books_by_month.get(5, 0)
    summer = books_by_month.get(6, 0) + books_by_month.get(7, 0) + books_by_month.get(8, 0)
    fall = books_by_month.get(9, 0) + books_by_month.get(10, 0) + books_by_month.get(11, 0)
    
    seasons = [('Winter', winter), ('Spring', spring), ('Summer', summer), ('Fall', fall)]
    seasons.sort(key=lambda x: x[1], reverse=True)
    
    print(f"   🍂 Best season: {seasons[0][0]} ({seasons[0][1]} books)")
    print(f"   🌱 Slowest season: {seasons[-1][0]} ({seasons[-1][1]} books)")

print()
print()

# ===== YEAR-OVER-YEAR READING VOLUME =====
print('📈 READING VOLUME TREND (Excluding 2013)')
print('-' * 70)

books_per_year = defaultdict(int)
for b in recent_books:
    if b.get('date_read'):
        year = b['date_read'].split('/')[0]
        if year.isdigit():
            books_per_year[year] += 1

years_list = sorted(books_per_year.keys())
print("Year-to-year reading volume:")
for year in years_list:
    count = books_per_year[year]
    bar = '█' * (count // 2)
    print(f"{year}: {count:3} books {bar}")

print()
print('💡 VOLUME TREND INSIGHT:')
if len(books_per_year) > 2:
    recent_3_years = years_list[-3:] if len(years_list) >= 3 else years_list
    avg_recent = sum(books_per_year[y] for y in recent_3_years) / len(recent_3_years)
    
    older_years = years_list[:-3] if len(years_list) > 3 else years_list[:1]
    avg_older = sum(books_per_year[y] for y in older_years) / len(older_years) if older_years else 0
    
    if avg_recent > avg_older * 1.3:
        print(f"   ↗️  READING MORE: Recent avg {avg_recent:.1f} vs earlier {avg_older:.1f} books/year")
    elif avg_recent < avg_older * 0.7:
        print(f"   ↘️  READING LESS: Recent avg {avg_recent:.1f} vs earlier {avg_older:.1f} books/year")
    else:
        print(f"   ➡️  STABLE PACE: Averaging {avg_recent:.1f} books/year recently")
    
    # Peak year (excluding 2013)
    peak_year = max(books_per_year.items(), key=lambda x: x[1])
    print(f"   🏆 Peak year (post-2013): {peak_year[0]} with {peak_year[1]} books")

print()
print('=' * 70)
