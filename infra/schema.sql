CREATE TABLE IF NOT EXISTS cards (
	id VARCHAR NOT NULL, 
	name VARCHAR NOT NULL, 
	colors VARCHAR NOT NULL, 
	color_identity VARCHAR NOT NULL, 
	cmc INTEGER NOT NULL, 
	mana_cost VARCHAR NOT NULL, 
	image VARCHAR NOT NULL, 
	art VARCHAR NOT NULL, 
	legal_commanders BOOLEAN NOT NULL, 
	is_commander BOOLEAN NOT NULL, 
	price VARCHAR NOT NULL, 
	PRIMARY KEY (id)
);
CREATE TABLE IF NOT EXISTS decks (
	id INTEGER NOT NULL, 
	nome VARCHAR NOT NULL, 
	last_update DATETIME NOT NULL, 
	PRIMARY KEY (id)
);
CREATE TABLE IF NOT EXISTS deck_cards (
	deck_id INTEGER NOT NULL, 
	card_id VARCHAR NOT NULL, 
	quantidade INTEGER NOT NULL, 
	is_commander BOOLEAN NOT NULL, 
	PRIMARY KEY (deck_id, card_id), 
	FOREIGN KEY(deck_id) REFERENCES decks (id) ON DELETE CASCADE,
	FOREIGN KEY(card_id) REFERENCES cards (id)
);
CREATE INDEX IF NOT EXISTS ix_cards_name ON cards (name);
CREATE INDEX IF NOT EXISTS ix_cards_id ON cards (id);
CREATE INDEX IF NOT EXISTS ix_decks_nome ON decks (nome);
CREATE INDEX IF NOT EXISTS ix_decks_id ON decks (id);
PRAGMA foreign_keys = ON;
