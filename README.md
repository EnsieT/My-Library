# My Library

A personal book library web application built from Goodreads exports. Browse, search, filter, and review your entire book collection with a beautiful, dark-themed interface.

## Features

✨ **Interactive Dashboard**
- View complete book collection with cover images
- Browse by category (Fiction, Non-Fiction, Spirituality & Religion)
- Search across titles, authors, and categories
- Filter by reading status and rating

📊 **Insights & Analytics**
- Overview stats (total books, read, reading, to-read)
- Reading statistics and insights
- Category distribution charts
- Bar charts showing genre breakdowns

⭐ **Reviews & Ratings**
- View all submitted book reviews
- Filter reviews by star rating (1-5 stars)
- Sort reviews by date, rating, text length, or title
- Click book cards to jump directly to reviews

📱 **Fully Responsive Design**
- Desktop: Multi-column grid layout
- Tablet: Horizontal scrolling nav, 2-column grid
- Mobile: 2-column book grid, full-screen modals
- Touch-friendly tap targets (44px minimum)

📚 **Book Management**
- Track reading dates (date_read, date_added)
- Mark books as owned, read, currently reading, or to-read
- View extended book details in modal popups
- Deduplication logic to handle owned + Goodreads entries

## Technology Stack

- **Frontend**: HTML5, CSS3 (dark theme with gradients), Vanilla JavaScript
- **Data**: JSON (generated from Goodreads CSV export)
- **Images**: 235+ local cover images (jpg format)
- **Hosting**: GitHub Pages (static site)

## Project Structure

```
.
├── index.html                    # Main web app (SPA)
├── library_data.json             # Generated book database
├── image_mapping.json            # Title/Author → image hash mapping
├── images/                       # Cover image assets (235+ images)
├── goodreads_library_export.csv  # Goodreads export (source)
├── owned_books.csv               # CSV of owned books (source)
├── build_library.py              # Build script (generates JSON from CSVs)
└── download_images.py            # Image downloader (Goodreads → local)
```

## Getting Started

### 1. View Locally

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/My-Library.git
cd My-Library

# Serve locally (Python 3.11+)
python -m http.server 8000
```

Then open `http://localhost:8000` in your browser.

### 2. Rebuild Library Data

If you update the CSV files (`goodreads_library_export.csv`, `owned_books.csv`):

```bash
python build_library.py
```

This will:
- Merge owned books with Goodreads entries
- Normalize titles and deduplicate
- Assign categories
- Generate `library_data.json`

### 3. Download/Update Images

To refresh cover images from Goodreads:

```bash
python download_images.py
```

This will:
- Scrape cover URLs from Goodreads
- Download images locally to `images/` folder
- Update `image_mapping.json`

## Data Sources

- **Goodreads Export**: Exported from Goodreads account (Settings → Export Library)
  - Contains: Title, Author, ISBN, My Rating, Average Rating, Read Count, Date Read, Exclusive Shelf, etc.
- **Owned Books**: Manual CSV of books owned locally
  - Format: `title, author, condition` (status: owned)

## Deduplication Logic

The build process automatically deduplicates books by:

1. **Exact Match**: Normalizes trailing series info `(Series, #N)` and matches by title + author
2. **Subtitle Match**: Strips subtitle after first colon for near-duplicates
   - Example: "Fooled by Randomness" + "Fooled by Randomness: The Hidden Role..." → merged
3. **Merge Strategy**: Keeps richest data set
   - Prefers entry with review/rating/date
   - Marks as owned if any entry is owned
   - Keeps best status (read > currently-reading > to-read > owned)

Result: 273 unique books from ~290 raw entries (296→280 after initial dedup, +7 subtitle dedup).

## UI Features

### Desktop
- 6-column responsive book grid
- Horizontal tab navigation
- Modal overlays for book details
- Sticky navigation

### Tablet (≤768px)
- Horizontal-scrollable nav tabs
- Text/filter inputs stack vertically
- 4-column book grid
- Nearly full-screen modals

### Mobile (≤480px)
- 2-column book grid with 8px gaps
- Full-screen modals (no border radius)
- Compact stat cards
- 44px+ touch targets on all buttons
- Font sizes scaled for readability

### Touch (smartphones/tablets)
- All buttons/filters require 40-44px minimum height
- Smooth scrolling with `-webkit-overflow-scrolling: touch`
- Notch-aware viewport with `viewport-fit=cover`

## Deployment to GitHub Pages

### Step 1: Create GitHub Repository

1. Go to [github.com/new](https://github.com/new)
2. Create a public repository named `My-Library`
3. Copy the repository URL

### Step 2: Push to GitHub

```bash
# Configure git (first time only)
git config user.name "Your Name"
git config user.email "your@email.com"

# Add all files
git add .

# Create initial commit
git commit -m "Initial commit: Book library with 273 books and reviews"

# Add remote and push
git remote add origin https://github.com/YOUR_USERNAME/My-Library.git
git branch -M main
git push -u origin main
```

### Step 3: Enable GitHub Pages

1. Go to repository Settings → Pages
2. Select Deploy from a branch → **main** branch → **/root** folder
3. Wait for deployment (usually 1-2 minutes)
4. Site will be live at `https://YOUR_USERNAME.github.io/My-Library/`

### Step 4: Update Custom Domain (Optional)

In Settings → Pages, you can point a custom domain to the GitHub Pages URL.

## Usage Tips

- **Search**: Type to filter across titles, authors, categories
- **Filter by Status**: Read, Currently Reading, To Read, Owned
- **Filter by Rating**: 5⭐ down to 1⭐
- **Sort**: By title, author, rating, pages, or date read
- **Jump to Review**: Click the "review" badge on any book card to jump to its full review
- **Category Browsing**: Use tabs to filter by Fiction, Non-Fiction, or Spirituality & Religion
- **Sub-categories**: Each main category has sub-category pills (e.g., Science Fiction, Fantasy under Fiction)

## Statistics

- **Total Books**: 273
- **With Reviews**: 102
- **Read**: 237
- **Currently Reading**: 1
- **To Read**: 11
- **Owned Only**: 24
- **Fiction**: 202 books
- **Non-Fiction**: 59 books
- **Spirituality & Religion**: 28 books
- **Cover Images**: 235 local downloads (~95%+ success rate)

## Customization

### Colors
Edit `:root` CSS variables in `index.html`:
```css
:root {
  --bg: #0f0f13;           /* Dark background */
  --accent: #7c6df0;       /* Purple accent */
  --gold: #f5c542;         /* Rating stars */
  --fiction: #7c6df0;      /* Fiction category color */
  --nonfiction: #60a5fa;   /* Non-Fiction color */
  --spirituality: #f5c542; /* Spirituality color */
}
```

### Category Assignments
Edit `CATEGORY_ASSIGNMENTS` dictionary in `build_library.py` to customize category mappings for specific titles.

## Performance

- **Single-page app**: Instant navigation, no page reloads
- **Bundle size**: ~273 KB JSON data + 235 images
- **Load time**: <1s on good connection (all data loads at startup)
- **Image serving**: GitHub Pages with CDN caching

## License

This project is personal/private. Feel free to adapt for your own library.

## Contributing

This is a personal project, but you're welcome to fork and modify for your own book library!

### To add your own books:

1. Export from Goodreads (Settings → Export Library)
2. Update `goodreads_library_export.csv`
3. Add owned books to `owned_books.csv`
4. Run `python build_library.py`
5. Optionally: `python download_images.py` to fetch covers
6. Commit and push: `git add . && git commit -m "Update library" && git push`

---

**Last Updated**: February 2026

Built with ❤️ for book lovers.
