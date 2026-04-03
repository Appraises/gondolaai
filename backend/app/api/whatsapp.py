"""
Rotas para o Webhook do WhatsApp via Evolution API.
Aqui o Gôndola.ai recebe mensagens, verifica permissões e ativa o Gemini.
"""

from fastapi import APIRouter, Depends, Request, Header
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from loguru import logger

from app.database import get_db
from app.models.store import Store
from app.services.ai_agent import GondolaAgent
from app.connectors.evolution_api import EvolutionAPIConnector


router = APIRouter()


@router.post("/webhook")
async def evolution_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """
    Recebe os eventos 'messages-upsert' da Evolution API.
    Apenas processa mensagens TEXTUAIS vindas do manager_phone da loja configurada.
    """
    try:
        payload = await request.json()
    except Exception:
        return {"status": "ignored", "reason": "invalid json"}

    # Evolution API v2 payload format:
    # { "event": "messages.upsert", "instance": "gondolabot", "data": { "message": { "conversation": "Hello!" }, "key": { "remoteJid": "5511999999999@s.whatsapp.net", "fromMe": false } } }
    
    event = payload.get("event")
    
    # Processar apenas novas mensagens recebidas
    if event != "messages.upsert":
        return {"status": "ignored", "reason": "not messages.upsert"}
        
    data = payload.get("data", {})
    if not data or data.get("key", {}).get("fromMe") == True:
        return {"status": "ignored", "reason": "fromMe or empty data"}
        
    remote_jid = data.get("key", {}).get("remoteJid", "")
    phone_sender = remote_jid.split("@")[0] if "@" in remote_jid else remote_jid
    
    # Extrair texto da mensagem (Pode vir em conversation ou extendedTextMessage.text)
    message_obj = data.get("message", {})
    text = ""
    if "conversation" in message_obj:
        text = message_obj["conversation"]
    elif "extendedTextMessage" in message_obj:
        text = message_obj["extendedTextMessage"].get("text", "")
        
    if not text:
        return {"status": "ignored", "reason": "empty text"}

    instance_name = payload.get("instance")
    
    logger.info(f"[WHATSAPP_WEBHOOK] Instância: {instance_name} | De: {phone_sender} | Txt: {text}")

    # 1. Identificar de qual loja é este webhook e checar se o sender é o Manager
    # Estamos buscando a loja que esteja atrelada a esta evolution_instance_name e cujo manager_phone bata
    query = select(Store).where(Store.manager_phone == phone_sender)
    
    # Se a loja também tiver a instance name configurada, melhor o filtro:
    if instance_name:
        query = query.where(Store.evolution_instance_name == instance_name)
        
    result = await db.execute(query)
    store = result.scalars().first()
    
    if not store:
        logger.warning(f"Mensagem de {phone_sender} ignorada. Não é gerente ou a instância {instance_name} não bate.")
        return {"status": "ignored", "reason": "unauthorized phone"}
        
    # 2. Iniciar o Cérebro (Gemini) e passar a mensagem
    agent = GondolaAgent(store_id=store.id)
    bot_response = await agent.get_response(text, db)
    
    # 3. Mandar resposta de volta via Evolution API
    connector = EvolutionAPIConnector(
        instance_name=store.evolution_instance_name or "gondolabot",
        instance_token=store.evolution_instance_token or ""
    )
    
    success = await connector.send_text(phone=phone_sender, text=bot_response)
    
    return {"status": "processed", "replied": success}
