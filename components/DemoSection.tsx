import React, { useState } from 'react';
import { Sparkles, AlertCircle, Package, Calculator, Loader2, Tag } from 'lucide-react';
import { generatePromotionStrategy } from '../services/geminiService';
import { PromotionSuggestion, AnalysisStatus } from '../types';

const DemoSection: React.FC = () => {
  const [productName, setProductName] = useState('Queijo Minas Frescal');
  const [days, setDays] = useState(4);
  const [stock, setStock] = useState(50);
  const [status, setStatus] = useState<AnalysisStatus>(AnalysisStatus.IDLE);
  const [results, setResults] = useState<PromotionSuggestion[]>([]);

  const handleGenerate = async () => {
    setStatus(AnalysisStatus.ANALYZING);
    try {
        const [suggestions] = await Promise.all([
            generatePromotionStrategy(productName, days, stock, 24.90),
            new Promise(resolve => setTimeout(resolve, 1500)) 
        ]);
        setResults(suggestions);
        setStatus(AnalysisStatus.COMPLETE);
    } catch (e) {
        setStatus(AnalysisStatus.ERROR);
    }
  };

  return (
    <section id="demo" className="py-24 bg-zinc-900 relative overflow-hidden border-t border-zinc-800">
      
      <div className="max-w-6xl mx-auto px-6 relative z-10">
        <div className="text-center mb-16">
          <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">Teste na Prática</h2>
          <p className="text-zinc-400 max-w-2xl mx-auto">
            Simule um produto próximo do vencimento e veja a mágica acontecer.
          </p>
        </div>

        <div className="grid lg:grid-cols-12 gap-8">
          {/* Painel de Entrada */}
          <div className="lg:col-span-4 bg-zinc-800 border border-zinc-700 p-8 rounded-2xl h-fit">
            <div className="flex items-center gap-3 mb-8 pb-4 border-b border-zinc-700">
              <div className="bg-brand-900/30 p-2 rounded text-brand-500">
                <Calculator size={20} />
              </div>
              <span className="font-bold text-white text-lg">Dados do Produto</span>
            </div>

            <div className="space-y-6">
              <div>
                <label className="block text-xs font-semibold text-zinc-400 uppercase tracking-wide mb-2">Nome do Produto</label>
                <input 
                  type="text" 
                  value={productName}
                  onChange={(e) => setProductName(e.target.value)}
                  className="w-full bg-zinc-900 border border-zinc-700 text-white px-4 py-3 rounded-lg focus:outline-none focus:border-brand-500 focus:ring-1 focus:ring-brand-500 transition-all font-medium"
                />
              </div>

              <div>
                 <div className="flex justify-between mb-2">
                    <label className="text-xs font-semibold text-zinc-400 uppercase tracking-wide">Dias para Vencer</label>
                    <span className={`font-mono font-bold ${days < 5 ? 'text-red-400' : 'text-brand-400'}`}>
                        {days} dias
                    </span>
                 </div>
                 <input 
                    type="range" 
                    min="1" 
                    max="30" 
                    value={days} 
                    onChange={(e) => setDays(Number(e.target.value))}
                    className="w-full h-2 bg-zinc-900 rounded-lg appearance-none cursor-pointer accent-brand-600"
                 />
              </div>

              <div>
                 <div className="flex justify-between mb-2">
                    <label className="text-xs font-semibold text-zinc-400 uppercase tracking-wide">Estoque Atual</label>
                    <span className="font-mono font-bold text-white">{stock} un.</span>
                 </div>
                 <input 
                    type="range" 
                    min="10" 
                    max="500" 
                    step="10"
                    value={stock} 
                    onChange={(e) => setStock(Number(e.target.value))}
                    className="w-full h-2 bg-zinc-900 rounded-lg appearance-none cursor-pointer accent-brand-600"
                 />
              </div>

              <button 
                onClick={handleGenerate}
                disabled={status === AnalysisStatus.ANALYZING}
                className="w-full mt-4 bg-brand-600 hover:bg-brand-500 disabled:bg-zinc-700 disabled:text-zinc-500 text-white font-bold py-4 rounded-lg flex items-center justify-center gap-2 transition-all shadow-lg shadow-brand-900/20"
              >
                {status === AnalysisStatus.ANALYZING ? (
                    <>
                        <Loader2 className="animate-spin" size={18} />
                        Analisando...
                    </>
                ) : (
                    <>
                        <Sparkles size={18} />
                        Gerar Promoção
                    </>
                )}
              </button>
            </div>
          </div>

          {/* Painel de Resultado */}
          <div className="lg:col-span-8 space-y-6">
             {status === AnalysisStatus.IDLE && (
                 <div className="h-full min-h-[400px] bg-zinc-800/30 flex flex-col items-center justify-center border-2 border-dashed border-zinc-700 rounded-2xl text-zinc-500 text-center p-12">
                    <div className="bg-zinc-800 p-4 rounded-full mb-4">
                        <Package size={32} className="opacity-50" />
                    </div>
                    <h4 className="text-white font-medium mb-2">Aguardando Dados</h4>
                    <p className="text-sm max-w-xs">Preencha as informações ao lado para receber sugestões de venda.</p>
                 </div>
             )}

             {status === AnalysisStatus.ANALYZING && (
                 <div className="h-full min-h-[400px] flex flex-col items-center justify-center bg-zinc-800/30 border border-zinc-700 rounded-2xl p-12">
                    <div className="relative w-16 h-16 mb-6">
                         <div className="absolute inset-0 border-4 border-zinc-700 rounded-full"></div>
                         <div className="absolute inset-0 border-4 border-brand-500 rounded-full border-t-transparent animate-spin"></div>
                    </div>
                    <h3 className="text-white font-bold text-xl mb-2">Processando Estratégias</h3>
                    <p className="text-zinc-500 text-sm">Calculando melhor margem vs. risco de perda...</p>
                 </div>
             )}

            {status === AnalysisStatus.COMPLETE && (
                <div className="grid gap-4">
                    <div className="flex items-center gap-2 text-zinc-400 mb-2">
                        <Tag size={16} />
                        <span className="text-sm font-medium uppercase">Sugestões Encontradas</span>
                    </div>
                    {results.map((item, idx) => (
                        <div key={idx} className="bg-zinc-800 border border-zinc-700 rounded-xl p-6 hover:border-brand-500/50 transition-colors group">
                            <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-3">
                                <h3 className="text-lg font-bold text-white flex items-center gap-2">
                                    {item.title}
                                </h3>
                                <span className="bg-emerald-500/10 text-emerald-400 text-xs font-bold px-3 py-1.5 rounded-full border border-emerald-500/20">
                                    {item.discount}
                                </span>
                            </div>
                            <p className="text-zinc-300 text-sm mb-4 leading-relaxed border-l-2 border-zinc-600 pl-4">
                                {item.strategy}
                            </p>
                            <div className="flex items-start gap-2 text-xs text-zinc-500 bg-zinc-900/50 p-3 rounded-lg">
                                <AlertCircle size={14} className="shrink-0 mt-0.5 text-brand-500" />
                                <span><strong>Por que funciona:</strong> {item.reasoning}</span>
                            </div>
                        </div>
                    ))}
                </div>
            )}
          </div>
        </div>
      </div>
    </section>
  );
};

export default DemoSection;