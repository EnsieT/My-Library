#!/usr/bin/env python3
"""
Incremental book image downloader.
Download images by author or in batches of 10.
Usage:
  python download_images.py              # Download next 10 books
  python download_images.py 5            # Download next 5 books
  python download_images.py --author "Haruki Murakami"  # Download by author
  python download_images.py --status completed  # Show status
"""

import os
import json
import requests
import sys
from pathlib import Path
from urllib.parse import quote
from datetime import datetime

IMAGES_DIR = Path(__file__).parent / "images"
IMAGES_DIR.mkdir(exist_ok=True)

MAPPING_FILE = Path(__file__).parent / "image_mapping.json"
STATUS_FILE = Path(__file__).parent / "image_download_status.json"
NOT_FOUND_FILE = Path(__file__).parent / "images_not_found.json"

BOOKS = [
    ("Dance Dance Dance", "Haruki Murakami"),
    ("Never Let Me Go", "Kazuo Ishiguro"),
    ("Don't Lose Your Mind, Lose Your Weight", "Rujuta Diwekar"),
    ("First Lie Wins", "Ashley Elston"),
    ("The Chola Tigers: Avengers of Somnath", "Amish Tripathi"),
    ("Doctor Who: The Clockwise Man", "Justin Richards"),
    ("The Secret of Secrets (Robert Langdon, #6)", "Dan Brown"),
    ("Uncle Fred in the Springtime (Blandings Castle, #6)", "P.G. Wodehouse"),
    ("Guards! Guards! (Discworld, #8; City Watch, #1)", "Terry Pratchett"),
    ("Roadside Picnic", "Arkady Strugatsky"),
    ("The Remains of the Day", "Kazuo Ishiguro"),
    ("The Silent Patient", "Alex Michaelides"),
    ("Spiritual Awakening, Vol. 1", "Hit Premanand Govind Sharan Ji Maharaj"),
    ("White Nights", "Fyodor Dostoevsky"),
    ("Blood Like Mine", "Stuart Neville"),
    ("The Stars, Like Dust (Galactic Empire, #1)", "Isaac Asimov"),
    ("A Damsel in Distress", "P.G. Wodehouse"),
    ("The Decision Book: Fifty Models for Strategic Thinking", "Mikael Krogerus"),
    ("Full Moon (Blandings Castle, #7)", "P.G. Wodehouse"),
    ("The Almanack of Naval Ravikant", "Eric Jorgenson"),
    ("Rework", "Jason Fried"),
    ("Galahad at Blandings (Blandings Castle, #10)", "P.G. Wodehouse"),
    ("Tell-Tale Brain", "V.S. Ramachandran"),
    ("The Hidden Hindu", "Akshat Gupta"),
    ("ANDAMAN", "Ratnadip Acharya"),
    ("Sputnik Sweetheart", "Haruki Murakami"),
    ("Origin (Robert Langdon, #5)", "Dan Brown"),
    ("A Pelican at Blandings (Blandings Castle, #11)", "P.G. Wodehouse"),
    ("Elon Musk", "Walter Isaacson"),
    ("The Giver", "Lois Lowry"),
    ("The Case Of The Worried Waitress (Perry Mason, #77)", "Erle Stanley Gardner"),
    ("The Case of the Howling Dog (Perry Mason, #4)", "Erle Stanley Gardner"),
    ("The Case of the Lame Canary (Perry Mason, #11)", "Erle Stanley Gardner"),
    ("The Murder on the Links (Hercule Poirot, #2)", "Agatha Christie"),
    ("1Q84", "Haruki Murakami"),
    ("Revolutionaries", "Sanjeev Sanyal"),
    ("Child 44", "Tom Rob Smith"),
    ("The Bhagavad Gita", "Krishna-Dwaipayana Vyasa"),
    ("Very Good, Jeeves! (Jeeves, #4)", "P.G. Wodehouse"),
    ("Samanya Dharma", "Nithin Sridhar"),
    ("The Mysterious Affair at Styles (Hercule Poirot, #1)", "Agatha Christie"),
    ("One Good Deed", "David Baldacci"),
    ("Hot Water", "P.G. Wodehouse"),
    ("KARMA YOGA", "Vivekananda"),
    ("The Psychology of Money", "Morgan Housel"),
    ("Siddhartha", "Hermann Hesse"),
    ("The Myth of Sisyphus", "Albert Camus"),
    ("The Hitchhiker's Guide to the Galaxy", "Douglas Adams"),
    ("The Ocean of Churn", "Sanjeev Sanyal"),
    ("The Will to Meaning", "Viktor E. Frankl"),
    ("India in the Age of Ideas", "Sanjeev Sanyal"),
    ("Quichotte", "Salman Rushdie"),
    ("After Dark", "Haruki Murakami"),
    ("The Secret Garden", "Frances Hodgson Burnett"),
    ("Joy in the Morning (Jeeves, #8)", "P.G. Wodehouse"),
    ("The Last Lecture", "Randy Pausch"),
    ("Atomic Habits", "James Clear"),
    ("Sapiens", "Yuval Noah Harari"),
    ("Fahrenheit 451", "Ray Bradbury"),
    ("Dracula", "Bram Stoker"),
    ("The Krishna Key", "Ashwin Sanghi"),
    ("Krishna's Secret", "Devdutt Pattanaik"),
    ("Keepers of the Kalachakra", "Ashwin Sanghi"),
    ("Ikigai", "Héctor García"),
    ("Land of the Seven Rivers", "Sanjeev Sanyal"),
    ("One Hundred Years of Solitude", "Gabriel García Márquez"),
    ("The Valmiki Ramayana Vol. 3", "Vālmīki"),
    ("Why We Sleep", "Matthew Walker"),
    ("The Mahabharata: Volume 1", "Krishna-Dwaipayana Vyasa"),
    ("Man's Search for Meaning", "Viktor E. Frankl"),
    ("As a Man Thinketh", "James Allen"),
    ("Young Men in Spats", "P.G. Wodehouse"),
    ("21 Lessons for the 21st Century", "Yuval Noah Harari"),
    ("Submission", "Michel Houellebecq"),
    ("A Gentleman in Moscow", "Amor Towles"),
    ("Uncle Dynamite", "P.G. Wodehouse"),
    ("1984", "George Orwell"),
    ("The Case of the Calendar Girl (Perry Mason, #57)", "Erle Stanley Gardner"),
    ("Homo Deus", "Yuval Noah Harari"),
    ("The Four", "Scott Galloway"),
    ("Summer Lightning (Blandings Castle, #4)", "P.G. Wodehouse"),
    ("Five Point Someone", "Chetan Bhagat"),
    ("Something Fresh (Blandings Castle, #1)", "P.G. Wodehouse"),
    ("Wings of Fire", "A.P.J. Abdul Kalam"),
    ("Angels & Demons (Robert Langdon, #1)", "Dan Brown"),
    ("Deception Point", "Dan Brown"),
    ("Rich Dad, Poor Dad", "Robert T. Kiyosaki"),
    ("The Seventh Secret", "Irving Wallace"),
    ("Digital Fortress", "Dan Brown"),
    ("Rich Dad's Cashflow Quadrant", "Robert T. Kiyosaki"),
    ("Illusions", "Richard Bach"),
    ("The Stranger", "Albert Camus"),
    ("The Mahabharata Secret", "Christopher C. Doyle"),
    ("Jonathan Livingston Seagull", "Richard Bach"),
    ("Service With a Smile", "P.G. Wodehouse"),
    ("Rumi", "Jalal ad-Din Muhammad ar-Rumi"),
    ("Kalki Purana", "B.K. Chaturvedi"),
    ("Robots and Empire (Robot, #4)", "Isaac Asimov"),
    ("A Column of Fire (Kingsbridge, #3)", "Ken Follett"),
    ("House of Leaves", "Mark Z. Danielewski"),
    ("The Metamorphosis", "Franz Kafka"),
    ("Big Money", "P.G. Wodehouse"),
    ("The Old Man and the Sea", "Ernest Hemingway"),
    ("Dune", "Frank Herbert"),
    ("Of Counsel", "Arvind Subramanian"),
    ("The Girl in Blue", "P.G. Wodehouse"),
    ("The Master and Margarita", "Mikhail Bulgakov"),
    ("Shunya", "Sri M."),
    ("Good Omens", "Terry Pratchett"),
    ("The Palace of Illusions", "Chitra Banerjee Divakaruni"),
    ("The Peshwa", "Ram Sivasankaran"),
    ("The Street Lawyer", "John Grisham"),
    ("Nothing Lasts Forever", "Sidney Sheldon"),
    ("The Case of the Counterfeit Eye (Perry Mason, #6)", "Erle Stanley Gardner"),
    ("Freedom", "Jonathan Franzen"),
    ("The Case of the Bigamous Spouse (Perry Mason, #65)", "Erle Stanley Gardner"),
    ("The Case of the Lucky Legs (Perry Mason, #3)", "Erle Stanley Gardner"),
    ("Midnight's Children", "Salman Rushdie"),
    ("The Satanic Verses", "Salman Rushdie"),
    ("Sidney Sheldon's The Silent Widow", "Tilly Bagshawe"),
    ("Life over Two Beers and other stories", "Sanjeev Sanyal"),
    ("Asura: Tale Of The Vanquished", "Anand Neelakantan"),
    ("In the Shadow of the Banyan", "Vaddey Ratner"),
    ("When Breath Becomes Air", "Paul Kalanithi"),
    ("Kafka on the Shore", "Haruki Murakami"),
    ("Norwegian Wood", "Haruki Murakami"),
    ("Leave It to Psmith", "P.G. Wodehouse"),
    ("And Then There Were None", "Agatha Christie"),
    ("The Afghan", "Frederick Forsyth"),
    ("Mossad", "Michael Bar-Zohar"),
    ("Blandings Castle", "P.G. Wodehouse"),
    ("The Hidden Life of Trees", "Peter Wohlleben"),
    ("Crime and Punishment", "Fyodor Dostoevsky"),
    ("Animal Farm", "George Orwell"),
    ("The Marble Collector", "Cecelia Ahern"),
    ("By the River Piedra I Sat Down and Wept", "Paulo Coelho"),
    ("The Enchantress of Florence", "Salman Rushdie"),
    ("The Great Indian Novel", "Shashi Tharoor"),
    ("Master of the Game", "Sidney Sheldon"),
    ("Rage of Angels", "Sidney Sheldon"),
    ("The Footprints of God", "Greg Iles"),
    ("Scion of Ikshvaku", "Amish Tripathi"),
    ("The Great Gatsby", "F. Scott Fitzgerald"),
    ("Playing It My Way", "Sachin Tendulkar"),
    ("Shalimar the Clown", "Salman Rushdie"),
    ("The Lovely Bones", "Alice Sebold"),
    ("The Sicilian (The Godfather, #2)", "Mario Puzo"),
    ("Beatrice and Virgil", "Yann Martel"),
    ("The Sceptical Patriot", "Sidin Vadukut"),
    ("Harry Potter and the Half-Blood Prince", "J.K. Rowling"),
    ("Plaster City", "Johnny Shaw"),
    ("This Book Does Not Exist", "Mike Schneider"),
    ("I Am the Messenger", "Markus Zusak"),
    ("A Painted House", "John Grisham"),
    ("Keep off the Grass", "Karan Bajaj"),
    ("The Oath of the Vayuputras", "Amish Tripathi"),
    ("The Lowland", "Jhumpa Lahiri"),
    ("Right Ho, Jeeves & Carry On, Jeeves", "P.G. Wodehouse"),
    ("The Da Vinci Code (Robert Langdon, #2)", "Dan Brown"),
    ("Pride and Prejudice", "Jane Austen"),
    ("The Book Thief", "Markus Zusak"),
    ("The Other Side of Midnight", "Sidney Sheldon"),
    ("The Immortals of Meluha", "Amish Tripathi"),
    ("Wicked Lovely", "Melissa Marr"),
    ("A Brief History of Time", "Stephen W. Hawking"),
    ("Evil Under the Sun", "Agatha Christie"),
    ("Inferno (Robert Langdon, #4)", "Dan Brown"),
    ("The Catcher in the Rye", "J.D. Salinger"),
    ("So Long, and Thanks for All the Fish", "Douglas Adams"),
    ("Ink Exchange (Wicked Lovely, #2)", "Melissa Marr"),
    ("Harry Potter and the Chamber of Secrets", "J.K. Rowling"),
    ("A Thousand Splendid Suns", "Khaled Hosseini"),
    ("The Witch of Portobello", "Paulo Coelho"),
    ("The Lost Symbol (Robert Langdon, #3)", "Dan Brown"),
    ("8th Confession", "James Patterson"),
    ("Fooled by Randomness", "Nassim Nicholas Taleb"),
    ("Maximum City", "Suketu Mehta"),
    ("The Family", "Mario Puzo"),
    ("The Godfather", "Mario Puzo"),
    ("Jeeves and the Feudal Spirit (Jeeves, #11)", "P.G. Wodehouse"),
    ("Joy: The Happiness That Comes from Within", "Osho"),
    ("Harry Potter and the Deathly Hallows", "J.K. Rowling"),
    ("If Tomorrow Comes", "Sidney Sheldon"),
    ("The Namesake", "Jhumpa Lahiri"),
    ("Into the Silent Land", "Paul Broks"),
    ("One Night at the Call Center", "Chetan Bhagat"),
    ("Omerta (The Godfather)", "Mario Puzo"),
    ("Catch-22", "Joseph Heller"),
    ("Anything for You, Ma'am", "Raheja Tushar"),
    ("Harry Potter and the Prisoner of Azkaban", "J.K. Rowling"),
    ("The Fountainhead", "Ayn Rand"),
    ("False Impression", "Jeffrey Archer"),
    ("The Celestial Bed", "Irving Wallace"),
    ("The Last Don", "Mario Puzo"),
    ("Life, the Universe and Everything", "Douglas Adams"),
    ("Twilight", "Stephenie Meyer"),
    ("The 3 Mistakes of My Life", "Chetan Bhagat"),
    ("The Kite Runner", "Khaled Hosseini"),
    ("Harry Potter and the Sorcerer's Stone", "J.K. Rowling"),
    ("The Case of the One-Eyed Witness", "Erle Stanley Gardner"),
    ("The Secret Adversary", "Agatha Christie"),
    ("2 States", "Chetan Bhagat"),
    ("I, Robot", "Isaac Asimov"),
    ("Right Ho, Jeeves", "P.G. Wodehouse"),
    ("Airport", "Arthur Hailey"),
    ("The Case of the Lonely Heiress", "Erle Stanley Gardner"),
    ("Black Holes and Baby Universes", "Stephen W. Hawking"),
    ("Harry Potter and the Goblet of Fire", "J.K. Rowling"),
    ("The Count of Monte Cristo", "Alexandre Dumas"),
    ("Oh Life! Relax Please", "Sukhabodhanandha"),
    ("The Miracle", "Irving Wallace"),
    ("The Search", "John Battelle"),
    ("A Briefer History of Time", "Stephen W. Hawking"),
    ("The Time Machine", "H.G. Wells"),
    ("The Inscrutable Americans", "Anurag Mathur"),
    ("The Second Lady", "Irving Wallace"),
    ("To Kill a Mockingbird", "Harper Lee"),
    ("The First P. G. Wodehouse Omnibus", "P.G. Wodehouse"),
    ("The Firm", "Robin Waterfield"),
    ("Veronika Decides to Die", "Paulo Coelho"),
    ("The Silence of the Lambs", "Thomas Harris"),
    ("Hotel", "Arthur Hailey"),
    ("The Secret of the Nagas", "Amish Tripathi"),
    ("The Universe in a Nutshell", "Stephen W. Hawking"),
    ("Tell Me Your Dreams", "Sidney Sheldon"),
    ("Surely You're Joking, Mr. Feynman!", "Richard P. Feynman"),
    ("The Case of the Amorous Aunt", "Erle Stanley Gardner"),
    ("The Alchemist", "Paulo Coelho"),
    ("Not a Penny More, Not a Penny Less", "Jeffrey Archer"),
    ("The Graveyard Book", "Neil Gaiman"),
    ("The Almighty", "Irving Wallace"),
    ("The Case of the Caretaker's Cat", "Erle Stanley Gardner"),
    ("The Fan Club", "Irving Wallace"),
    ("Harry Potter and the Order of the Phoenix", "J.K. Rowling"),
    ("Fragile Eternity (Wicked Lovely, #3)", "Melissa Marr"),
    ("The Restaurant at the End of the Universe", "Douglas Adams"),
    ("Operation Karakoram", "Arvind Nayar"),
    ("Mostly Harmless", "Douglas Adams"),
    ("The Ultimate Hitchhiker's Guide to the Galaxy", "Douglas Adams"),
]

