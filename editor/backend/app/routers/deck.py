from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from io import BytesIO, StringIO
from domain import card_service
from domain.deck import Deck
from domain.deck_card import DeckCard
import domain.deck_service as deck_service
import domain.deck_card_service as deck_card_service
from commom.excptions import (
    CardNotFound,
    DeckNotFound,
    DeckAlreadyExists,
    CardNotOnDeck,
    CardIsCommander,
    ShortPartial,
    InvalidQuantity,
)
import csv
import json

from editor.backend.app.schemas.deck import (
    CompleteDeckRead,
    DeckCreate,
    DeckInDB,
    DeckList,
    DeckUpdate,
)
from editor.backend.app.schemas.deck_cards import DeckQuantity, FullDeckCards

router = APIRouter(prefix="/api/decks", tags=["deck"])


def convert_exception_to_http(e: Exception) -> HTTPException:
    if isinstance(e, CardNotFound):
        return HTTPException(status_code=404, detail=e.message)
    elif isinstance(e, DeckNotFound):
        return HTTPException(status_code=404, detail=e.message)
    elif isinstance(e, DeckAlreadyExists):
        return HTTPException(status_code=400, detail=e.message)
    elif isinstance(e, CardNotOnDeck):
        return HTTPException(status_code=404, detail=e.message)
    elif isinstance(e, CardIsCommander):
        return HTTPException(status_code=400, detail=e.message)
    elif isinstance(e, ShortPartial):
        return HTTPException(status_code=400, detail=e.message)
    elif isinstance(e, InvalidQuantity):
        return HTTPException(status_code=400, detail=e.message)
    return None


@router.get("/", response_model=DeckList)
def list_decks():
    try:
        decks = deck_service.get_decks()
        return DeckList(decks=decks)
    except Exception as e:
        return {"error": str(e)}


@router.get("/{id}", response_model=CompleteDeckRead)
def get_deck(id: int):
    try:
        deck = deck_service.get_deck_by_id(id)
        assert deck.name is not None, "Deck should have a name"
        deck, deck_cards = deck_card_service.get_deck_data_by_name(deck.name)

        return {
            "name": deck.name,
            "id": deck.id,
            "last_update": deck.last_update,
            "cards": deck_cards,
        }
    except HTTPException:
        raise
    except (CardNotFound, DeckNotFound) as e:
        http_exc = convert_exception_to_http(e)
        if http_exc:
            raise http_exc
        raise
    except Exception as e:
        return {"error": str(e)}


@router.post("/", response_model=DeckInDB, status_code=201)
def create_deck(new_deck: DeckCreate):
    try:
        deck = deck_service.get_deck_by_name(new_deck.name)
        if deck:
            raise DeckAlreadyExists(new_deck.name)

        deck = Deck(name=new_deck.name)
        deck.update()
        if new_deck.commander:
            card = card_service.get_card_by_name(new_deck.commander)
            deck = deck_service.create_deck_with_cards(
                new_deck.name, [{"card": card, "quantidade": 1}]
            )
        else:
            deck = deck_service.create_deck(deck)
        return deck
    except HTTPException:
        raise
    except (DeckAlreadyExists, CardNotFound) as e:
        http_exc = convert_exception_to_http(e)
        if http_exc:
            raise http_exc
        raise
    except Exception as e:
        return {"error": str(e)}


@router.put("/{id}", response_model=DeckInDB)
def rename_deck(id: int, data: DeckUpdate):
    try:
        deck = deck_service.get_deck_by_id(id)
        dest = deck_service.get_deck_by_name(data.name)
        if dest:
            raise DeckAlreadyExists(data.name)
        assert deck.name is not None, "Deck should have a name"
        deck_service.rename_deck(deck.name, data.name)
        return deck_service.get_deck_by_name(data.name)
    except HTTPException:
        raise
    except (DeckNotFound, DeckAlreadyExists) as e:
        http_exc = convert_exception_to_http(e)
        if http_exc:
            raise http_exc
        raise
    except Exception as e:
        return {"error": str(e)}


