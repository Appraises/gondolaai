import React, { useState } from 'react';
import { Check, X, Zap, Store, Building2, HelpCircle } from 'lucide-react';

const plans = [
  {
    name: "Essencial",
    icon: <Store className="w-6 h-6" />,
    description: "Para mercadinhos que querem parar de perder dinheiro.",
    priceMonthly: 199,
    priceYearly: 159,
    features: [
      "Até 2.000 SKUs monitorados",
      "Alerta de validade por e-mail",
      "Sugestão simples de preço",
      "1 Usuário administrativo",
      "Suporte por E-mail"
    ],
    notIncluded: [
      "Integração automática ERP",
      "IA Geradora de Cartazes",
      "Dashboard Financeiro"
    ],
    highlight: false
  },
  {
    name: "Gôndola Pro",
    icon: <Zap className="w-6 h-6" />,
    description: "Automação total para supermercados em crescimento.",
    priceMonthly: 499,
    priceYearly: 399,
    features: [
      "Até 15.000 SKUs monitorados",
      "Alertas via WhatsApp e App",
      "IA de Promoção (Demo acima)",
      "Integração com ERPs populares",
      "5 Usuários administrativos",
      "Dashboard de Perdas Evitadas",
      "Suporte Prioritário"
    ],
    notIncluded: [],
    highlight: true,
    tag: "MAIS ESCOLHIDO"
  },
  {
    name: "Rede / Franquia",
    icon: <Building2 className="w-6 h-6" />,
    description: "Gestão centralizada para múltiplas lojas.",
    priceMonthly: null, // Sob consulta
    priceYearly: null,
    features: [
      "SKUs Ilimitados",
      "API para integração customizada",
      "Gestão Multi-loja",
      "IA Treinada no seu histórico",
      "Gerente de Sucesso Dedicado",
      "SLA de 99.9%",
      "Treinamento da equipe"
    ],
    notIncluded: [],
    highlight: false
  }
];