def load_status():
    """Load download status."""
    if STATUS_FILE.exists():
        try:
            with open(STATUS_FILE, 'r') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_status(status):
    """Save download status."""
    with open(STATUS_FILE, 'w') as f:
        json.dump(status, f, indent=2)

def load_mapping():
    """Load image mapping."""
    if MAPPING_FILE.exists():
        try:
            with open(MAPPING_FILE, 'r') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_mapping(mapping):
    """Save image mapping."""
    with open(MAPPING_FILE, 'w') as f:
        json.dump(mapping, f, indent=2)

def load_not_found():
    """Load list of books without images."""
    if NOT_FOUND_FILE.exists():
        try:
            with open(NOT_FOUND_FILE, 'r') as f:
                return json.load(f)
        except:
            return []
    return []

def save_not_found(not_found_list):
    """Save list of books without images."""
    with open(NOT_FOUND_FILE, 'w') as f:
        json.dump(not_found_list, f, indent=2)

def get_image_hash(title, author):
    """Get hash for filename."""
    import hashlib
    key = f"{title}|{author}".lower()
    return hashlib.md5(key.encode()).hexdigest()[:10]

import re
import time

def clean_title(title):
    """Strip series info like (Blandings Castle, #6) from title."""
    return re.sub(r'\s*\([^)]*#\d+[^)]*\)\s*', '', title).strip()

