# **mtg-commander**

A command-line deck builder, analyzer, and management tool for *Magic: The Gathering* — focused on the Commander (EDH) format.

`mtg-commander` allows you to create, modify, validate, analyze, import, export, and manage Commander decks entirely from the terminal.

---

## **📦 Installation**

```bash
pip install mtg-commander
```

or with **pipx**:

```bash
pipx install mtg-commander
```

---

## **🚀 Basic Usage**

```bash
mtg-commander <deck-name> [options]
```

* Opens the program with the specified deck loaded.
* Automatically creates the deck if it does not exist.

Example:

```bash
mtg-commander Yuriko-Ninjas
```

---

## **📖 Options**

### **General**

| Flag              | Description                                                    |
| ----------------- | -------------------------------------------------------------- |
| `-h`, `--help`    | Display help information.                                      |
| `-v`, `--version` | Show program version.                                          |
| `--info`          | Show app metadata, version, config paths, and number of decks. |

---

### **User & Authentication**

| Flag                 | Description               |
| -------------------- | ------------------------- |
| `--get-key`          | Set account key.     |
| `--logout`           | Clear stored credentials. |

---

### **Deck Creation**

| Flag                      | Description                             |
| ------------------------- | --------------------------------------- |
| `-f <file>`               | Create a new deck from a `.txt` file.   |
| `--commander <card-name>` | Set commander when creating a new deck. |

---

### **Deck Analysis**

| Flag             | Description                                       |
| ---------------- | ------------------------------------------------- |
| `--analyze`      | Analyze the deck without launching the UI.        |
| `--validade`     | Validate a Commander deck.                        |
| `-c <card-name>` | Analyze a single card (only without a deck/file). |
| `--recommend`    | Provide card recommendations for the deck.        |

---

### **Exporting**

| Flag                           | Description                                 |
| ------------------------------ | ------------------------------------------- |
| `--export-txt <path>`          | Export deck as `.txt`.                      |
| `--export-csv <path>`          | Export deck as `.csv`.                      |
| `--export-json <path>`         | Export deck as `.json`.                     |
| `--export-cb`                  | Export deck to clipboard.                   |
| `--export-decks <archive.zip>` | Export all decks as `.txt` into a zip file. |

---

### **Deck Management**

| Flag                    | Description           |
| ----------------------- | --------------------- |
| `--list-decks`          | List all saved decks. |
| `--delete <deck>`       | Delete a deck.        |
| `--rename <old> <new>`  | Rename a deck.        |
| `--copy <source> <new>` | Duplicate a deck.     |

---

### **Importing**

| Flag                     | Description                            |
| ------------------------ | -------------------------------------- |
| `--import-folder <path>` | Import all `.txt` decks from a folder. |

---

### **Randomization**

| Flag                 | Description                     |
| -------------------- | ------------------------------- |
| `--random <n>`       | Fetch *n* random Magic cards.   |
| `--random-commander` | Fetch a random legal Commander. |

---

## **🧰 Examples**

**Create or open a deck**

```bash
mtg-commander Atraxa
```

**Create a deck from a txt file**

```bash
mtg-commander MyDeck -f list.txt
```

**Analyze a deck without opening the full program**

```bash
mtg-commander MyDeck --analyze
```

**Validate a deck**

```bash
mtg-commander MyDeck --validade
```

**Get a random commander**

```bash
mtg-commander --random-commander
```

**Export a deck**

```bash
mtg-commander MyDeck --export-json mydeck.json
```

---

## **🧪 Development**

Clone the repository:

```bash
git clone https://github.com/mtg-deck/mtg-deck.git
cd mtg-deck
```

Install in editable mode:

```bash
pip install -e .
```

Run tests:

```bash
pytest
```

---

## **🐛 Reporting Issues**

If you find bugs or want new features, open an issue:

```
https://github.com/mtg-deck/mtg-deck/issues
```

---

## **📄 License**

MIT
