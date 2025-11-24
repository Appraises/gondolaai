import React from 'react';
import { Clock, TrendingUp, ShieldCheck, BarChart3, Database, Tag } from 'lucide-react';

const features = [
  {
    icon: <Clock className="w-6 h-6 text-brand-500" />,
    title: "Alerta de Validade",
    description: "Evite o prejuízo. O sistema avisa quais produtos estão para vencer na semana e sugere ações imediatas."
  },
  {
    icon: <Tag className="w-6 h-6 text-brand-500" />,
    title: "Etiqueta Inteligente",
    description: "Sugestão de preço ideal para 'queimar' o estoque próximo ao vencimento sem perder toda a margem."
  },
  {
    icon: <Database className="w-6 h-6 text-brand-500" />,
    title: "Conexão com ERP",
    description: "Não precisa cadastrar nada. A Gôndola lê o seu sistema atual e começa a trabalhar em 24 horas."
  },
  {
    icon: <BarChart3 className="w-6 h-6 text-brand-500" />,
    title: "Painel de Ganhos",
    description: "Veja exatamente quantos Reais você recuperou no mês evitando o descarte de mercadorias."
  },
  {
    icon: <ShieldCheck className="w-6 h-6 text-brand-500" />,
    title: "Prevenção de Perdas",
    description: "Cruzamento de dados de estoque físico e fiscal para identificar furos e furtos administrativos."
  },
  {
    icon: <TrendingUp className="w-6 h-6 text-brand-500" />,
    title: "Giro de Estoque",
    description: "Acelere a saída de produtos parados com estratégias de combos geradas por Inteligência Artificial."
  }
];

const Features: React.FC = () => {
  return (
    <section id="features" className="py-24 bg-zinc-900 border-t border-zinc-800">
      <div className="max-w-7xl mx-auto px-6">
        <div className="mb-16 max-w-2xl">
          <h2 className="text-sm font-bold text-brand-500 mb-4 tracking-wider uppercase">Por que usar Gôndola?</h2>
          <h3 className="text-3xl md:text-4xl font-bold text-white mb-6">
            Mais lucro, menos desperdício.
          </h3>
          <p className="text-zinc-400 text-lg">
            Pequenos e médios supermercados perdem até 4% da receita jogando comida fora. Nossa missão é zerar esse número no seu negócio.
          </p>
        </div>

        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
          {features.map((feature, index) => (
            <div key={index} className="group p-8 rounded-xl bg-zinc-800/50 border border-zinc-700/50 hover:border-brand-500/30 hover:bg-zinc-800 transition-all duration-300 shadow-sm hover:shadow-lg hover:shadow-brand-900/10">
              <div className="w-12 h-12 bg-zinc-900 rounded-lg border border-zinc-700 flex items-center justify-center mb-6 group-hover:scale-105 transition-transform group-hover:border-brand-500/30">
                {feature.icon}
              </div>
              <h4 className="text-xl font-bold text-white mb-3">{feature.title}</h4>
              <p className="text-zinc-400 leading-relaxed text-sm">
                {feature.description}
              </p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default Features;