def fetch_image(title, author):
    """Fetch image URL from Open Library or Google Books."""
    clean = clean_title(title)
    
    # --- Attempt 1: Open Library with clean title only ---
    try:
        url = f"https://openlibrary.org/search.json?title={quote(clean)}&limit=3"
        resp = requests.get(url, timeout=8)
        if resp.status_code == 200:
            data = resp.json()
            for doc in (data.get('docs') or []):
                if doc.get('cover_i') or doc.get('cover_id'):
                    cover_id = doc.get('cover_i') or doc.get('cover_id')
                    return f"https://covers.openlibrary.org/b/id/{cover_id}-M.jpg"
    except:
        pass
    
    time.sleep(0.3)
    
    # --- Attempt 2: Open Library general query ---
    try:
        url = f"https://openlibrary.org/search.json?q={quote(clean + ' ' + author)}&limit=3"
        resp = requests.get(url, timeout=8)
        if resp.status_code == 200:
            data = resp.json()
            for doc in (data.get('docs') or []):
                if doc.get('cover_i') or doc.get('cover_id'):
                    cover_id = doc.get('cover_i') or doc.get('cover_id')
                    return f"https://covers.openlibrary.org/b/id/{cover_id}-M.jpg"
    except:
        pass
    
    time.sleep(0.3)
    
    # --- Attempt 3: Google Books API ---
    try:
        url = f"https://www.googleapis.com/books/v1/volumes?q={quote(clean + ' ' + author)}&maxResults=1"
        resp = requests.get(url, timeout=8)
        if resp.status_code == 200:
            data = resp.json()
            items = data.get('items') or []
            if items:
                info = items[0].get('volumeInfo', {})
                links = info.get('imageLinks', {})
                img = links.get('thumbnail') or links.get('smallThumbnail')
                if img:
                    return img.replace('http://', 'https://')
    except:
        pass
    
    return None

