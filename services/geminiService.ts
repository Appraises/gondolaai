import { GoogleGenAI, Type } from "@google/genai";
import { PromotionSuggestion } from "../types";

const ai = new GoogleGenAI({ apiKey: process.env.API_KEY });

export const generatePromotionStrategy = async (
  productName: string,
  daysUntilExpiry: number,
  stock: number,
  price: number
): Promise<PromotionSuggestion[]> => {
  
  try {
    const model = 'gemini-2.5-flash';
    
    const prompt = `
      Atue como um especialista em gestão de varejo e perdas para supermercados.
      Tenho o seguinte produto no meu inventário que precisa ser vendido rapidamente para evitar perdas:
      
      Produto: ${productName}
      Dias para validade: ${daysUntilExpiry} dias
      Estoque atual: ${stock} unidades
      Preço original: R$ ${price.toFixed(2)}

      Com base na urgência (validade) e no volume de estoque, gere 3 estratégias de promoção distintas para zerar esse estoque sem destruir completamente a margem de lucro, mas priorizando a venda antes do vencimento.
      
      Retorne APENAS um JSON.
    `;

    const response = await ai.models.generateContent({
      model,
      contents: prompt,
      config: {
        responseMimeType: "application/json",
        responseSchema: {
          type: Type.ARRAY,
          items: {
            type: Type.OBJECT,
            properties: {
              title: { type: Type.STRING, description: "Nome curto e chamativo da promoção" },
              strategy: { type: Type.STRING, description: "Descrição detalhada da mecânica da venda" },
              discount: { type: Type.STRING, description: "Percentual ou valor sugerido de desconto (ex: '30% OFF' ou 'Leve 3 Pague 2')" },
              reasoning: { type: Type.STRING, description: "Por que essa estratégia funciona para este cenário de validade" }
            },
            required: ["title", "strategy", "discount", "reasoning"]
          }
        }
      }
    });

    if (response.text) {
      return JSON.parse(response.text) as PromotionSuggestion[];
    }
    
    throw new Error("No response text generated");

  } catch (error) {
    console.error("Error generating promotion strategy:", error);
    // Fallback data in case of API failure or missing key for demo purposes
    return [
      {
        title: "Oferta Relâmpago de Validade",
        strategy: "Coloque o produto na ilha de destaque 'Próximo ao Vencimento' na entrada da loja.",
        discount: "40% OFF",
        reasoning: "Com apenas alguns dias restantes, o foco é recuperar o custo do produto agressivamente."
      },
      {
        title: "Combo Leve Mais",
        strategy: "Faça um bundle: Leve 3 unidades pelo preço de 2.",
        discount: "33% efetivo",
        reasoning: "Aumenta o volume de saída por cliente, limpando o estoque mais rápido."
      },
      {
        title: "Venda Cruzada",
        strategy: `Na compra de um item complementar, o ${productName} sai com desconto progressivo.`,
        discount: "50% na 2ª unidade",
        reasoning: "Incentiva a compra por impulso associada a produtos de alto giro."
      }
    ];
  }
};