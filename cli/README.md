# CLI Commands

This module contains all CLI commands for `edhelper`. It can be installed separately as `edhelper[cli]`.

## Installation

```bash
pip install edhelper[cli]
```

## Commands

### Deck Commands

#### Create Deck

```bash
# Create empty deck
edhelper deck create MyDeck

# Create deck with commander
edhelper deck create MyDeck "Atraxa, Praetors' Voice"
```

#### Open/Create Deck

```bash
# Opens existing deck or creates new one
edhelper deck open MyDeck

# Open with commander
edhelper deck open MyDeck "Atraxa, Praetors' Voice"
```

#### Import Deck

```bash
# Import from .txt file
edhelper deck import-txt decklist.txt MyDeck
```

#### Delete Deck

```bash
edhelper deck delete MyDeck
```

#### Rename Deck

```bash
edhelper deck rename OldName NewName
```

#### Copy Deck

```bash
edhelper deck copy SourceDeck NewDeck
```

#### List Decks

```bash
# List all decks
edhelper deck list

# List with limit
edhelper deck list 10
```

#### Show Deck

```bash
# Show deck contents
edhelper deck show MyDeck
```

#### Commander Management

```bash
# Set commander
edhelper deck set-commander MyDeck "Atraxa, Praetors' Voice"

# Reset commander
edhelper deck reset-commander MyDeck
```

#### Deck Meta (EDHREC)

```bash
# List available categories
edhelper deck meta "Atraxa, Praetors' Voice"

# Get cards from specific category
edhelper deck meta "Atraxa, Praetors' Voice" "Top Cards"
```

Available categories:
- New Cards
- High Synergy Cards
- Top Cards
- Game Changers
- Creatures
- Instants
- Sorceries
- Utility Artifacts
- Enchantments
- Battles
- Planeswalkers
- Utility Lands
- Mana Artifacts

#### Deck Cards

```bash
# Add card
edhelper deck add MyDeck "Lightning Bolt" 1

# Remove card
edhelper deck remove MyDeck "Lightning Bolt" 1

# Set card quantity
edhelper deck set MyDeck "Lightning Bolt" --qty 4
```

### Card Commands

#### Find Card

```bash
edhelper card find "Lightning Bolt"
```

#### Search Cards

```bash
# Search by partial name (minimum 3 characters)
edhelper card search "lightning"
```

#### Top Commanders

```bash
# List top 100 commanders (uses pager)
edhelper card top-commanders
```

### Export Commands

#### Export to TXT

```bash
edhelper export txt MyDeck /path/to/export/
```

#### Export to CSV

```bash
edhelper export csv MyDeck /path/to/export/
```

#### Export to JSON

```bash
edhelper export json MyDeck /path/to/export/
```

#### Export All Decks

```bash
edhelper export all /path/to/export/
```

## Error Handling

All commands use custom exceptions that provide clear error messages:

- `CardNotFound` - Card not found in database or API
- `DeckNotFound` - Deck does not exist
- `DeckAlreadyExists` - Deck name already in use
- `CardNotOnDeck` - Card is not in the specified deck
- `CardIsCommander` - Operation not allowed on commander
- `ShortPartial` - Search partial must be at least 3 characters
- `InvalidQuantity` - Invalid quantity value

## Examples

### Complete Workflow

```bash
# 1. Create a new deck
edhelper deck create MyCommanderDeck "Atraxa, Praetors' Voice"

# 2. Search for cards
edhelper card search "sol ring"

# 3. Add cards to deck
edhelper deck add MyCommanderDeck "Sol Ring" 1
edhelper deck add MyCommanderDeck "Lightning Bolt" 4

# 4. Get meta suggestions
edhelper deck meta "Atraxa, Praetors' Voice" "Top Cards"

# 5. View deck
edhelper deck show MyCommanderDeck

# 6. Export deck
edhelper export txt MyCommanderDeck ./exports/
```

### Using Top Commanders

```bash
# Get top commanders (opens in pager)
edhelper card top-commanders

# Navigate with arrow keys, exit with 'q'
```

### Meta Cards Workflow

```bash
# 1. Check available categories
edhelper deck meta "Atraxa, Praetors' Voice"

# 2. Get cards from a category
edhelper deck meta "Atraxa, Praetors' Voice" "Top Cards"

# 3. Add suggested cards to your deck
edhelper deck add MyDeck "Suggested Card" 1
```

