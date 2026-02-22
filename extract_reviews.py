"""
Extract all reviews from goodreads CSV and generate JS review data.
Also find any books in CSV not in current goodreadsBooks array.
"""
import csv, json, re

reviews = {}
csv_books = []

with open('goodreads_library_export.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        title = row.get('Title', '').strip()
        author = row.get('Author', '').strip()
        review = row.get('My Review', '').strip()
        rating = int(row.get('My Rating', '0') or '0')
        shelf = row.get('Exclusive Shelf', '').strip()
        date_read = row.get('Date Read', '').strip()
        date_added = row.get('Date Added', '').strip()
        pages = row.get('Number of Pages', '').strip()
        avg_rating = row.get('Average Rating', '').strip()
        
        csv_books.append(title)
        
        if review:
            # Clean review HTML - convert <br/> to \n, strip other tags
            clean = review.replace('<br/>', '\n').replace('<br>', '\n')
            clean = re.sub(r'<[^>]+>', '', clean)
            clean = clean.strip()
            reviews[title] = {
                'author': author,
                'rating': rating,
                'review': clean,
                'date_read': date_read,
                'date_added': date_added,
                'pages': pages,
                'avg_rating': avg_rating
            }

# Write reviews as JSON for embedding
with open('reviews_data.json', 'w', encoding='utf-8') as f:
    json.dump(reviews, f, ensure_ascii=False, indent=2)

print(f"Extracted {len(reviews)} reviews")
print(f"Total CSV books: {len(csv_books)}")

# Print all reviews for JS embedding
print("\n// JS format:")
print("const bookReviews = {")
for title, data in reviews.items():
    escaped_title = title.replace('\\', '\\\\').replace("'", "\\'")
    escaped_review = data['review'].replace('\\', '\\\\').replace("'", "\\'").replace('\n', '\\n')
    print(f"    '{escaped_title}': {{review: '{escaped_review}', dateRead: '{data['date_read']}'}},")
print("};")
