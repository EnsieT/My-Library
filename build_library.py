#!/usr/bin/env python3
"""
=============================================================================
  BUILD LIBRARY DATA
  ------------------
  This script reads your Goodreads export CSV and owned-books file (books.txt),
  merges them, applies category taxonomy, extracts reviews, and writes
  library_data.json which index.html loads.

  TO MODIFY YOUR LIBRARY:
    - Edit the sections below marked with >>>
    - Re-run:  python build_library.py
    - Refresh index.html in browser
=============================================================================
"""

import csv, json, re, os, sys
from collections import defaultdict

# ==========================================================================
# >>> CONFIGURATION — edit these paths if needed
# ==========================================================================
GOODREADS_CSV   = "goodreads_library_export.csv"
OWNED_BOOKS_TXT = "books.txt"
OUTPUT_FILE     = "library_data.json"

# ==========================================================================
# >>> BOOK OVERRIDES — add, remove, or modify individual books here
#     Each entry overrides or adds a book. Set _delete: True to remove.
# ==========================================================================
BOOK_OVERRIDES = [
    # Remove First Lie Wins
    {"title": "First Lie Wins", "_delete": True},

    # Add Miguel Street as currently reading
    {
        "title": "Miguel Street",
        "author": "V.S. Naipaul",
        "rating": 0,
        "status": "currently-reading",
        "category_override": "Fiction/Literary Fiction",
    },

    # Example: to change a book's category or rating, add an entry:
    # {"title": "Some Book Title", "rating": 5, "category_override": "Fiction/Thriller"},
]

# ==========================================================================
# >>> MAIN CATEGORY TAXONOMY
#     Maps subcategories to their main category.
#     Books can appear under multiple main categories if their subcategory
#     string contains multiple parts (e.g. "Fiction/Spirituality").
# ==========================================================================
MAIN_CATEGORIES = {
    "Fiction": [
        "Fiction", "Magical Realism", "Mythology", "Horror", "Fantasy",
        "Short Stories", "Classics", "Science Fiction", "Humor", "Satire",
        "Dystopian", "Historical", "Thriller", "Literary Fiction",
        "Sci-Fi", "Mystery", "Romance", "Adventure", "Fable",
    ],
    "Non-Fiction": [
        "Non-Fiction", "History", "Science", "Philosophy", "Psychology",
        "Neuroscience", "Programming", "Finance", "Futurology", "Nature",
        "Geography", "Politics", "Biography", "Self-Help", "Memoir",
        "Economics", "Business", "Technology", "Health",
    ],
    "Spirituality & Religion": [
        "Spirituality", "Religion", "Inspirational", "Poetry",
        "Yoga", "Meditation", "Vedanta", "Gita",
    ],
}

