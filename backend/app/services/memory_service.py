from datetime import datetime

from sqlalchemy.orm import Session

from backend.app.database.models import Conversation, Message


def create_conversation(db: Session) -> Conversation:
    """Créer une nouvelle conversation."""
    conversation = Conversation(title="Nouvelle conversation")

    db.add(conversation)
    db.commit()
    db.refresh(conversation)

    return conversation


def save_message(
    db: Session,
    conversation_id: int,
    role: str,
    content: str
) -> Message:
    """Enregistrer un message dans une conversation."""

    if role not in ["user", "assistant"]:
        raise ValueError("Role must be 'user' or 'assistant'.")

    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id
    ).first()

    if conversation is None:
        raise ValueError("Conversation not found.")

    message = Message(
        conversation_id=conversation_id,
        role=role,
        content=content
    )

    db.add(message)

    # Mettre à jour la date de modification de la conversation.
    conversation.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(message)

    return message


def get_conversation_history(
    db: Session,
    conversation_id: int,
    limit: int = 20
) -> list[dict]:
    """Récupérer les derniers messages d'une conversation."""

    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id
    ).first()

    if conversation is None:
        raise ValueError("Conversation not found.")

    messages = (
        db.query(Message)
        .filter(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.desc(), Message.id.desc())
        .limit(limit)
        .all()
    )

    # Les messages doivent être dans l'ordre chronologique.
    messages.reverse()

    return [
        {
            "role": message.role,
            "content": message.content
        }
        for message in messages
    ]