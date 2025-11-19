from db import transaction
from external.api import get_card_from_api, get_many_cards_from_api


def list_decks():
    with transaction() as t:
        decks = t.execute("SELECT * FROM decks;").fetchall()
        return decks


def get_commander_name_from_deck(deck_id):
    with transaction() as t:
        commander_id = t.execute(
            "SELECT card_id FROM deck_cards WHERE deck_id = ? and is_commander = TRUE;",
            (deck_id,),
        ).fetchone()
        if commander_id:
            commander_name = t.execute(
                "SELECT name FROM cards WHERE id = ?", (commander_id[0],)
            ).fetchone()
            if commander_name:
                return commander_name[0]
            return ""
        return ""


def get_deck_by_name(deck_name):
    with transaction() as t:
        deck = t.execute("SELECT * FROM decks WHERE nome = ?", (deck_name,)).fetchone()
        return deck


def get_deck_cards(deck_id):
    with transaction() as t:
        deck_cards = t.execute(
            "SELECT card_id, quantidade, is_commander FROM deck_cards WHERE deck_id = ?",
            (deck_id,),
        ).fetchall()
        cards = []
        for card in deck_cards:
            cards_data = t.execute(
                "SELECT name FROM cards WHERE id = ?", (card[0],)
            ).fetchone()
            cards.append([card[1], cards_data[0], "COMMANDER" if card[2] else ""])
        return cards


def add_card_to_db(card_json):
    with transaction() as t:
        params = (
            card_json["id"],
            card_json["name"],
            card_json["colors"],
            card_json["color_identity"],
            card_json["cmc"],
            card_json["mana_cost"],
            card_json["image"],
            card_json["art"],
            card_json["legal_commanders"],
            card_json["is_commander"],
            card_json["price"],
        )

        t.execute(
            """
            INSERT OR REPLACE INTO cards 
            (id, name, colors, color_identity, cmc, mana_cost, image, art, legal_commanders, is_commander, price)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
            """,
            params,
        )

        card = t.execute(
            "SELECT * FROM cards WHERE id = ?", (card_json["id"],)
        ).fetchone()

        return card


def get_card_by_name(card_name):
    with transaction() as t:
        card = t.execute("SELECT * FROM cards WHERE name = ?", (card_name,)).fetchone()
        if not card:
            card = get_card_from_api(card_name)
            if card:
                add_card_to_db(card)
            else:
                return None
        else:
            card_data = {}
            card_data["id"] = card[0]
            card_data["name"] = card[1]
            card_data["colors"] = card[2]
            card_data["color_identity"] = card[3]
            card_data["cmc"] = card[4]
            card_data["mana_cost"] = card[5]
            card_data["image"] = card[6]
            card_data["art"] = card[7]
            card_data["legal_commanders"] = card[8]
            card_data["is_commander"] = card[9]
            card_data["price"] = card[10]
            return card_data
        return card


def get_many_cards_by_name(card_names):
    cards = get_many_cards_from_api(card_names)
    for card in cards:
        add_card_to_db(card)
