from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.app.database.connection import get_db
from backend.app.database.models import Conversation, Message
from backend.app.api.schemas.chat import ChatMessageCreate
from backend.app.services.memory_service import (
    create_conversation,
    save_message,
    get_conversation_history
)
from backend.app.agents.business_agent import run_business_agent


router = APIRouter(
    prefix="/api/v1/chat",
    tags=["Chat"]
)


@router.post("/")
def chat(
    request: ChatMessageCreate,
    db: Session = Depends(get_db)
):
    try:
        # 1. Créer ou récupérer la conversation
        if request.conversation_id is None:
            conversation = create_conversation(db)
        else:
            conversation = db.query(Conversation).filter(
                Conversation.id == request.conversation_id
            ).first()

            if conversation is None:
                raise HTTPException(
                    status_code=404,
                    detail="Conversation not found."
                )

        conversation_id = conversation.id

        # 2. Récupérer l'ancien historique
        history = get_conversation_history(
            db,
            conversation_id
        )

        # 3. Enregistrer le message utilisateur
        save_message(
            db,
            conversation_id,
            "user",
            request.content
        )

        # 4. Envoyer le message et l'historique à Gemini
        agent_result = run_business_agent(
            user_message=request.content,
            db=db,
            history=history
        )

        if not agent_result.get("success"):
            raise HTTPException(
                status_code=500,
                detail=agent_result.get(
                    "message",
                    "Agent execution failed."
                )
            )

        assistant_response = agent_result.get("response")

        if not assistant_response:
            raise HTTPException(
                status_code=500,
                detail="The agent returned an empty response."
            )

        # 5. Enregistrer la réponse de l'agent
        save_message(
            db,
            conversation_id,
            "assistant",
            assistant_response
        )

        # 6. Retourner la réponse
        return {
            "success": True,
            "conversation_id": conversation_id,
            "response": assistant_response,
            "tools_used": agent_result.get("tools_used", []),
            "tool_results": agent_result.get("tool_results", [])
        }

    except HTTPException:
        raise

    except Exception as error:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Chat error: {str(error)}"
        )


# Récupérer toutes les conversations
@router.get("/conversations")
def get_all_conversations(db: Session = Depends(get_db)):
    conversations = (
        db.query(Conversation)
        .order_by(Conversation.updated_at.desc())
        .all()
    )

    results = []

    for conversation in conversations:
        # Récupérer le dernier message de chaque conversation
        last_message = (
            db.query(Message)
            .filter(Message.conversation_id == conversation.id)
            .order_by(Message.created_at.desc(), Message.id.desc())
            .first()
        )

        results.append({
            "id": conversation.id,
            "title": conversation.title,
            "created_at": conversation.created_at,
            "updated_at": conversation.updated_at,
            "last_message": last_message.content if last_message else ""
        })

    return results


# Récupérer une conversation avec tous ses messages
@router.get("/conversations/{conversation_id}")
def get_conversation(
    conversation_id: int,
    db: Session = Depends(get_db)
):
    conversation = (
        db.query(Conversation)
        .filter(Conversation.id == conversation_id)
        .first()
    )

    if conversation is None:
        raise HTTPException(
            status_code=404,
            detail="Conversation not found."
        )

    messages = (
        db.query(Message)
        .filter(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.asc(), Message.id.asc())
        .all()
    )

    return {
        "id": conversation.id,
        "title": conversation.title,
        "created_at": conversation.created_at,
        "updated_at": conversation.updated_at,
        "messages": [
            {
                "id": msg.id,
                "role": msg.role,
                "content": msg.content,
                "created_at": msg.created_at
            }
            for msg in messages
        ]
    }