@router.delete("/{id}", status_code=204)
def delete_deck(id: int):
    try:
        deck = deck_service.get_deck_by_id(id)
        assert deck.name is not None, "Deck should have a name"
        deck_service.delete_deck(deck.name)
        return
    except HTTPException:
        raise
    except DeckNotFound as e:
        http_exc = convert_exception_to_http(e)
        if http_exc:
            raise http_exc
        raise
    except Exception as e:
        return {"error": str(e)}


@router.post("/{id}/copy", response_model=DeckInDB, status_code=201)
def copy_deck(id: int, dest: DeckUpdate):
    try:
        deck = deck_service.get_deck_by_id(id)
        if not deck:
            raise HTTPException(status_code=404, detail="Deck not found")
        assert deck.name is not None, "Deck should have a name"
        dest_deck = deck_service.get_deck_by_name(dest.name)
        if dest_deck:
            raise HTTPException(status_code=400, detail="Deck already exists")
        deck_service.copy_deck(deck, dest.name)
        resp = deck_service.get_deck_by_name(dest.name)
        return resp
    except HTTPException as e:
        raise e
    except Exception as e:
        return {"error": str(e)}


@router.get("/{id}/txt")
def export_txt(id: int):
    try:
        deck = deck_service.get_deck_by_id(id)
        if not deck:
            raise HTTPException(status_code=404, detail="Deck not found")
        assert deck.name is not None, "Deck should have a name"
        _, cards = deck_card_service.get_deck_data_by_name(deck.name)
        txt = []
        for card in cards:
            if card.is_commander:
                txt.insert(0, f"{card.quantidade} {card.card.name}")
            else:
                txt.append(f"{card.quantidade} {card.card.name}")
        path = deck.name + ".txt"
        buffer = StringIO("\n".join(txt))
        return StreamingResponse(
            buffer,
            media_type="text/plain",
            headers={"Content-Disposition": f'attachment; filename="{path}"'},
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        return {"error": str(e)}


@router.get("/{id}/csv")
def export_csv(id: int):
    try:
        deck = deck_service.get_deck_by_id(id)
        if not deck:
            raise HTTPException(status_code=404, detail="Deck not found")
        assert deck.name is not None, "Deck should have a name"
        _, cards = deck_card_service.get_deck_data_by_name(deck.name)

        buffer = StringIO()
        writer = csv.writer(buffer)
        writer.writerow(["Quantity", "Card"])
        rows = []

        for card in cards:
            if card.is_commander:
                writer.writerow([card.quantidade, card.card.name])
            else:
                rows.append([card.quantidade, card.card.name])
        writer.writerows(rows)
        buffer.seek(0)
        path = deck.name + ".csv"
        return StreamingResponse(
            buffer,
            media_type="text/csv",
            headers={"Content-Disposition": f'attachment; filename="{path}"'},
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        return {"error": str(e)}


@router.get(
    "/{id}/json",
)
def export_json(id: int):
    try:
        deck = deck_service.get_deck_by_id(id)
        if not deck:
            raise HTTPException(status_code=404, detail="Deck not found")
        assert deck.name is not None, "Deck should have a name"
        _, cards = deck_card_service.get_deck_data_by_name(deck.name)

        data = []
        for card in cards:
            if card.is_commander:
                data.insert(0, {"card": card.card.name, "quantity": card.quantidade})
            else:
                data.append({"card": card.card.name, "quantity": card.quantidade})
        json_bytes = json.dumps(data, indent=4).encode("utf-8")
        buffer = BytesIO(json_bytes)
        path = deck.name + ".json"
        return StreamingResponse(
            buffer,
            media_type="application/json",
            headers={"Content-Disposition": f'attachment; filename="{path}"'},
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        return {"error": str(e)}


@router.post("/{id}/txt", response_model=CompleteDeckRead)
def import_txt(id: int):
    pass


@router.get("/{id}/all", response_model=CompleteDeckRead)
def export_all(id: int):
    pass


@router.get("/{id}/analyze", response_model=dict)
def analize_deck(id: int):
    pass


@router.post("/{id}/add", response_model=FullDeckCards)
def add_card(id: int, body: DeckQuantity):
    try:
        if body.quantidade <= 0:
            raise InvalidQuantity(body.quantidade)
        deck = deck_service.get_deck_by_id(id)
        card = card_service.get_card_by_id(body.card_id)
        assert card.name is not None, "Card should have a name"
        dc = deck_card_service.get_deck_commanders_name(card.name)
        if not dc:
            dc = DeckCard(
                deck_id=deck.id,
                card=card,
                quantidade=body.quantidade,
                is_commander=False,
            )
        else:
            dc.quantidade = body.quantidade
        deck_card_service.update_or_insert_deck_card(dc)
        assert deck.id is not None, "Deck should have an id"
        assert card.id is not None, "Card should have an id"
        dc = deck_card_service.get_deck_card(deck.id, card.id)
        if not dc:
            raise HTTPException(status_code=404, detail="Deck card not found")
        return dc
    except HTTPException:
        raise
    except (InvalidQuantity, DeckNotFound, CardNotFound) as e:
        http_exc = convert_exception_to_http(e)
        if http_exc:
            raise http_exc
        raise
    except Exception as e:
        return {"error": str(e)}


@router.post("/{id}/remove", response_model=FullDeckCards)
def remove_card(id: int, body: DeckQuantity):
    try:
        if body.quantidade <= 0:
            raise InvalidQuantity(body.quantidade)
        deck = deck_service.get_deck_by_id(id)
        card = card_service.get_card_by_id(body.card_id)
        assert card.name is not None, "Card should have a name"
        assert deck.id is not None, "Deck should have an id"
        assert card.id is not None, "Card should have an id"
        dc = deck_card_service.get_deck_card(deck.id, card.id)
        if not dc:
            assert deck.name is not None
            raise CardNotOnDeck(card.name, deck.name)
        assert dc.quantidade is not None, "Deck card should have a qty"
        if dc.quantidade <= body.quantidade:
            deck_card_service.delete_deck_card(dc)
            return DeckCard(card=card, quantidade=0, is_commander=False)
        dc.quantidade -= body.quantidade
        deck_card_service.update_deck_card_quantity(dc)
        return dc
    except HTTPException:
        raise
    except (InvalidQuantity, DeckNotFound, CardNotFound, CardNotOnDeck) as e:
        http_exc = convert_exception_to_http(e)
        if http_exc:
            raise http_exc
        raise
    except Exception as e:
        return {"error": str(e)}


@router.delete("/{id}/commander", status_code=204)
def reset_commander(id: int):
    try:
        deck = deck_service.get_deck_by_id(id)
        if not deck:
            raise HTTPException(status_code=404, detail="Deck not found")
        assert deck.id is not None, "Deck should have a id"
        deck_card_service.reset_deck_commander(deck.id)
    except Exception as e:
        return {"error": str(e)}


@router.post("/{id}/commander", response_model=FullDeckCards)
def set_commander(id: int, card_id: str):
    try:
        deck = deck_service.get_deck_by_id(id)
        assert deck.id is not None, "Deck should have a id"
        card = card_service.get_card_by_id(card_id)
        dc = deck_card_service.get_deck_card(deck.id, card_id)
        if not dc:
            assert deck.name is not None
            raise CardNotOnDeck(card.name, deck.name)
        deck_card_service.set_deck_commander(dc)
        return dc
    except HTTPException:
        raise
    except (DeckNotFound, CardNotFound, CardNotOnDeck) as e:
        http_exc = convert_exception_to_http(e)
        if http_exc:
            raise http_exc
        raise
    except Exception as e:
        return {"error": str(e)}


@router.get("/{id}/commander", response_model=FullDeckCards)
def get_commander(id: int):
    try:
        deck = deck_service.get_deck_by_id(id)
        if not deck:
            raise HTTPException(status_code=404, detail="Deck not found")
        commander = deck_card_service.get_deck_commanders_name(id)
        if not commander:
            raise HTTPException(status_code=404, detail="Commander not found")
        card = card_service.get_card_by_name(commander)
        assert deck.id is not None, "Deck should have an id"
        assert card.id is not None, "Card should have an id"
        deck_card = deck_card_service.get_deck_card(deck.id, card.id)
        return deck_card
    except HTTPException as e:
        raise e
    except Exception as e:
        return {"error": str(e)}
