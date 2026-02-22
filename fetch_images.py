#!/usr/bin/env python3
"""Fetch and cache book cover images locally."""

import os
import json
import requests
import hashlib
from pathlib import Path
from urllib.parse import quote

IMAGES_DIR = Path(__file__).parent / "images"
IMAGES_DIR.mkdir(exist_ok=True)
MAPPING_FILE = Path(__file__).parent / "image_mapping.json"

# All books data
GOODREADS_BOOKS = [
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
    ("The Brothers Karamazov", "Fyodor Dostoyevsky"),
    ("Keepers of the Kalachakra", "Ashwin Sanghi"),
    ("Ikigai", "Héctor García"),
    ("Land of the Seven Rivers", "Sanjeev Sanyal"),
    ("One Hundred Years of Solitude", "Gabriel García Márquez"),
    ("The Valmiki Ramayana Vol. 3", "Valmiki"),
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
    ("Homo Deus", "Yuval Noah Harari"),
    ("The Four", "Scott Galloway"),
    ("Summer Lightning", "P.G. Wodehouse"),
    ("Five Point Someone", "Chetan Bhagat"),
    ("Something Fresh", "P.G. Wodehouse"),
    ("Wings of Fire", "A.P.J. Abdul Kalam"),
    ("Angels & Demons", "Dan Brown"),
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
    ("A Column of Fire", "Ken Follett"),
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
    ("Freedom", "Jonathan Franzen"),
    ("Midnight's Children", "Salman Rushdie"),
    ("The Satanic Verses", "Salman Rushdie"),
    ("Sidney Sheldon's The Silent Widow", "Tilly Bagshawe"),
    ("Life over Two Beers and other stories", "Sanjeev Sanyal"),
    ("Asura", "Anand Neelakantan"),
    ("In the Shadow of the Banyan", "Vaddey Ratner"),
    ("When Breath Becomes Air", "Paul Kalanithi"),
    ("Kafka on the Shore", "Haruki Murakami"),
    ("Slaughterhouse-Five", "Kurt Vonnegut Jr."),
    ("Infinite Jest", "David Foster Wallace"),
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
    ("1Q84", "Haruki Murakami"),
    ("The Great Gatsby", "F. Scott Fitzgerald"),
    ("Playing It My Way", "Sachin Tendulkar"),
    ("Shalimar the Clown", "Salman Rushdie"),
    ("The Lovely Bones", "Alice Sebold"),
    ("The Sicilian", "Mario Puzo"),
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
    ("Right Ho, Jeeves", "P.G. Wodehouse"),
    ("The Da Vinci Code", "Dan Brown"),
    ("Pride and Prejudice", "Jane Austen"),
    ("The Book Thief", "Markus Zusak"),
    ("The Other Side of Midnight", "Sidney Sheldon"),
    ("The Immortals of Meluha", "Amish Tripathi"),
    ("Wicked Lovely", "Melissa Marr"),
    ("A Brief History of Time", "Stephen W. Hawking"),
    ("Evil Under the Sun", "Agatha Christie"),
    ("Inferno", "Dan Brown"),
    ("The Catcher in the Rye", "J.D. Salinger"),
    ("So Long, and Thanks for All the Fish", "Douglas Adams"),
    ("Ink Exchange", "Melissa Marr"),
    ("Harry Potter and the Chamber of Secrets", "J.K. Rowling"),
    ("A Thousand Splendid Suns", "Khaled Hosseini"),
    ("The Witch of Portobello", "Paulo Coelho"),
    ("The Lost Symbol", "Dan Brown"),
    ("8th Confession", "James Patterson"),
    ("Fooled by Randomness", "Nassim Nicholas Taleb"),
    ("Maximum City", "Suketu Mehta"),
    ("The Family", "Mario Puzo"),
    ("The Godfather", "Mario Puzo"),
    ("Jeeves and the Feudal Spirit", "P.G. Wodehouse"),
    ("Joy: The Happiness That Comes from Within", "Osho"),
    ("Harry Potter and the Deathly Hallows", "J.K. Rowling"),
    ("If Tomorrow Comes", "Sidney Sheldon"),
    ("The Namesake", "Jhumpa Lahiri"),
    ("Into the Silent Land", "Paul Broks"),
    ("One Night at the Call Center", "Chetan Bhagat"),
    ("Omerta", "Mario Puzo"),
    ("Catch-22", "Joseph Heller"),
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
    ("The Secret Adversary", "Agatha Christie"),
    ("2 States", "Chetan Bhagat"),
    ("I, Robot", "Isaac Asimov"),
    ("Right Ho, Jeeves (Jeeves, #6)", "P.G. Wodehouse"),
    ("Airport", "Arthur Hailey"),
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
    ("The Alchemist", "Paulo Coelho"),
    ("Not a Penny More, Not a Penny Less", "Jeffrey Archer"),
    ("The Graveyard Book", "Neil Gaiman"),
    ("The Almighty", "Irving Wallace"),
    ("The Fan Club", "Irving Wallace"),
    ("Harry Potter and the Order of the Phoenix", "J.K. Rowling"),
    ("Fragile Eternity", "Melissa Marr"),
    ("The Restaurant at the End of the Universe", "Douglas Adams"),
    ("The Hitchhiker's Guide to the Galaxy Part 1", "Douglas Adams"),
    ("Operation Karakoram", "Arvind Nayar"),
    ("Mostly Harmless", "Douglas Adams"),
    ("The Ultimate Hitchhiker's Guide to the Galaxy", "Douglas Adams"),
]

