"""
Serviço proativo: lê os alertas criados pelo ML no banco e os empurra via WhatsApp.
Esse é o processo "Ativo" (Push Notifications).
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from loguru import logger
import google.generativeai as genai

from app.models.alert import Alert
from app.models.store import Store
from app.connectors.evolution_api import EvolutionAPIConnector


class AlertDispatcher:
    """Dispara alertas críticos do ML via WhatsApp ativamente para a loja."""

    def __init__(self, session: AsyncSession, store_id: int):
        self.session = session
        self.store_id = store_id
        
        # Pode usar um mini-LLM para escrever a notificação em tom natural
        self.model = genai.GenerativeModel("gemini-1.5-flash")

    async def dispatch_pending_alerts(self) -> dict:
        """
        Busca alertas que acabaram de ser gerados e ainda não foram sinalizados
        como is_read ou despachados (geralmente depois que o pipeline do Sprint 3 rodar).
        Para não spammar, agrupa ou envia só os críticos.
        """
        # Carregar loja para pegar alert_phones
        stmt_store = select(Store).where(Store.id == self.store_id)
        result_store = await self.session.execute(stmt_store)
        store = result_store.scalars().first()
        
        if not store or not store.alert_phones:
            logger.warning(f"Loja id={self.store_id} sem 'alert_phones' configurado.")
            return {"success": False, "reason": "no alert phones configured"}

        # Buscar até 5 alertas críticos que não foram lidos
        stmt_alerts = (
            select(Alert)
            .where(Alert.store_id == self.store_id, Alert.is_read == False, Alert.severity == "critical")
            .limit(5)
        )
        result_alerts = await self.session.execute(stmt_alerts)
        alerts = result_alerts.scalars().all()

        if not alerts:
            return {"success": True, "dispatched": 0, "reason": "no critical alerts"}

        # Montar um prompt pro Gemini reescrever os alertas como notificação amigável
        alert_details = "\n".join([f"- Produto de ID {a.product_id}: {a.alert_type}. {a.message} Ação recomendada: {a.suggested_action}" for a in alerts])
        
        prompt = (
            "Você é o 'Gôndola', IA assistente de supermercado. "
            "Reescreva os seguintes alertas de estoque/validade em UMA única mensagem proativa do WhatsApp "
            "direta e amigável (sem enrolação, mas destacando urgência), para mandar ao gerente agora mesmo:\n\n"
            f"{alert_details}"
        )
        
        try:
            response = self.model.generate_content(prompt)
            final_text = response.text
        except Exception as e:
            logger.error(f"[DISPATCHER] Falha no Gemini ao formatar alertas: {e}")
            final_text = f"🚨 *Alerta Automático (Sistema)*:\n\n{alert_details}"
            
        # Conectar na API e despachar
        connector = EvolutionAPIConnector(
             instance_name=store.evolution_instance_name or "gondolabot",
             instance_token=store.evolution_instance_token or ""
        )
        
        phones = [p.strip() for p in store.alert_phones.split(",")]
        success_count = 0
        
        for phone in phones:
             if await connector.send_text(phone=phone, text=final_text):
                 success_count += 1
                 
        # Marcar como lido para não encher o saco
        for a in alerts:
            a.is_read = True
            
        await self.session.commit()
        
        logger.info(f"✅ Disparados {len(alerts)} agrupados para {success_count} números.")
        return {"success": True, "dispatched": len(alerts), "destinations": success_count}
