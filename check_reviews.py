import csv

with open('goodreads_library_export.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    cols = reader.fieldnames
    print('COLUMNS:', cols)
    print()
    count = 0
    reviews_found = 0
    all_reviews = []
    for row in reader:
        count += 1
        review = row.get('My Review', '').strip()
        if review:
            reviews_found += 1
            all_reviews.append({
                'title': row.get('Title', ''),
                'author': row.get('Author', ''),
                'rating': row.get('My Rating', ''),
                'review': review
            })
            if reviews_found <= 8:
                print(f"--- {row.get('Title','')} by {row.get('Author','')} ---")
                print(f"Rating: {row.get('My Rating','')}")
                print(f"Review: {review[:300]}")
                print()
    print(f"Total books: {count}")
    print(f"Books with reviews: {reviews_found}")