# ==========================================================================
# >>> CATEGORY ASSIGNMENTS for books that come from Goodreads without one
#     Key = book title (exact match), Value = category string
# ==========================================================================
CATEGORY_ASSIGNMENTS = {
    "Dance Dance Dance": "Fiction/Magical Realism",
    "Never Let Me Go": "Fiction/Literary Fiction",
    "Don't Lose Your Mind, Lose Your Weight": "Non-Fiction/Health",
    "Siddhartha": "Fiction/Philosophy",
    "The Myth of Sisyphus": "Non-Fiction/Philosophy",
    "The Hitchhiker's Guide to the Galaxy": "Fiction/Science Fiction/Humor",
    "The Ocean of Churn": "Non-Fiction/History",
    "The Will to Meaning": "Non-Fiction/Psychology",
    "India in the Age of Ideas": "Non-Fiction/History",
    "Quichotte": "Fiction/Literary Fiction",
    "After Dark": "Fiction/Magical Realism",
    "The Secret Garden": "Fiction/Classics",
    "Joy in the Morning (Jeeves, #8)": "Fiction/Humor",
    "The Last Lecture": "Non-Fiction/Memoir",
    "Atomic Habits": "Non-Fiction/Self-Help",
    "Sapiens": "Non-Fiction/History",
    "Fahrenheit 451": "Fiction/Dystopian",
    "Dracula": "Fiction/Classics",
    "The Krishna Key": "Fiction/Thriller",
    "Krishna's Secret": "Fiction/Mythology",
    "Keepers of the Kalachakra": "Fiction/Thriller",
    "Ikigai": "Non-Fiction/Self-Help/Philosophy",
    "Land of the Seven Rivers": "Non-Fiction/History/Geography",
    "One Hundred Years of Solitude": "Fiction/Magical Realism",
    "The Valmiki Ramayana Vol. 3": "Spirituality/Religion",
    "Why We Sleep": "Non-Fiction/Science",
    "The Mahabharata: Volume 1": "Spirituality/Religion",
    "Man's Search for Meaning": "Non-Fiction/Psychology",
    "As a Man Thinketh": "Self-Help/Philosophy",
    "21 Lessons for the 21st Century": "Non-Fiction/Philosophy",
    "Submission": "Fiction/Literary Fiction",
    "A Gentleman in Moscow": "Fiction/Historical",
    "Uncle Dynamite": "Fiction/Humor",
    "1984": "Fiction/Dystopian",
    "Homo Deus": "Non-Fiction/Futurology",
    "The Four": "Non-Fiction/Business",
    "Summer Lightning": "Fiction/Humor",
    "Five Point Someone": "Fiction/Literary Fiction",
    "Something Fresh": "Fiction/Humor",
    "Wings of Fire": "Non-Fiction/Biography/Memoir",
    "Angels & Demons": "Fiction/Thriller",
    "Deception Point": "Fiction/Thriller",
    "Rich Dad, Poor Dad": "Non-Fiction/Finance",
    "The Seventh Secret": "Fiction/Thriller",
    "Digital Fortress": "Fiction/Thriller",
    "Rich Dad's Cashflow Quadrant": "Non-Fiction/Finance",
    "Illusions": "Fiction/Spirituality",
    "The Stranger": "Fiction/Philosophy",
    "The Mahabharata Secret": "Fiction/Thriller",
    "Jonathan Livingston Seagull": "Fiction/Fable/Spirituality",
    "Service With a Smile": "Fiction/Humor",
    "Rumi": "Poetry/Spirituality",
    "Kalki Purana": "Spirituality/Religion",
    "Robots and Empire": "Fiction/Science Fiction",
    "A Column of Fire": "Fiction/Historical",
    "House of Leaves": "Fiction/Horror",
    "The Metamorphosis": "Fiction/Classics",
    "Big Money": "Fiction/Humor",
    "The Old Man and the Sea": "Fiction/Classics",
    "Dune": "Fiction/Science Fiction",
    "Of Counsel": "Non-Fiction/Economics",
    "The Girl in Blue": "Fiction/Humor",
    "The Master and Margarita": "Fiction/Classics",
    "Shunya": "Spirituality/Memoir",
    "Good Omens": "Fiction/Fantasy/Humor",
    "The Palace of Illusions": "Fiction/Mythology",
    "The Peshwa": "Fiction/Historical",
    "The Street Lawyer": "Fiction/Thriller",
    "Nothing Lasts Forever": "Fiction/Thriller",
    "Freedom": "Fiction/Literary Fiction",
    "Midnight's Children": "Fiction/Magical Realism",
    "The Satanic Verses": "Fiction/Literary Fiction",
    "Sidney Sheldon's The Silent Widow": "Fiction/Thriller",
    "Life over Two Beers and other stories": "Fiction/Short Stories",
    "Asura: Tale Of The Vanquished": "Fiction/Mythology",
    "In the Shadow of the Banyan": "Fiction/Historical",
    "When Breath Becomes Air": "Non-Fiction/Memoir",
    "Kafka on the Shore": "Fiction/Magical Realism",
    "Norwegian Wood": "Fiction/Literary Fiction",
    "Leave It to Psmith": "Fiction/Humor",
    "And Then There Were None": "Fiction/Mystery",
    "The Afghan": "Fiction/Thriller",
    "Mossad": "Non-Fiction/History",
    "Blandings Castle": "Fiction/Humor",
    "The Hidden Life of Trees": "Non-Fiction/Science/Nature",
    "Crime and Punishment": "Fiction/Classics",
    "Animal Farm": "Fiction/Dystopian/Satire",
    "The Marble Collector": "Fiction/Literary Fiction",
    "By the River Piedra I Sat Down and Wept": "Fiction/Spirituality",
    "The Enchantress of Florence": "Fiction/Historical/Magical Realism",
    "The Great Indian Novel": "Fiction/Satire",
    "Master of the Game": "Fiction/Thriller",
    "Rage of Angels": "Fiction/Thriller",
    "The Footprints of God": "Fiction/Thriller",
    "Scion of Ikshvaku": "Fiction/Mythology",
    "The Great Gatsby": "Fiction/Classics",
    "Playing It My Way": "Non-Fiction/Biography",
    "Shalimar the Clown": "Fiction/Literary Fiction",
    "The Lovely Bones": "Fiction/Literary Fiction",
    "The Sicilian": "Fiction/Thriller",
    "Beatrice and Virgil": "Fiction/Literary Fiction",
    "The Sceptical Patriot": "Non-Fiction/History",
    "Harry Potter and the Half-Blood Prince": "Fiction/Fantasy",
    "Plaster City": "Fiction/Thriller",
    "This Book Does Not Exist": "Fiction/Philosophy",
    "I Am the Messenger": "Fiction/Literary Fiction",
    "A Painted House": "Fiction/Literary Fiction",
    "Keep off the Grass": "Fiction/Literary Fiction",
    "The Oath of the Vayuputras": "Fiction/Mythology",
    "The Lowland": "Fiction/Literary Fiction",
    "Right Ho, Jeeves & Carry On, Jeeves": "Fiction/Humor",
    "The Da Vinci Code": "Fiction/Thriller",
    "Pride and Prejudice": "Fiction/Classics",
    "The Book Thief": "Fiction/Historical",
    "The Other Side of Midnight": "Fiction/Thriller",
    "The Immortals of Meluha": "Fiction/Mythology",
    "Wicked Lovely": "Fiction/Fantasy",
    "A Brief History of Time": "Non-Fiction/Science",
    "Evil Under the Sun": "Fiction/Mystery",
    "Inferno": "Fiction/Thriller",
    "The Catcher in the Rye": "Fiction/Classics",
    "So Long, and Thanks for All the Fish": "Fiction/Science Fiction/Humor",
    "Ink Exchange": "Fiction/Fantasy",
    "Harry Potter and the Chamber of Secrets": "Fiction/Fantasy",
    "A Thousand Splendid Suns": "Fiction/Literary Fiction",
    "The Witch of Portobello": "Fiction/Spirituality",
    "The Lost Symbol": "Fiction/Thriller",
    "8th Confession": "Fiction/Mystery",
    "Fooled by Randomness": "Non-Fiction/Finance/Philosophy",
    "Maximum City": "Non-Fiction/History",
    "The Family": "Fiction/Historical",
    "The Godfather": "Fiction/Thriller",
    "Jeeves and the Feudal Spirit": "Fiction/Humor",
    "Joy: The Happiness That Comes from Within": "Self-Help/Spirituality",
    "Harry Potter and the Deathly Hallows": "Fiction/Fantasy",
    "If Tomorrow Comes": "Fiction/Thriller",
    "The Namesake": "Fiction/Literary Fiction",
    "Into the Silent Land": "Non-Fiction/Neuroscience",
    "One Night at the Call Center": "Fiction/Literary Fiction",
    "Omerta": "Fiction/Thriller",
    "Catch-22": "Fiction/Satire",
    "Anything for You, Ma'am": "Fiction/Romance",
    "Harry Potter and the Prisoner of Azkaban": "Fiction/Fantasy",
    "The Fountainhead": "Fiction/Philosophy",
    "False Impression": "Fiction/Thriller",
    "The Celestial Bed": "Fiction/Thriller",
    "The Last Don": "Fiction/Thriller",
    "Life, the Universe and Everything": "Fiction/Science Fiction/Humor",
    "Twilight": "Fiction/Romance",
    "The 3 Mistakes of My Life": "Fiction/Literary Fiction",
    "The Kite Runner": "Fiction/Literary Fiction",
    "Harry Potter and the Sorcerer's Stone": "Fiction/Fantasy",
    "The Case of the One-Eyed Witness": "Fiction/Mystery",
    "The Secret Adversary": "Fiction/Mystery",
    "2 States": "Fiction/Literary Fiction",
    "I, Robot": "Fiction/Science Fiction",
    "Right Ho, Jeeves": "Fiction/Humor",
    "Airport": "Fiction/Thriller",
    "The Case of the Lonely Heiress": "Fiction/Mystery",
    "Black Holes and Baby Universes": "Non-Fiction/Science",
    "Harry Potter and the Goblet of Fire": "Fiction/Fantasy",
    "The Count of Monte Cristo": "Fiction/Classics",
    "Oh Life! Relax Please": "Self-Help/Spirituality",
    "The Miracle": "Fiction/Thriller",
    "The Search": "Non-Fiction/Technology",
    "A Briefer History of Time": "Non-Fiction/Science",
    "The Time Machine": "Fiction/Science Fiction",
    "The Inscrutable Americans": "Fiction/Humor",
    "The Second Lady": "Fiction/Thriller",
    "To Kill a Mockingbird": "Fiction/Classics",
    "The First P. G. Wodehouse Omnibus": "Fiction/Humor",
    "The Firm": "Fiction/Thriller",
    "Veronika Decides to Die": "Fiction/Spirituality",
    "The Silence of the Lambs": "Fiction/Thriller",
    "Hotel": "Fiction/Thriller",
    "The Secret of the Nagas": "Fiction/Mythology",
    "The Universe in a Nutshell": "Non-Fiction/Science",
    "Tell Me Your Dreams": "Fiction/Thriller",
    "Surely You're Joking, Mr. Feynman!": "Non-Fiction/Biography/Science",
    "The Case of the Amorous Aunt": "Fiction/Mystery",
    "The Alchemist": "Fiction/Fable/Spirituality",
    "Not a Penny More, Not a Penny Less": "Fiction/Thriller",
    "The Graveyard Book": "Fiction/Fantasy",
    "The Almighty": "Fiction/Thriller",
    "The Case of the Caretaker's Cat": "Fiction/Mystery",
    "The Fan Club": "Fiction/Thriller",
    "Harry Potter and the Order of the Phoenix": "Fiction/Fantasy",
    "Fragile Eternity": "Fiction/Fantasy",
    "The Restaurant at the End of the Universe": "Fiction/Science Fiction/Humor",
    "Operation Karakoram": "Fiction/Thriller",
    "Mostly Harmless": "Fiction/Science Fiction/Humor",
    "The Ultimate Hitchhiker's Guide to the Galaxy": "Fiction/Science Fiction/Humor",
    "Miguel Street": "Fiction/Literary Fiction",
    # Owned-only books that may need explicit assignment
    "Krsna: The Supreme Personality of Godhead": "Spirituality/Religion",
    "Guards! Guards!": "Fiction/Fantasy",
    "Chaos": "Non-Fiction/Science",
    "Brida": "Fiction/Spirituality",
    "White Nights": "Fiction/Classics",
    "Autobiography of a Yogi": "Spirituality/Biography",
    "Nirvana: The Last Nightmare": "Spirituality/Philosophy",
    "The Best of Speaking Tree Volume 2": "Spirituality/Inspirational",
    "India that is Bharat": "Non-Fiction/History/Politics",
    "Roadside Picnic": "Fiction/Science Fiction",
    "The Doctrine of Vibration": "Spirituality/Religion",
    "The Tell-Tale Brain": "Non-Fiction/Neuroscience",
    "Spark with Python": "Non-Fiction/Programming",
    "Galapagos": "Fiction/Satire/Science Fiction",
    "Wodehouse at Blandings": "Fiction/Humor",
    "Full Moon": "Fiction/Humor",
    "Summer Moonshine": "Fiction/Humor",
    "Ukridge": "Fiction/Humor",
    "A Damsel in Distress": "Fiction/Humor",
    "A Pelican at Blandings": "Fiction/Humor",
    "Uncle Fred in the Springtime": "Fiction/Humor",
    "Joy in the Morning": "Fiction/Humor",
    "Elon Musk": "Non-Fiction/Biography",
    "Oh, Life Relax Please!": "Self-Help/Spirituality",
    "An Era of Darkness": "Non-Fiction/History",
    "Revolutionaries": "Non-Fiction/History",
    "The Selfish Gene (40th Anniversary Edition)": "Non-Fiction/Science",
    "Raavan: Enemy of Aryavarta (Gujarati)": "Fiction/Mythology",
    "Bhagavad Gita (Gujarati)": "Spirituality/Religion",
    "The Bhagavad Gita (translated)": "Spirituality/Religion",
    "Hatha Yoga Upanishad": "Spirituality/Religion",
    "Vedanta: Book of Definitions Upanishad": "Spirituality/Religion",
    "Death and the Ashtavakra Gita": "Spirituality/Religion",
    "A Twist in the Tale": "Fiction/Short Stories",
    "Man's Search for Meaning": "Non-Fiction/Psychology",
    "Homo Deus: A Brief History of Tomorrow": "Non-Fiction/Futurology",
    # --- Books only in Goodreads CSV (with series info in title) ---
    "The Chola Tigers: Avengers of Somnath": "Fiction/Historical",
    "Doctor Who: The Clockwise Man": "Fiction/Science Fiction",
    "The Secret of Secrets": "Fiction/Thriller",
    "The Remains of the Day": "Fiction/Literary Fiction",
    "The Silent Patient": "Fiction/Thriller",
    "Spiritual Awakening, Vol. 1": "Spirituality/Religion",
    "Blood Like Mine": "Fiction/Thriller",
    "The Stars, Like Dust": "Fiction/Science Fiction",
    "1Q84": "Fiction/Magical Realism",
    "A Fine Balance": "Fiction/Literary Fiction",
    "ANDAMAN": "Fiction/Thriller",
    "Against the Gods: The Remarkable Story of Risk": "Non-Fiction/Finance",
    "Child 44": "Fiction/Thriller",
    "Galahad at Blandings": "Fiction/Humor",
    "Hot Water": "Fiction/Humor",
    "Infinite Jest": "Fiction/Literary Fiction",
    "Sputnik Sweetheart": "Fiction/Magical Realism",
    "KARMA YOGA by Swami Vivenkananda": "Spirituality/Religion",
    "The Mating Season": "Fiction/Humor",
    "The Critique of Pure Reason": "Non-Fiction/Philosophy",
    "The Decision Book: Fifty Models for Strategic Thinking": "Non-Fiction/Business",
    "The Giver": "Fiction/Dystopian",
    "The Hidden Hindu": "Fiction/Mythology",
    "The Murder on the Links": "Fiction/Mystery",
    "The Mysterious Affair at Styles": "Fiction/Mystery",
    "The Psychology of Money": "Non-Fiction/Finance",
    "Mr. Everit's Secret": "Non-Fiction/Finance",
    "One Good Deed": "Fiction/Thriller",
    "Origin": "Fiction/Thriller",
    "Rework": "Non-Fiction/Business",
    "Samanya Dharma": "Spirituality/Religion",
    "Slaughterhouse-Five": "Fiction/Satire/Science Fiction",
    "The Almanack of Naval Ravikant": "Non-Fiction/Self-Help/Philosophy",
    "The Bhagavad Gita": "Spirituality/Religion",
    "The Brothers Karamazov": "Fiction/Classics",
    "The Smile that Wins": "Fiction/Humor",
    "Very Good, Jeeves!": "Fiction/Humor",
    "Wodehouse on Crime": "Fiction/Humor",
    "Young Men in Spats": "Fiction/Humor",
    "Tell-Tale Brain": "Non-Fiction/Neuroscience",
    # Perry Mason books
    "The Case Of The Worried Waitress": "Fiction/Mystery",
    "The Case of the Bigamous Spouse": "Fiction/Mystery",
    "The Case of the Calendar Girl": "Fiction/Mystery",
    "The Case of the Counterfeit Eye": "Fiction/Mystery",
    "The Case of the Howling Dog": "Fiction/Mystery",
    "The Case of the Lame Canary": "Fiction/Mystery",
    "The Case of the Lucky Legs": "Fiction/Mystery",
    # Titles with long subtitles that need exact match
    "Asura: Tale Of The Vanquished, The Story of Ravana and His People": "Fiction/Mythology",
    "Black Holes and Baby Universes and Other Essays": "Non-Fiction/Science",
    "Joy: The Happiness That Comes from Within (Insights for a New Way of Living)": "Self-Help/Spirituality",
    "Midnight's Children": "Fiction/Magical Realism",
    "Omerta (The Godfather)": "Fiction/Thriller",
    "Right Ho, Jeeves & Carry On, Jeeves; P. G. Wodehouse Collected Works": "Fiction/Humor",
    "Samanya Dharma – Ethical Duties Common to All": "Spirituality/Religion",
    "Sidney Sheldon's The Silent Widow": "Fiction/Thriller",
    "The Hitchhiker's Guide to the Galaxy (Hitchhiker's Guide to the Galaxy, #1)": "Fiction/Science Fiction/Humor",
    "The Hitchhiker's Guide to the Galaxy (The Hitchhiker's Guide to the Galaxy, #1)": "Fiction/Science Fiction/Humor",
    "The Ultimate Hitchhiker's Guide to the Galaxy (Hitchhiker's Guide to the Galaxy, #1-5)": "Fiction/Science Fiction/Humor",
}