const PricingSection: React.FC = () => {
  const [isYearly, setIsYearly] = useState(false);

  return (
    <section id="pricing" className="py-24 bg-zinc-900 border-t border-zinc-800 relative overflow-hidden">
      {/* Background Decorativo */}
      <div className="absolute top-0 left-0 w-full h-px bg-gradient-to-r from-transparent via-zinc-700 to-transparent"></div>
      
      <div className="max-w-7xl mx-auto px-6 relative z-10">
        
        {/* Header da Seção */}
        <div className="text-center mb-16">
          <h2 className="text-brand-500 font-bold tracking-widest uppercase text-sm mb-4">Planos e Preços</h2>
          <h3 className="text-3xl md:text-5xl font-bold text-white mb-6">
            Investimento que se paga <br/>
            <span className="text-zinc-500">na primeira semana.</span>
          </h3>
          <p className="text-zinc-400 max-w-2xl mx-auto text-lg">
            Escolha o nível de inteligência que seu estoque precisa. 
            Sem taxas de setup, cancele quando quiser.
          </p>

          {/* Toggle Anual/Mensal */}
          <div className="flex items-center justify-center gap-4 mt-8">
            <span className={`text-sm font-bold transition-colors ${!isYearly ? 'text-white' : 'text-zinc-500'}`}>Mensal</span>
            <button 
              onClick={() => setIsYearly(!isYearly)}
              className="relative w-14 h-8 rounded-full bg-zinc-800 border border-zinc-700 p-1 transition-colors hover:border-zinc-600 focus:outline-none"
            >
              <div className={`w-6 h-6 bg-brand-500 rounded-full shadow-md transform transition-transform duration-300 ${isYearly ? 'translate-x-6' : 'translate-x-0'}`}></div>
            </button>
            <span className={`text-sm font-bold transition-colors ${isYearly ? 'text-white' : 'text-zinc-500'}`}>
              Anual <span className="text-brand-500 text-xs ml-1 font-normal uppercase tracking-wide">(-20%)</span>
            </span>
          </div>
        </div>

        {/* Grid de Planos - Agora com flex-col para garantir alturas iguais */}
        <div className="grid md:grid-cols-3 gap-8">
          {plans.map((plan, idx) => (
            <div 
              key={idx} 
              className={`
                relative p-8 rounded-2xl border transition-all duration-300 group flex flex-col
                ${plan.highlight 
                  ? 'bg-zinc-900/80 border-brand-500/50 shadow-[0_0_30px_rgba(16,185,129,0.1)] hover:border-brand-500 hover:shadow-[0_0_40px_rgba(16,185,129,0.2)] transform md:-translate-y-4 z-10' 
                  : 'bg-zinc-900/50 border-zinc-800 hover:border-zinc-600 hover:bg-zinc-800/50'
                }
              `}
            >
              {plan.highlight && (
                <div className="absolute -top-4 left-1/2 -translate-x-1/2 bg-brand-600 text-white text-[10px] font-bold px-3 py-1 rounded-full uppercase tracking-widest shadow-lg">
                  {plan.tag}
                </div>
              )}

              <div className="mb-8">
                <div className={`w-12 h-12 rounded-lg flex items-center justify-center mb-6 border ${plan.highlight ? 'bg-brand-900/20 border-brand-500/30 text-brand-400' : 'bg-zinc-800 border-zinc-700 text-zinc-400'}`}>
                  {plan.icon}
                </div>
                <h4 className="text-xl font-bold text-white mb-2">{plan.name}</h4>
                <p className="text-zinc-400 text-sm h-10 line-clamp-2">{plan.description}</p>
              </div>

              {/* Price Container - Altura Fixa e Centralizada */}
              <div className="mb-8 p-4 bg-zinc-950/50 rounded-lg border border-zinc-800/50 text-center flex flex-col justify-center min-h-[104px]">
                {plan.priceMonthly !== null ? (
                  <>
                    <div className="flex items-center justify-center gap-1">
                        <span className="text-3xl font-bold text-white">R$ {isYearly ? plan.priceYearly : plan.priceMonthly}</span>
                        <span className="text-zinc-500 text-sm self-end mb-1">/mês</span>
                    </div>
                    {isYearly && <div className="text-xs text-brand-500 mt-1 font-medium">Cobrado anualmente</div>}
                  </>
                ) : (
                    <div className="flex flex-col items-center justify-center h-full">
                        <span className="text-xl font-bold text-white uppercase tracking-tight">Sob Consulta</span>
                        <span className="text-zinc-500 text-xs mt-1">Personalizado para volume</span>
                    </div>
                )}
              </div>

              {/* Lista de Features - Flex Grow para empurrar botão para baixo */}
              <ul className="space-y-4 mb-8 flex-1">
                {plan.features.map((feature, i) => (
                  <li key={i} className="flex items-start gap-3 text-sm text-zinc-300">
                    <Check size={16} className={`mt-0.5 shrink-0 ${plan.highlight ? 'text-brand-500' : 'text-zinc-500'}`} />
                    <span>{feature}</span>
                  </li>
                ))}
                {plan.notIncluded.map((feature, i) => (
                  <li key={i} className="flex items-start gap-3 text-sm text-zinc-600 line-through decoration-zinc-700">
                    <X size={16} className="mt-0.5 shrink-0 opacity-50" />
                    <span>{feature}</span>
                  </li>
                ))}
              </ul>

              <button className={`
                w-full py-4 rounded-lg font-bold text-sm tracking-wide transition-all uppercase mt-auto
                ${plan.highlight 
                  ? 'bg-brand-600 hover:bg-brand-500 text-white shadow-lg shadow-brand-900/20' 
                  : 'bg-zinc-800 hover:bg-zinc-700 text-white border border-zinc-700'
                }
              `}>
                {plan.priceMonthly === null ? 'Falar com Consultor' : 'Começar Agora'}
              </button>
            </div>
          ))}
        </div>

        {/* FAQ Rápido / Trust */}
        <div className="mt-20 grid md:grid-cols-3 gap-6 p-6 bg-zinc-800/30 rounded-xl border border-zinc-800 text-sm text-zinc-400">
             <div className="flex gap-4">
                <HelpCircle className="shrink-0 text-zinc-500" />
                <div>
                    <h5 className="text-white font-bold mb-1">O que são SKUs?</h5>
                    <p>SKU (Stock Keeping Unit) é cada código de barras único. Ex: "Coca-Cola Lata" e "Coca-Cola 2L" contam como 2 SKUs.</p>
                </div>
             </div>
             <div className="flex gap-4">
                <HelpCircle className="shrink-0 text-zinc-500" />
                <div>
                    <h5 className="text-white font-bold mb-1">Preciso de servidor?</h5>
                    <p>Não. A Gôndola é 100% na nuvem e se conecta ao seu sistema de caixa atual via API segura.</p>
                </div>
             </div>
             <div className="flex gap-4">
                <HelpCircle className="shrink-0 text-zinc-500" />
                <div>
                    <h5 className="text-white font-bold mb-1">Garantia?</h5>
                    <p>Você tem 14 dias de garantia incondicional. Se não gostar, devolvemos seu dinheiro integralmente.</p>
                </div>
             </div>
        </div>

      </div>
    </section>
  );
};

export default PricingSection;