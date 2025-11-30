# Interactive Shell

The `edhelper` shell provides an interactive REPL (Read-Eval-Print Loop) for managing decks and cards. It can be installed separately as `edhelper[shell]`.

## Installation

```bash
pip install edhelper[shell]
```

## Starting the Shell

```bash
edhelper shell
```

The shell will start with a prompt showing the current command number:

```
[ 1 ] > 
```

When a deck is selected, the prompt changes to show the deck name:

```
[ 2 ] : [ MyDeck ] > 
```

## Commands

### Root Mode Commands

These commands are available when no deck is selected:

#### Deck Selection

```bash
select MyDeck
# or
cd MyDeck
```

#### Deck Management

```bash
# Create deck
create MyDeck
# or
mk MyDeck

# Rename deck
rename OldName NewName
# or
mv OldName NewName

# Delete deck
delete MyDeck
# or
del MyDeck

# Copy deck
copy SourceDeck NewDeck
# or
cp SourceDeck NewDeck
```

#### Export

```bash
# Export all decks
export_all /path/to/export/

# Export specific deck
export_txt /path/to/export/ MyDeck
export_csv /path/to/export/ MyDeck
export_json /path/to/export/ MyDeck
```

#### Import

```bash
import_txt /path/to/file.txt MyDeck
```

#### Card Search

```bash
# Find card
find "Lightning Bolt"

# Search cards
search "lightning"
```

#### Meta Commands

```bash
# List categories for commander
meta "Atraxa, Praetors' Voice"

# Get cards from category
meta "Atraxa, Praetors' Voice" "Top Cards"
```

#### Top Commanders

```bash
# List top 100 commanders (uses pager)
top-commanders
```

#### Utility

```bash
# Clear screen
clear
# or
cls

# Exit shell
exit
```

### Deck Mode Commands

These commands are available when a deck is selected:

#### Card Management

```bash
# Add card
add "Lightning Bolt" 1

# Remove card
remove "Lightning Bolt" 1
# or
rmc "Lightning Bolt" 1
```

#### Commander Management

```bash
# Show current commander
commander

# Set commander
set-commander "Atraxa, Praetors' Voice"

# Reset commander
reset-commander
```

#### View Deck

```bash
# List deck cards
list
# or
ls

# List with limit
list 10
```

#### Analysis

```bash
# Analyze deck
analize
```

#### Export

```bash
# Export current deck
export_txt /path/to/export/
export_csv /path/to/export/
export_json /path/to/export/
```

#### Card Search

```bash
# Find card
find "Lightning Bolt"

# Search cards
search "lightning"
```

#### Meta Commands

```bash
# Get meta cards
meta "Atraxa, Praetors' Voice" "Top Cards"
```

## Autocomplete

The shell provides autocomplete for:

- Commands
- Deck names
- Card names (from saved cards)
- File paths

Press `TAB` to trigger autocomplete.

## Examples

### Basic Workflow

```
[ 1 ] > create MyDeck
[ 2 ] > select MyDeck
[ 3 ] : [ MyDeck ] > add "Sol Ring" 1
[ 4 ] : [ MyDeck ] > add "Lightning Bolt" 4
[ 5 ] : [ MyDeck ] > list
[ 6 ] : [ MyDeck ] > exit
```

### Using Meta Cards

```
[ 1 ] > meta "Atraxa, Praetors' Voice"
Available categories for 'Atraxa, Praetors' Voice':
  - New Cards
  - High Synergy Cards
  - Top Cards
  ...

[ 2 ] > meta "Atraxa, Praetors' Voice" "Top Cards"
Fetching 50 cards from category 'Top Cards'...
Found 50 cards. Saved to database.
[Table with cards displayed]

[ 3 ] > select MyDeck
[ 4 ] : [ MyDeck ] > add "Suggested Card" 1
```

### Top Commanders

```
[ 1 ] > top-commanders
Fetching top 100 commanders...
Found 100 commanders. Saved to database.
[Opens in pager - use arrow keys to navigate, 'q' to exit]
```

## Error Handling

The shell handles errors gracefully and displays user-friendly messages:

- Invalid commands show suggestions
- Missing decks/cards show clear error messages
- Validation errors are displayed immediately

## Tips

1. **Use autocomplete**: Press `TAB` to see available options
2. **Command history**: Use arrow keys to navigate command history
3. **Context awareness**: Commands change based on whether a deck is selected
4. **Pager for long output**: Top commanders and large lists use a pager automatically

## Exiting

```bash
exit
# or press Ctrl+D
# or press Ctrl+C
```