def download_image(url, filename):
    """Download image to file."""
    try:
        resp = requests.get(url, timeout=10)
        if resp.status_code == 200 and len(resp.content) > 500:
            with open(IMAGES_DIR / filename, 'wb') as f:
                f.write(resp.content)
            return True
    except:
        pass
    return False

def show_status():
    """Show download status."""
    status = load_status()
    mapping = load_mapping()
    not_found_list = load_not_found()
    
    completed = sum(1 for b in BOOKS if f"{b[0]}|{b[1]}" in mapping)
    total = len(BOOKS)
    
    print(f"\nDownload Status:")
    print(f"  Completed: {completed}/{total} ({completed*100//total}%)")
    print(f"  Not Found: {len(not_found_list)}")
    print(f"  Remaining: {total - completed - len(not_found_list)}")
    print(f"  Last updated: {status.get('last_updated', 'Never')}\n")

def show_not_found():
    """Show all books without images found."""
    not_found_list = load_not_found()
    
    if not not_found_list:
        print("\nNo books without images. All books either have downloaded images or are pending download.\n")
        return
    
    print(f"\nBooks without images found ({len(not_found_list)}):")
    print("="*80)
    for title, author in sorted(not_found_list, key=lambda x: (x[1], x[0])):
        print(f"  {title:50s} - {author}")
    print("="*80 + "\n")

