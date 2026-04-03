"""
Serviço do Gemini AI Agente.
Instancia o SDK do Gemini, registra as ferramentas e mantém a memória da sessão.
"""

import os
from loguru import logger
import google.generativeai as genai

from app.services.ai_tools import (
    tool_search_stock,
    tool_get_active_alerts,
    tool_get_sales_today,
)

# Inicializar chave da API (será carregada do .env)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)


class GondolaAgent:
    """Gerente de Bolso - Agente com Gemini que consulta o BD ativamente."""
    
    def __init__(self, store_id: int):
        self.store_id = store_id
        
        # Prompt de Sistema dita a "Personalidade" e as "Regras" do agente
        self.system_instruction = (
            "Você é o 'Gôndola', assistente inteligente de gestão para donos de supermercados. "
            "Você analisa vendas, prediz rupturas e responde a perguntas rápidas. "
            "Sempre seja conciso, proativo e use um tom amigável (de negócios). "
            "Sempre que o usuário perguntar algo que dependa de dados, OBRIGATORIAMENTE "
            "use a ferramenta apropriada para puxar os valores reais antes de responder. "
            "Nunca invente números de faturamento, estoque ou produtos."
        )
        
        if not GEMINI_API_KEY:
            logger.error("[GEMINI] GEMINI_API_KEY não encontrada no .env. Agente não funcionará!")
            self.model = None
            return

        # Model e ferramentas
        self.model = genai.GenerativeModel(
            model_name="gemini-2.5-flash",  # Pode ser gemini-1.5-flash dependendo da doc API do usuário, vamos com gemini-exp ou 1.5
            system_instruction=self.system_instruction,
            tools=[
                {"function_declarations": [
                    {
                        "name": "search_stock",
                        "description": "Busca o preço e a quantidade em estoque atual de um produto no supermercado.",
                        "parameters": {
                            "type": "object",
                            "properties": {"product_name": {"type": "string"}},
                            "required": ["product_name"]
                        }
                    },
                    {
                        "name": "get_active_alerts",
                        "description": "Puxa a lista de alertas críticos ou de ruptura da IA que precisam da atenção do dono da loja.",
                        "parameters": {
                            "type": "object",
                            "properties": {}
                        }
                    },
                    {
                        "name": "get_sales_today",
                        "description": "Lista o total de faturamento do supermercado no dia ou os fechamentos mais recentes. Pode filtrar por departamento.",
                        "parameters": {
                            "type": "object",
                            "properties": {"category": {"type": "string", "description": "Categoria ex: 'Açougue', 'Bebidas' (deixe vazio para total)"}},
                            "required": []
                        }
                    }
                ]}
            ]
        )
        
        # Em produção, a conversa deveria persistir em Redis/DB. 
        # Como é stateless aqui para webhook único (sem memória longa):
        self.chat = self.model.start_chat()

    async def get_response(self, user_message: str, session) -> str:
        """Processa a mensagem do usuário, decide se usa tools e retorna a string final."""
        if not self.model:
            return "Desculpe, estou sem cérebro hoje (API Key do Gemini faltando no servidor)."
            
        logger.info(f"Usuário perguntou: {user_message}")
        
        # Manda pro LLM
        response = self.chat.send_message(user_message)
        
        # Verifica se o modelo quer chamar alguma ferramenta
        for tool_call in response.parts:
            if tool_call.function_call:
                func_name = tool_call.function_call.name
                args = tool_call.function_call.args
                logger.info(f"[GEMINI] Chamando função: {func_name} com args {args}")
                
                # Executa a tool localmente mapeada
                tool_result = ""
                if func_name == "search_stock":
                    tool_result = await tool_search_stock(session, args.get("product_name"), self.store_id)
                elif func_name == "get_active_alerts":
                    tool_result = await tool_get_active_alerts(session, self.store_id)
                elif func_name == "get_sales_today":
                    tool_result = await tool_get_sales_today(session, self.store_id, args.get("category", ""))
                
                logger.debug(f"[GEMINI] Tool result -> {tool_result}")
                
                # Devolve a resposta da tool para o LLM gerar a mensagem final
                response = self.chat.send_message({
                    "function_response": {
                        "name": func_name,
                        "response": {"result": tool_result}
                    }
                })
                
        # O último passo será a string formatada em texto do LLM
        return response.text
