from db import transaction
from external.api import get_card_from_api, get_many_cards_from_api
from datetime import datetime


def list_decks():
    with transaction() as t:
        decks = t.execute("SELECT * FROM decks ORDER BY last_update DESC;").fetchall()
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


def get_deck_cards_by_name(deck_name):
    with transaction() as t:
        sql = """
        SELECT deck_cards.card_id, deck_cards.quantidade, deck_cards.is_commander
        FROM deck_cards
        INNER JOIN decks ON deck_cards.deck_id = decks.id
        WHERE decks.nome = ?
        """
        deck_cards = t.execute(sql, (deck_name,)).fetchall()
        return deck_cards


def get_cards_by_deck_name(deck_name):
    with transaction() as t:
        sql = """
        SELECT deck_cards.quantidade, cards.name, deck_cards.is_commander
        FROM deck_cards
        INNER JOIN cards ON deck_cards.card_id = cards.id
        INNER JOIN decks ON deck_cards.deck_id = decks.id
        WHERE decks.nome = ?
        """
        deck_cards = t.execute(sql, (deck_name,)).fetchall()
        return deck_cards


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


def create_deck(deck_name, cursor=None):
    with transaction(cursor=cursor) as t:
        last_updated = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        t.execute(
            "INSERT INTO decks (nome, last_update) VALUES (?, ?);",
            (
                deck_name,
                last_updated,
            ),
        )
        deck = t.execute("SELECT * FROM decks WHERE nome = ?", (deck_name,)).fetchone()
        return deck


def create_deck_with_initial_commander(deck_name, commander_id):
    with transaction() as t:
        last_updated = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        t.execute(
            "INSERT INTO decks (nome, last_update) VALUES (?, ?);",
            (
                deck_name,
                last_updated,
            ),
        )
        deck = t.execute("SELECT * FROM decks WHERE nome = ?", (deck_name,)).fetchone()
        t.execute(
            "INSERT INTO deck_cards (deck_id, card_id, quantidade, is_commander) VALUES (?, ?, 1, TRUE);",
            (deck[0], commander_id),
        )
        return deck


def copy_deck(new, old):
    old_cards = get_deck_cards_by_name(old)
    with transaction() as t:
        new_deck = create_deck(new, cursor=t)

        rows = [
            (new_deck[0], card_id, quantidade, is_commander)
            for (card_id, quantidade, is_commander) in old_cards
        ]

        sql = """
        INSERT INTO deck_cards (deck_id, card_id, quantidade, is_commander)
        VALUES (?, ?, ?, ?);
        """

        t.executemany(sql, rows)


def delete_deck(deck_id):
    # TODO: CHANGE TO CASCADE LATER
    with transaction() as t:
        t.execute("DELETE FROM deck_cards WHERE deck_id = ?", (deck_id,))
        t.execute("DELETE FROM decks WHERE id = ?", (deck_id,))


def rename_deck(old_name, new_name):
    with transaction() as t:
        t.execute("UPDATE decks SET nome = ? WHERE nome = ?", (new_name, old_name))


def replace_deck(old_name, new_cards, cursor=None):
    with transaction(cursor=cursor) as t:
        t.execute(
            "DELETE FROM deck_cards WHERE deck_id = (SELECT id FROM decks WHERE nome = ?)",
            (old_name,),
        )
        t.executemany(
            "INSERT INTO deck_cards (deck_id, card_id, quantidade, is_commander) VALUES (?, ?, ?, ?);",
            new_cards,
        )


def get_many_cards(card_list, cursor=None):
    cards = get_many_cards_from_api(card_list)
    if not cards:
        return {}
    cards = cards["cards"]
    with transaction(cursor=cursor) as t:
        cards_data = []
        for card in cards:
            cards_data.append(
                (
                    card["id"],
                    card["name"],
                    card["colors"],
                    card["color_identity"],
                    card["cmc"],
                    card["mana_cost"],
                    card["image"],
                    card["art"],
                    card["legal_commanders"],
                    card["is_commander"],
                    card["price"],
                )
            )
        t.executemany(
            "INSERT OR REPLACE INTO cards (id, name, colors, color_identity, cmc, mana_cost, image, art, legal_commanders, is_commander, price) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);",
            cards_data,
        )
        return cards


def insert_cards(deck_id, cards_data, cursor=None):
    with transaction(cursor=cursor) as t:
        cards = []
        for card in cards_data:
            cards.append(
                [deck_id, card["id"], card["quantidade"], card["is_commander"]]
            )
        t.executemany(
            "INSERT INTO deck_cards (deck_id, card_id, quantidade, is_commander) VALUES (?, ?, ?, ?);",
            cards,
        )


def crete_and_insert_cards(deck_name, card_list, cursor=None):
    with transaction(cursor=cursor) as t:
        deck = create_deck(deck_name, cursor=t)
        deck_id = deck[0]
        insert_cards(deck_id, card_list, cursor=t)


def remove_card_from_deck(deck_id, card_id, cursor=None):
    with transaction(cursor=cursor) as t:
        t.execute(
            "DELETE FROM deck_cards WHERE deck_id = ? and card_id = ?",
            [deck_id, card_id],
        )


def add_card_to_deck(deck_id, card_id, qty, cursor=None, commander=False):
    with transaction(cursor=cursor) as t:
        deck_card = t.execute(
            "SELECT * FROM deck_cards WHERE deck_id = ? and card_id = ?",
            [deck_id, card_id],
        ).fetchone()
        if deck_card and not commander:
            qty = deck_card[2] + qty
        t.execute(
            "INSERT OR REPLACE INTO deck_cards (deck_id, card_id, quantidade, is_commander) VALUES (?, ?, ?, ?);",
            [deck_id, card_id, qty, commander],
        )


def reset_comander_of_deck(deck_id, cursor=None):
    with transaction(cursor=cursor) as t:
        t.execute(
            "UPDATE deck_cards SET is_commander = FALSE WHERE deck_id = ?", [deck_id]
        )


def set_commander(deck_id, commander_id):
    with transaction() as t:
        remove_card_from_deck(deck_id, commander_id, cursor=t)
        reset_comander_of_deck(deck_id, cursor=t)
        add_card_to_deck(deck_id, commander_id, 1, commander=True, cursor=t)
