"""
Evolution API Connector — Envia mensagens de WhatsApp (Mocked/Real).

Se `EVOLUTION_API_URL` não for configurado no ambiente, esta classe loga
as mensagens em console para simulação (modo desenvolvimento/sem Docker).
Se configurado, faz requisições HTTP reais para a Evolution v2.
"""

import os
import httpx
from loguru import logger
from typing import Optional


class EvolutionAPIConnector:
    def __init__(self, instance_name: str, instance_token: str):
         self.instance_name = instance_name
         self.instance_token = instance_token
         self.base_url = os.getenv("EVOLUTION_API_URL", "").rstrip("/")
         self.global_api_key = os.getenv("EVOLUTION_API_KEY", "")
         
         if not self.base_url:
             logger.warning(
                 f"[EVOLUTION] Modo MOCK ativado para instância '{instance_name}'. "
                 "Nenhuma mensagem real de WhatsApp será enviada."
             )
    
    async def send_text(self, phone: str, text: str) -> bool:
        """Envia uma mensagem de texto."""
        # Sanitizar telefone (garantir que tem o sufixo correto para Evolution)
        phone_sanitized = "".join(filter(str.isdigit, phone))
        
        if not self.base_url:
            logger.info(f"\n[MOCK WHATSAPP] => {phone_sanitized}\n{text}\n")
            return True
            
        url = f"{self.base_url}/message/sendText/{self.instance_name}"
        headers = {
            "apikey": self.global_api_key,
            "Content-Type": "application/json"
        }
        payload = {
            "number": phone_sanitized,
            "text": text,
            "delay": 1200  # Pequeno delay para simular digitação
        }
        
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.post(url, json=payload, headers=headers, timeout=10)
                resp.raise_for_status()
                return True
        except Exception as e:
            logger.error(f"[EVOLUTION] Erro ao enviar text para {phone_sanitized}: {e}")
            return False

    async def send_image(self, phone: str, image_url: str, caption: str = "") -> bool:
        """Envia uma imagem com legenda."""
        phone_sanitized = "".join(filter(str.isdigit, phone))
        
        if not self.base_url:
            logger.info(f"\n[MOCK WHATSAPP IMAGE] => {phone_sanitized} | URL: {image_url}\nLegenda: {caption}\n")
            return True
            
        url = f"{self.base_url}/message/sendMedia/{self.instance_name}"
        headers = {
            "apikey": self.global_api_key,
            "Content-Type": "application/json"
        }
        payload = {
            "number": phone_sanitized,
            "mediaMessage": {
                "mediatype": "image",
                "media": image_url,
                "caption": caption
            }
        }
        
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.post(url, json=payload, headers=headers, timeout=15)
                resp.raise_for_status()
                return True
        except Exception as e:
            logger.error(f"[EVOLUTION] Erro ao enviar imagem para {phone_sanitized}: {e}")
            return False
