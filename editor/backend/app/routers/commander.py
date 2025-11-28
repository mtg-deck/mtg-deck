from fastapi import APIRouter, HTTPException
from external.edhec import get_edhrec_cardlists
from external.api import get_commanders_from_api, get_many_cards_from_api
import domain.card_service as card_service
from commom.excptions import CardNotFound, DeckNotFound
from editor.backend.app.schemas.card import CommanderList

router = APIRouter(prefix="/api/commander", tags=["commander"])

CATEGORIES = [
    "New Cards",
    "Basic Lands",
    "High Synergy Cards",
    "Top Cards",
    "Game Changers",
    "Creatures",
    "Instants",
    "Sorceries",
    "Utility Artifacts",
    "Enchantments",
    "Battles",
    "Planeswalkers",
    "Utility Lands",
    "Mana Artifacts",
]


def convert_exception_to_http(e: Exception) -> HTTPException:
    if isinstance(e, CardNotFound):
        return HTTPException(status_code=404, detail=e.message)
    elif isinstance(e, DeckNotFound):
        return HTTPException(status_code=404, detail=e.message)
    return None


@router.get("/", response_model=CommanderList)
def get_top_commanders():
    try:
        commanders = get_commanders_from_api()
        card_service.insert_or_update_cards(commanders)
        return CommanderList(cards=commanders)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{name}/meta", response_model=dict)
def get_commander_meta(name: str, category: str | None = None):
    try:
        card_list = get_edhrec_cardlists(name)

        if not card_list:
            raise HTTPException(
                status_code=404, detail=f"No meta data found for commander {name}"
            )

        if category != "Basic Lands" and category not in card_list:
            available_categories = [cat for cat in CATEGORIES if cat in card_list]
            available_categories.append("Basic Lands")
            raise HTTPException(
                status_code=400,
                detail=f"Category '{category}' not found. Available categories: {', '.join(available_categories)}",
            )

        if category == "Basic Lands":
            card = card_service.get_card_by_name(name)
            if not card:
                raise CardNotFound(name)
            card_ci = card.color_identity
            card_names = []
            if card_ci is not None:
                if "W" in card_ci:
                    card_names.append("Plains")
                if "U" in card_ci:
                    card_names.append("Swamp")
                if "B" in card_ci:
                    card_names.append("Island")
                if "R" in card_ci:
                    card_names.append("Mountain")
                if "G" in card_ci:
                    card_names.append("Forest")
        else:
            card_names = card_list[category]
        print("==============================")
        print(card_names)
        print("==============================")
        if not card_names:
            return {"commander": name, "category": category, "cards": []}

        cards = get_many_cards_from_api(card_names)

        card_service.insert_or_update_cards(cards)

        cards_dict = []
        for card in cards:
            cards_dict.append(
                {
                    "id": card.id,
                    "name": card.name,
                    "colors": card.colors,
                    "color_identity": card.color_identity,
                    "cmc": card.cmc,
                    "mana_cost": card.mana_cost,
                    "image": card.image,
                    "art": card.art,
                    "legal_commanders": card.legal_commanders,
                    "is_commander": card.is_commander,
                    "price": card.price,
                    "edhrec_rank": card.edhrec_rank,
                }
            )

        return {"commander": name, "category": category, "cards": cards_dict}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
