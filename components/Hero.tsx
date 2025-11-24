import React from 'react';
import AsciiCart from './AsciiCart';
import { ArrowRight, ScanLine, Percent } from 'lucide-react';

interface HeroProps {
  onNavigate: (view: 'home' | 'pricing', sectionId?: string) => void;
}

const Hero: React.FC<HeroProps> = ({ onNavigate }) => {
  return (
    <section className="relative min-h-screen flex items-center pt-24 pb-12 overflow-hidden bg-zinc-900">
      {/* Background sutil de grade de supermercado */}
      <div className="absolute inset-0 opacity-[0.03] bg-[linear-gradient(to_right,#80808012_1px,transparent_1px),linear-gradient(to_bottom,#80808012_1px,transparent_1px)] bg-[size:24px_24px]"></div>
      
      {/* Glow esmeralda central */}
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[800px] bg-brand-900/20 rounded-full blur-[120px] pointer-events-none"></div>

      <div className="max-w-7xl mx-auto px-6 w-full grid lg:grid-cols-2 gap-16 items-center relative z-10">
        
        <div className="space-y-8 order-2 lg:order-1">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-brand-950/40 border border-brand-900/50 text-brand-400 font-medium text-sm">
            <div className="w-2 h-2 bg-brand-500 rounded-full animate-pulse"></div>
            Controle de validade ativo
          </div>

          <h1 className="text-4xl md:text-6xl font-bold tracking-tight text-white leading-[1.1]">
            Seu estoque não precisa <br />
            <span className="text-brand-500">virar prejuízo.</span>
          </h1>

          <p className="text-lg text-zinc-400 max-w-xl leading-relaxed">
            A <strong>Gôndola.ai</strong> transforma a gestão do seu supermercado. Nossa IA monitora a validade e cria promoções automáticas no PDV antes que o produto vença.
          </p>

          <div className="flex flex-wrap gap-4">
            <button 
              onClick={() => onNavigate('home', 'demo')}
              className="bg-brand-600 hover:bg-brand-500 text-white font-semibold text-lg px-8 py-3.5 rounded-lg transition-all flex items-center gap-2 shadow-lg shadow-brand-900/20"
            >
              Ver Demonstração
              <ArrowRight size={20} />
            </button>
            <button 
              onClick={() => onNavigate('home', 'features')}
              className="bg-zinc-800 border border-zinc-700 hover:border-zinc-600 text-zinc-300 font-medium text-lg px-8 py-3.5 rounded-lg transition-all"
            >
              Como Funciona
            </button>
          </div>

          <div className="grid grid-cols-3 gap-6 pt-8 border-t border-zinc-800/50">
            <div>
              <div className="text-2xl font-bold text-white mb-1">-30%</div>
              <div className="text-xs text-zinc-500 uppercase tracking-wide font-semibold">Quebras</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-white mb-1">+15%</div>
              <div className="text-xs text-zinc-500 uppercase tracking-wide font-semibold">Margem</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-white mb-1">Auto</div>
              <div className="text-xs text-zinc-500 uppercase tracking-wide font-semibold">Precificação</div>
            </div>
          </div>
        </div>

        {/* Lado Direito: A Nota Fiscal Visual */}
        <div className="flex items-center justify-center lg:justify-end relative order-1 lg:order-2 perspective-1000">
          
          {/* Efeito de brilho atrás da nota */}
          <div className="absolute inset-0 bg-gradient-to-tr from-brand-500/10 to-transparent blur-2xl transform rotate-6 scale-90"></div>

          {/* O Cupom Fiscal */}
          <div className="relative w-full max-w-sm bg-white text-zinc-800 shadow-receipt transform rotate-[-2deg] transition-transform hover:rotate-0 duration-500 group">
            
            {/* SCANNER LASER */}
            <div className="absolute left-0 right-0 h-[2px] bg-red-500 shadow-[0_0_15px_2px_rgba(239,68,68,0.6)] z-30 animate-scan pointer-events-none"></div>
            
            {/* Serrilhado Topo */}
            <div className="absolute -top-3 left-0 right-0 h-3 bg-[radial-gradient(circle,transparent,transparent_50%,#ffffff_50%,#ffffff_100%)] bg-[length:16px_16px] rotate-180"></div>

            <div className="p-8 space-y-6 font-mono text-sm">
              {/* Cabeçalho da Nota */}
              <div className="text-center border-b-2 border-dashed border-zinc-200 pb-6">
                <ScanLine className="w-8 h-8 mx-auto text-zinc-800 mb-2" />
                <h3 className="text-xl font-bold tracking-wider uppercase">ESTOQUE INTELIGENTE</h3>
                <p className="text-xs text-zinc-500 mt-1">ID: #882-PROMO-AUTO</p>
              </div>

              {/* O Carrinho ASCII no papel */}
              <div className="py-4 opacity-90 flex justify-center text-brand-900">
                <AsciiCart />
              </div>

              {/* Detalhes da Análise */}
              <div className="border-t-2 border-b-2 border-dashed border-zinc-200 py-4 space-y-2">
                <div className="flex justify-between items-center">
                  <span className="text-zinc-500">ITEM:</span>
                  <span className="font-bold">IOGURTE NAT.</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-zinc-500">VALIDADE:</span>
                  <span className="text-red-600 font-bold bg-red-50 px-1 rounded">EM 3 DIAS</span>
                </div>
                <div className="flex justify-between items-center mt-2">
                  <span className="text-zinc-500">AÇÃO IA:</span>
                  <span className="text-brand-600 font-bold flex items-center gap-1">
                    <Percent size={12} /> OFERTA 30% OFF
                  </span>
                </div>
              </div>

              {/* Rodapé da Nota */}
              <div className="text-center pt-2">
                <p className="text-xs text-zinc-400 uppercase mb-1">*** ECONOMIA GERADA ***</p>
                <p className="text-3xl font-bold text-zinc-900 tracking-tighter">R$ 1.240,50</p>
                <p className="text-[10px] text-zinc-400 mt-4">Gôndola Systems © 2024</p>
              </div>
            </div>

            {/* Serrilhado Fundo */}
            <div className="absolute -bottom-3 left-0 right-0 h-3 bg-[radial-gradient(circle,transparent,transparent_50%,#ffffff_50%,#ffffff_100%)] bg-[length:16px_16px]"></div>
          </div>
        </div>

      </div>
    </section>
  );
};

export default Hero;