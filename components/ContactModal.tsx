import React, { useState } from 'react';
import { X, Check, Terminal, Loader2 } from 'lucide-react';

interface ContactModalProps {
  isOpen: boolean;
  onClose: () => void;
}

const ContactModal: React.FC<ContactModalProps> = ({ isOpen, onClose }) => {
  const [step, setStep] = useState<'FORM' | 'SUCCESS'>('FORM');
  const [loading, setLoading] = useState(false);

  if (!isOpen) return null;

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    // Simula envio para API
    setTimeout(() => {
      setLoading(false);
      setStep('SUCCESS');
    }, 1500);
  };

  const handleClose = () => {
    onClose();
    // Reseta estado após fechar (com pequeno delay para animação)
    setTimeout(() => {
      setStep('FORM');
    }, 300);
  };

  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center p-4">
      {/* Backdrop com Blur */}
      <div 
        className="absolute inset-0 bg-black/60 backdrop-blur-sm transition-opacity"
        onClick={handleClose}
      ></div>

      {/* Modal Content */}
      <div className="relative bg-zinc-900 border border-zinc-700 w-full max-w-lg shadow-2xl shadow-brand-900/20 rounded-lg overflow-hidden animate-in fade-in zoom-in-95 duration-200">
        
        {/* Header tipo Janela de OS */}
        <div className="bg-zinc-800 border-b border-zinc-700 p-3 flex items-center justify-between select-none">
          <div className="flex items-center gap-2 text-zinc-400 text-xs font-mono">
            <Terminal size={14} />
            <span className="uppercase tracking-wider">AGENDAMENTO_DEMO.exe</span>
          </div>
          <button 
            onClick={handleClose}
            className="text-zinc-500 hover:text-white transition-colors"
          >
            <X size={18} />
          </button>
        </div>

        <div className="p-8">
          {step === 'FORM' ? (
            <div className="space-y-6">
              <div>
                <h3 className="text-2xl font-bold text-white mb-2">Vamos automatizar seu estoque.</h3>
                <p className="text-zinc-400 text-sm">
                  Preencha seus dados. Um especialista em varejo entrará em contato em até 15 minutos.
                </p>
              </div>

              <form onSubmit={handleSubmit} className="space-y-4 font-mono text-sm">
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-1">
                    <label className="text-xs text-brand-500 font-bold uppercase">Nome</label>
                    <input 
                      required
                      type="text" 
                      placeholder="Seu nome"
                      className="w-full bg-zinc-950 border border-zinc-800 focus:border-brand-500 text-white px-3 py-2.5 rounded-sm focus:outline-none transition-colors placeholder:text-zinc-700"
                    />
                  </div>
                  <div className="space-y-1">
                    <label className="text-xs text-brand-500 font-bold uppercase">Cargo</label>
                    <input 
                      type="text" 
                      placeholder="Ex: Gerente"
                      className="w-full bg-zinc-950 border border-zinc-800 focus:border-brand-500 text-white px-3 py-2.5 rounded-sm focus:outline-none transition-colors placeholder:text-zinc-700"
                    />
                  </div>
                </div>

                <div className="space-y-1">
                  <label className="text-xs text-brand-500 font-bold uppercase">Email Corporativo</label>
                  <input 
                    required
                    type="email" 
                    placeholder="voce@seu-mercado.com.br"
                    className="w-full bg-zinc-950 border border-zinc-800 focus:border-brand-500 text-white px-3 py-2.5 rounded-sm focus:outline-none transition-colors placeholder:text-zinc-700"
                  />
                </div>

                <div className="space-y-1">
                  <label className="text-xs text-brand-500 font-bold uppercase">Nome do Supermercado</label>
                  <input 
                    required
                    type="text" 
                    placeholder="Mercado..."
                    className="w-full bg-zinc-950 border border-zinc-800 focus:border-brand-500 text-white px-3 py-2.5 rounded-sm focus:outline-none transition-colors placeholder:text-zinc-700"
                  />
                </div>

                <button 
                  type="submit"
                  disabled={loading}
                  className="w-full bg-brand-600 hover:bg-brand-500 disabled:bg-zinc-700 disabled:cursor-not-allowed text-black font-bold py-3 mt-4 flex items-center justify-center gap-2 transition-all uppercase tracking-wide"
                >
                  {loading ? (
                    <>
                      <Loader2 size={16} className="animate-spin" />
                      Processando...
                    </>
                  ) : (
                    <>
                      Solicitar Acesso
                      <span className="text-brand-900">&gt;&gt;</span>
                    </>
                  )}
                </button>
              </form>
              
              <div className="text-[10px] text-zinc-600 text-center">
                * Seus dados estão seguros e criptografados.
              </div>
            </div>
          ) : (
            <div className="py-8 flex flex-col items-center text-center animate-in zoom-in-95 duration-300">
              <div className="w-16 h-16 bg-brand-500/10 rounded-full flex items-center justify-center mb-6 border border-brand-500/20">
                <Check className="w-8 h-8 text-brand-500" />
              </div>
              <h3 className="text-2xl font-bold text-white mb-2">Solicitação Recebida!</h3>
              <p className="text-zinc-400 text-sm max-w-xs mx-auto mb-8">
                Nossa equipe comercial já recebeu seu alerta. Fique atento ao seu email e telefone.
              </p>
              <button 
                onClick={handleClose}
                className="text-zinc-500 hover:text-white text-sm font-mono underline decoration-zinc-700 underline-offset-4"
              >
                [FECHAR_JANELA]
              </button>
            </div>
          )}
        </div>
        
        {/* Footer do Modal */}
        <div className="bg-zinc-950 p-2 border-t border-zinc-800 flex justify-between items-center text-[10px] font-mono text-zinc-600 px-4">
          <span>STATUS: ONLINE</span>
          <span>V.2.4.0</span>
        </div>
      </div>
    </div>
  );
};

export default ContactModal;