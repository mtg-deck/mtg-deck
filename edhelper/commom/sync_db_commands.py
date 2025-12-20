import click
import edhelper.domain.card_service as card_service
import edhelper.domain.deck_service as deck_service
import edhelper.domain.deck_card_service as deck_card_service
from edhelper.external.api import get_many_cards_from_api, get_card_from_api
from edhelper.infra.config import settings
from edhelper.commom.excptions import SyncNotAvailable, CardNotFound, DeckNotFound


class SyncDbCommands:
    @staticmethod
    def sync_database():
        """Sync all cards in database with API."""
        if not settings.can_sync():
            raise SyncNotAvailable()
        click.echo("Fetching all card names from database...")
        card_names = card_service.get_card_names()

        if not card_names:
            click.echo("No cards found in database.")
            return

        click.echo(f"Found {len(card_names)} cards. Updating from API...")

        try:
            # Fetch updated cards from API
            updated_cards = get_many_cards_from_api(card_names)

            # Update database
            card_service.insert_or_update_cards(updated_cards)

            click.echo(f"Successfully updated {len(updated_cards)} cards.")
        except Exception as e:
            click.echo(f"Error syncing database: {e}", err=True)
            raise

    @staticmethod
    def sync_database_shell():
        """Sync all cards in database with API (for shell)."""
        if not settings.can_sync():
            raise SyncNotAvailable()
        print("Fetching all card names from database...")
        card_names = card_service.get_card_names()

        if not card_names:
            print("No cards found in database.")
            return

        print(f"Found {len(card_names)} cards. Updating from API...")

        try:
            updated_cards = get_many_cards_from_api(card_names)

            card_service.insert_or_update_cards(updated_cards)

            print(f"Successfully updated {len(updated_cards)} cards.")
        except Exception as e:
            print(f"Error syncing database: {e}")
            raise

    @staticmethod
    def sync_card(card_id: str):
        if not settings.can_sync_card():
            raise SyncNotAvailable()
        card = card_service.get_card_by_id(card_id)
        if not card:
            raise CardNotFound(card_id)
        try:
            assert card.name is not None, "Card name is None"
            updated_card = get_card_from_api(card.name)
            card_service.insert_or_update_card(updated_card)
            settings.set_card_sync_timestamp()
        except Exception as e:
            print(f"Error syncing database: {e}")
            raise

    @staticmethod
    def sync_deck(deck_id: int):
        if not settings.can_sync_deck():
            raise SyncNotAvailable()
        deck = deck_service.get_deck_by_id(deck_id)
        if not deck:
            raise DeckNotFound(deck_id)
        try:
            assert deck.name is not None, "Deck name is None"
            deck, data = deck_card_service.get_deck_data_by_name(deck.name)
            cards = []
            for deck_card in data:
                name = deck_card.card.name
                cards.append(name)
            updated_deck = get_many_cards_from_api(cards)
            card_service.insert_or_update_cards(updated_deck)
            settings.set_deck_sync_timestamp()
        except Exception as e:
            raise e