def get_image_key(title, author):
    """Generate a consistent filename key for a book."""
    hash_suffix = hashlib.md5(f"{title}|{author}".encode()).hexdigest()[:8]
    return f"{hash_suffix}"

def fetch_from_open_library(title, author):
    """Try to fetch image from Open Library API."""
    try:
        query = quote(f"{title} {author}")
        url = f"https://openlibrary.org/search.json?title={query}&author={quote(author)}&limit=1"
        response = requests.get(url, timeout=3)
        if response.status_code == 200:
            data = response.json()
            if data.get('docs') and len(data['docs']) > 0 and 'cover_id' in data['docs'][0]:
                cover_id = data['docs'][0]['cover_id']
                return f"https://covers.openlibrary.org/b/id/{cover_id}-M.jpg"
    except:
        pass
    return None

def download_image(image_url, filename):
    """Download image from URL and save locally."""
    try:
        response = requests.get(image_url, timeout=3)
        if response.status_code == 200:
            file_path = IMAGES_DIR / filename
            with open(file_path, 'wb') as f:
                f.write(response.content)
            return True
    except:
        pass
    return False

def main():
    print("Fetching book images...")
    print("Total books: " + str(len(GOODREADS_BOOKS)))
    
    mapping = {}
    successful = 0
    failed = 0
    
    for idx, (title, author) in enumerate(GOODREADS_BOOKS, 1):
        key = get_image_key(title, author)
        print("[" + str(idx) + "/" + str(len(GOODREADS_BOOKS)) + "] " + title[:40] + "...")
        
        image_url = fetch_from_open_library(title, author)
        
        if image_url:
            filename = key + ".jpg"
            if download_image(image_url, filename):
                mapping[title + "|" + author] = filename
                successful += 1
                print("  OK")
            else:
                failed += 1
                print("  FAIL")
        else:
            failed += 1
            print("  NOT FOUND")
    
    # Save mapping file
    try:
        with open(MAPPING_FILE, 'w', encoding='utf-8') as f:
            json.dump(mapping, f, indent=2)
        print("\nMapping file saved")
    except Exception as e:
        print("Error saving mapping file: " + str(e))
    
    print("\n--- Results ---")
    print("Total: " + str(len(GOODREADS_BOOKS)))
    print("Successful: " + str(successful))
    print("Failed: " + str(failed))
    if len(GOODREADS_BOOKS) > 0:
        print("Success rate: " + str(round((successful / len(GOODREADS_BOOKS) * 100), 1)) + "%")

if __name__ == "__main__":
    main()