# ==========================================================================
#  INTERNAL — you usually don't need to edit below this line
# ==========================================================================

def clean_review(text):
    """Convert Goodreads HTML review to plain text."""
    text = text.replace('<br/>', '\n').replace('<br>', '\n')
    text = re.sub(r'<[^>]+>', '', text)
    return text.strip()

def strip_series(title):
    """Strip series info like '(Blandings Castle, #6)' from title."""
    return re.sub(r'\s*\([^)]*#\d+[^)]*\)\s*$', '', title).strip()

def normalize_title(title):
    return re.sub(r'[^\w\s]', '', title.lower()).strip()

def normalize_quotes(s):
    """Normalize curly/smart quotes to straight ASCII quotes."""
    s = s.replace('\u2018', "'").replace('\u2019', "'")  # ' '
    s = s.replace('\u201C', '"').replace('\u201D', '"')   # " "
    return s

def lookup_category(title):
    """Look up category, trying exact match first, then stripped title."""
    # Normalize curly quotes in the input title
    title_n = normalize_quotes(title)
    
    for t in [title, title_n]:
        if t in CATEGORY_ASSIGNMENTS:
            return CATEGORY_ASSIGNMENTS[t]
    
    stripped = strip_series(title_n)
    if stripped in CATEGORY_ASSIGNMENTS:
        return CATEGORY_ASSIGNMENTS[stripped]
    
    # Try matching by removing subtitle after colon
    base = title_n.split(':')[0].strip()
    if base in CATEGORY_ASSIGNMENTS:
        return CATEGORY_ASSIGNMENTS[base]
    base2 = stripped.split(':')[0].strip()
    if base2 in CATEGORY_ASSIGNMENTS:
        return CATEGORY_ASSIGNMENTS[base2]
    return ''