def download_batch(batch_size=10):
    """Download next batch of images."""
    status = load_status()
    mapping = load_mapping()
    not_found_list = load_not_found()
    
    to_download = []
    for title, author in BOOKS:
        key = f"{title}|{author}"
        if key not in mapping and [title, author] not in not_found_list:
            to_download.append((title, author))
            if len(to_download) >= batch_size:
                break
    
    if not to_download:
        print("All images already downloaded!")
        return
    
    print(f"Downloading {len(to_download)} images...\n")
    
    success = 0
    failed = []
    for i, (title, author) in enumerate(to_download, 1):
        print(f"[{i}/{len(to_download)}] {title[:40]:40s} {author[:20]:20s} ", end='', flush=True)
        
        url = fetch_image(title, author)
        if url:
            filename = f"{get_image_hash(title, author)}.jpg"
            if download_image(url, filename):
                mapping[f"{title}|{author}"] = filename
                success += 1
                print("OK")
            else:
                print("DL FAIL")
                failed.append([title, author])
        else:
            print("NOT FOUND")
            failed.append([title, author])
    
    # Update not_found list
    not_found_list.extend(failed)
    not_found_list = list({json.dumps(b, sort_keys=True): b for b in not_found_list}.values())  # Deduplicate
    
    save_mapping(mapping)
    save_not_found(not_found_list)
    status['last_updated'] = datetime.now().isoformat()
    save_status(status)
    
    print(f"\nCompleted: {success}/{len(to_download)}")
    if failed:
        print(f"Not Found: {len(failed)}")
    
    completed = len(mapping)
    total = len(BOOKS)
    print(f"Total Progress: {completed}/{total} ({completed*100//total}%)\n")