def classify_book(category_string):
    """Return list of {main, sub} from a category string like 'Fiction/Mythology'."""
    if not category_string or category_string == 'Unknown':
        return []
    parts = [p.strip() for p in category_string.split('/')]
    results = []
    for main_cat, subs in MAIN_CATEGORIES.items():
        subs_lower = [s.lower() for s in subs]
        matched_subs = []
        for part in parts:
            if part.lower() in subs_lower:
                matched_subs.append(part)
        if matched_subs:
            results.append({"main": main_cat, "subs": matched_subs})
    # If no main category matched, try to infer from first part
    if not results and parts:
        first = parts[0]
        if first.lower() in ['self-help']:
            results.append({"main": "Non-Fiction", "subs": parts})
        elif first.lower() in ['poetry']:
            results.append({"main": "Spirituality & Religion", "subs": parts})
        elif first.lower() in ['biography']:
            results.append({"main": "Non-Fiction", "subs": parts})
        else:
            results.append({"main": "Non-Fiction", "subs": parts})
    return results

def main():
    # --- 1. Read Goodreads CSV ---
    gr_books = []
    reviews = {}
    if os.path.exists(GOODREADS_CSV):
        with open(GOODREADS_CSV, 'r', encoding='utf-8') as f:
            for row in csv.DictReader(f):
                title = row.get('Title', '').strip()
                author = row.get('Author', '').strip()
                rating = int(row.get('My Rating', '0') or '0')
                shelf = row.get('Exclusive Shelf', '').strip()
                review_text = row.get('My Review', '').strip()
                date_read = row.get('Date Read', '').strip()
                date_added = row.get('Date Added', '').strip()
                pages = row.get('Number of Pages', '').strip()
                avg_rating = row.get('Average Rating', '').strip()

                status = shelf if shelf in ('read', 'currently-reading', 'to-read') else 'read'

                gr_books.append({
                    "title": title,
                    "author": author,
                    "rating": rating,
                    "status": status,
                    "date_read": date_read,
                    "date_added": date_added,
                    "pages": pages,
                    "avg_rating": avg_rating,
                })

                if review_text:
                    reviews[title] = clean_review(review_text)
    else:
        print(f"WARNING: {GOODREADS_CSV} not found")

    # --- 2. Read owned books ---
    owned_books = []
    if os.path.exists(OWNED_BOOKS_TXT):
        with open(OWNED_BOOKS_TXT, 'r', encoding='utf-8') as f:
            lines = f.read().strip().split('\n')
        # Parse: "Title - Author" or CSV-like
        for line in lines:
            line = line.strip()
            if not line:
                continue
            # books.txt is likely just a list; owned CSV is embedded in old HTML
            # We'll handle it as simple lines
            owned_books.append(line)
    # We still have the CSV embedded in the old data — use the owned data from it
    # For now, owned data comes from the built-in ownedBooksData

    # --- 3. Read owned books CSV (inline) ---
    owned_csv_path = "owned_books.csv"
    owned_map = {}  # normalized_title -> {title, author, category, condition}
    if os.path.exists(owned_csv_path):
        with open(owned_csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                t = row.get('Title', '').strip()
                owned_map[normalize_title(t)] = {
                    "title": t,
                    "author": row.get('Author', '').strip(),
                    "category": row.get('Category', '').strip(),
                    "condition": row.get('Condition', '').strip(),
                }
    else:
        print(f"NOTE: {owned_csv_path} not found — using only Goodreads data for merging")

    # --- 4. Merge books ---
    all_books = []
    seen_normalized = set()
    deletions = {o['title'].lower() for o in BOOK_OVERRIDES if o.get('_delete')}
    override_map = {}
    additions = []
    for o in BOOK_OVERRIDES:
        if o.get('_delete'):
            continue
        # Check if it's an existing book override or a new addition
        found = False
        for gb in gr_books:
            if gb['title'].lower() == o['title'].lower():
                found = True
                break
        if not found:
            for nt, ob in owned_map.items():
                if ob['title'].lower() == o['title'].lower():
                    found = True
                    break
        if found:
            override_map[o['title'].lower()] = o
        else:
            additions.append(o)

    # Process Goodreads books
    for gb in gr_books:
        if gb['title'].lower() in deletions:
            continue
        nt = normalize_title(gb['title'])
        seen_normalized.add(nt)

        owned_info = owned_map.get(nt)
        cat = lookup_category(gb['title'])
        if not cat and owned_info:
            cat = owned_info.get('category', '')
        if not cat:
            cat = 'Unknown'

        # Apply overrides
        ovr = override_map.get(gb['title'].lower(), {})
        if ovr.get('category_override'):
            cat = ovr['category_override']
        if 'rating' in ovr:
            gb['rating'] = ovr['rating']
        if 'status' in ovr:
            gb['status'] = ovr['status']

        classifications = classify_book(cat)

        book = {
            "title": gb['title'],
            "author": ovr.get('author', gb['author']),
            "rating": gb['rating'],
            "status": gb['status'],
            "category": cat,
            "classifications": classifications,
            "owned": owned_info is not None,
            "condition": owned_info['condition'] if owned_info else None,
            "review": reviews.get(gb['title'], None),
            "date_read": gb.get('date_read', ''),
            "date_added": gb.get('date_added', ''),
            "pages": gb.get('pages', ''),
            "avg_rating": gb.get('avg_rating', ''),
        }
        all_books.append(book)

    # Process owned-only books not in Goodreads
    for nt, ob in owned_map.items():
        if nt in seen_normalized:
            continue
        if ob['title'].lower() in deletions:
            continue
        seen_normalized.add(nt)

        cat = lookup_category(ob['title']) or ob.get('category', 'Unknown')
        ovr = override_map.get(ob['title'].lower(), {})
        if ovr.get('category_override'):
            cat = ovr['category_override']

        classifications = classify_book(cat)

        book = {
            "title": ob['title'],
            "author": ob['author'],
            "rating": ovr.get('rating', 0),
            "status": ovr.get('status', 'owned'),
            "category": cat,
            "classifications": classifications,
            "owned": True,
            "condition": ob.get('condition'),
            "review": reviews.get(ob['title'], None),
            "date_read": "",
            "date_added": "",
            "pages": "",
            "avg_rating": "",
        }
        all_books.append(book)

    # Process additions from overrides
    for add in additions:
        cat = add.get('category_override', 'Unknown')
        classifications = classify_book(cat)
        book = {
            "title": add['title'],
            "author": add.get('author', 'Unknown'),
            "rating": add.get('rating', 0),
            "status": add.get('status', 'read'),
            "category": cat,
            "classifications": classifications,
            "owned": add.get('owned', False),
            "condition": add.get('condition'),
            "review": add.get('review'),
            "date_read": add.get('date_read', ''),
            "date_added": add.get('date_added', ''),
            "pages": add.get('pages', ''),
            "avg_rating": add.get('avg_rating', ''),
        }
        all_books.append(book)

    # --- 5. De-duplicate books ---
    def merge_books(blist):
        """Merge a list of duplicate book entries, keeping the richest data."""
        base = max(blist, key=lambda b: (
            bool(b.get('review')),
            b.get('rating', 0),
            bool(b.get('date_read')),
            b.get('status') == 'read',
        ))
        merged = dict(base)
        for b in blist:
            if b is base:
                continue
            if b.get('owned'):
                merged['owned'] = True
            if b.get('condition') and not merged.get('condition'):
                merged['condition'] = b['condition']
            if b.get('review') and not merged.get('review'):
                merged['review'] = b['review']
            if b.get('rating', 0) > merged.get('rating', 0):
                merged['rating'] = b['rating']
            if b.get('date_read') and not merged.get('date_read'):
                merged['date_read'] = b['date_read']
            if b.get('date_added') and not merged.get('date_added'):
                merged['date_added'] = b['date_added']
            if b.get('pages') and not merged.get('pages'):
                merged['pages'] = b['pages']
            if b.get('avg_rating') and not merged.get('avg_rating'):
                merged['avg_rating'] = b['avg_rating']
            # Merge status: read > currently-reading > to-read > owned
            status_priority = {'read': 4, 'currently-reading': 3, 'to-read': 2, 'owned': 1}
            if status_priority.get(b['status'], 0) > status_priority.get(merged['status'], 0):
                merged['status'] = b['status']
        return merged

    # Group by normalized base title + author, merge entries
    def dedup_key(b):
        t = re.sub(r'\s*\([^)]*\)\s*$', '', b['title']).strip().lower()
        # Also normalize curly quotes
        t = t.replace('\u2018', "'").replace('\u2019', "'").replace('\u201c', '"').replace('\u201d', '"')
        return (t, b['author'].lower())

    def dedup_key_colon(b):
        """More aggressive: also strip subtitle after colon."""
        t = re.sub(r'\s*\([^)]*\)\s*$', '', b['title']).strip().lower()
        t = t.replace('\u2018', "'").replace('\u2019', "'").replace('\u201c', '"').replace('\u201d', '"')
        t = t.split(':')[0].strip()
        return (t, b['author'].lower())

    # First pass: exact base title dedup
    groups = defaultdict(list)
    for b in all_books:
        groups[dedup_key(b)].append(b)

    pass1 = []
    merged_count = 0
    for key, blist in groups.items():
        if len(blist) == 1:
            pass1.append(blist[0])
        else:
            merged_count += len(blist) - 1
            pass1.append(merge_books(blist))

    # Second pass: colon-based dedup (catches "Fooled by Randomness" vs "Fooled by Randomness: The Hidden Role...")
    groups2 = defaultdict(list)
    for b in pass1:
        groups2[dedup_key_colon(b)].append(b)

    deduped = []
    for key, blist in groups2.items():
        if len(blist) == 1:
            deduped.append(blist[0])
        else:
            merged_count += len(blist) - 1
            deduped.append(merge_books(blist))

    all_books = deduped
    if merged_count:
        print(f"  De-duplicated: merged {merged_count} duplicate entries")

    # --- 6. Write output ---
    output = {
        "generated": True,
        "book_count": len(all_books),
        "review_count": sum(1 for b in all_books if b.get('review')),
        "main_categories": list(MAIN_CATEGORIES.keys()),
        "books": all_books,
    }

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    # --- Stats ---
    statuses = defaultdict(int)
    mains = defaultdict(int)
    for b in all_books:
        statuses[b['status']] += 1
        for c in b.get('classifications', []):
            mains[c['main']] += 1

    print(f"\n{'='*50}")
    print(f"  Library built successfully!")
    print(f"{'='*50}")
    print(f"  Total books:    {len(all_books)}")
    print(f"  With reviews:   {output['review_count']}")
    print(f"  Read:           {statuses.get('read', 0)}")
    print(f"  Reading:        {statuses.get('currently-reading', 0)}")
    print(f"  To Read:        {statuses.get('to-read', 0)}")
    print(f"  Owned only:     {statuses.get('owned', 0)}")
    print(f"  ---")
    for mc, count in sorted(mains.items(), key=lambda x: -x[1]):
        print(f"  {mc}: {count} books")
    print(f"{'='*50}")
    print(f"  Output: {OUTPUT_FILE}")
    print(f"  Open index.html in browser to view.\n")

if __name__ == "__main__":
    main()