def download_by_author(author_name):
    """Download all images for a specific author."""
    books_by_author = [(t, a) for t, a in BOOKS if a.lower() == author_name.lower()]
    
    if not books_by_author:
        print(f"No books found for author: {author_name}")
        return
    
    print(f"Found {len(books_by_author)} books by {author_name}\n")
    
    mapping = load_mapping()
    not_found_list = load_not_found()
    to_download = [(t, a) for t, a in books_by_author if f"{t}|{a}" not in mapping and [t, a] not in not_found_list]
    
    if not to_download:
        print("All images for this author already downloaded!")
        # Show which ones were not found
        already_not_found = [[t, a] for t, a in books_by_author if [t, a] in not_found_list]
        if already_not_found:
            print(f"\n{len(already_not_found)} books by this author have no images available:")
            for title, author in already_not_found:
                print(f"  - {title}")
        return
    
    print(f"Downloading {len(to_download)} images...\n")
    
    success = 0
    failed = []
    for i, (title, author) in enumerate(to_download, 1):
        print(f"[{i}/{len(to_download)}] {title[:50]:50s} ", end='', flush=True)
        
        url = fetch_image(title, author)
        if url:
            filename = f"{get_image_hash(title, author)}.jpg"
            if download_image(url, filename):
                mapping[f"{title}|{author}"] = filename
                success += 1
                print("OK")
            else:
                print("DL FAIL")
                failed.append([title, author])
        else:
            print("NOT FOUND")
            failed.append([title, author])
    
    # Update not_found list
    not_found_list.extend(failed)
    not_found_list = list({json.dumps(b, sort_keys=True): b for b in not_found_list}.values())  # Deduplicate
    
    save_mapping(mapping)
    save_not_found(not_found_list)
    print(f"\nCompleted: {success}/{len(to_download)}")
    if failed:
        print(f"\nNOT FOUND ({len(failed)}):")
        for title, author in failed:
            print(f"  - {title} by {author}")

def main():
    if len(sys.argv) > 1:
        if sys.argv[1] == "--status":
            show_status()
        elif sys.argv[1] == "--list-not-found":
            show_not_found()
        elif sys.argv[1] == "--author" and len(sys.argv) > 2:
            author = " ".join(sys.argv[2:])
            download_by_author(author)
        else:
            try:
                batch_size = int(sys.argv[1])
                download_batch(batch_size)
            except ValueError:
                print("Usage:")
                print("  python download_images.py              # Download next 10")
                print("  python download_images.py 5            # Download next 5")
                print("  python download_images.py --author John # Download by author")
                print("  python download_images.py --status     # Show progress")
                print("  python download_images.py --list-not-found  # List books without images")
    else:
        download_batch(10)

if __name__ == "__main__":
    main()
