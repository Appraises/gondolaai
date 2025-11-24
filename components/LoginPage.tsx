import React, { useState } from 'react';
import { Lock, ArrowRight, Loader2, Mail } from 'lucide-react';

interface LoginPageProps {
  onLoginSuccess: () => void;
}

const LoginPage: React.FC<LoginPageProps> = ({ onLoginSuccess }) => {
  const [loading, setLoading] = useState(false);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  const handleLogin = (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    
    // Simula delay de rede
    setTimeout(() => {
      setLoading(false);
      onLoginSuccess();
    }, 1500);
  };

  return (
    // Adicionado font-inter para quebrar o visual 'código/mono' do resto do site apenas aqui
    <div className="min-h-screen bg-zinc-950 flex items-center justify-center p-6 relative overflow-hidden font-inter">
      
      {/* Background Grid Animation (Mantido como solicitado) */}
      <div className="absolute inset-0 bg-[linear-gradient(to_right,#80808012_1px,transparent_1px),linear-gradient(to_bottom,#80808012_1px,transparent_1px)] bg-[size:32px_32px]"></div>
      
      {/* Container Principal */}
      <div className="w-full max-w-md relative z-30">
        
        {/* Logo */}
        <div className="text-center mb-8">
           <div className="flex items-center justify-center gap-2 mb-2">
             <div className="w-8 h-8 bg-brand-600 rounded-lg flex items-center justify-center text-white font-bold text-lg font-mono">G</div>
             <span className="text-2xl font-bold text-white tracking-tight font-mono">Gôndola.ai</span>
           </div>
           <p className="text-zinc-500 text-sm">Gestão inteligente para seu supermercado</p>
        </div>

        {/* Wrapper do Card para Posicionamento do Brilho */}
        <div className="relative">
            
            {/* O BRILHO VERDE (Replicado do Hero/Nota Fiscal) */}
            {/* Ajustado: scale-105 para aparecer atrás do card, -z-10 para ficar atrás */}
            <div className="absolute inset-0 bg-gradient-to-tr from-brand-500/20 to-transparent blur-2xl transform rotate-3 scale-105 -z-10 rounded-xl"></div>

            {/* Card de Login - Visual Clean/SaaS */}
            <div className="bg-zinc-900 border border-zinc-800 shadow-xl rounded-xl overflow-hidden">
                <div className="p-8">
                    <div className="mb-6">
                      <h2 className="text-xl font-semibold text-white">Acesse sua conta</h2>
                      <p className="text-sm text-zinc-500 mt-1">Insira suas credenciais para continuar.</p>
                    </div>

                    <form onSubmit={handleLogin} className="space-y-5">
                        <div className="space-y-2">
                            <label className="text-sm font-medium text-zinc-300">Email Corporativo</label>
                            <div className="relative">
                                <Mail className="absolute left-3 top-1/2 -translate-y-1/2 text-zinc-500" size={18} />
                                <input 
                                    type="email" 
                                    value={email}
                                    onChange={(e) => setEmail(e.target.value)}
                                    className="w-full bg-zinc-950 border border-zinc-700 text-white pl-10 pr-4 py-2.5 rounded-lg focus:outline-none focus:border-brand-500 focus:ring-1 focus:ring-brand-500 transition-all placeholder:text-zinc-700"
                                    placeholder="nome@empresa.com.br"
                                    required
                                />
                            </div>
                        </div>

                        <div className="space-y-2">
                             <div className="flex justify-between items-center">
                                <label className="text-sm font-medium text-zinc-300">Senha</label>
                                <a href="#" className="text-xs text-brand-500 hover:text-brand-400 font-medium">Esqueceu?</a>
                             </div>
                            <div className="relative">
                                <Lock className="absolute left-3 top-1/2 -translate-y-1/2 text-zinc-500" size={18} />
                                <input 
                                    type="password"
                                    value={password}
                                    onChange={(e) => setPassword(e.target.value)}
                                    className="w-full bg-zinc-950 border border-zinc-700 text-white pl-10 pr-4 py-2.5 rounded-lg focus:outline-none focus:border-brand-500 focus:ring-1 focus:ring-brand-500 transition-all placeholder:text-zinc-700"
                                    placeholder="••••••••"
                                    required
                                />
                            </div>
                        </div>

                        <button 
                            type="submit" 
                            disabled={loading}
                            className="w-full bg-brand-600 hover:bg-brand-500 text-white font-semibold py-2.5 rounded-lg flex items-center justify-center gap-2 transition-all shadow-lg shadow-brand-900/20 hover:shadow-brand-900/40 disabled:opacity-70 disabled:cursor-not-allowed mt-2"
                        >
                            {loading ? (
                                <>
                                    <Loader2 className="animate-spin" size={18} />
                                    Entrando...
                                </>
                            ) : (
                                <>
                                    Entrar na Plataforma
                                    <ArrowRight size={18} />
                                </>
                            )}
                        </button>
                    </form>
                </div>
                
                <div className="bg-zinc-950/50 border-t border-zinc-800/50 p-4 text-center">
                    <p className="text-sm text-zinc-500">
                        Não tem uma conta? <a href="#" className="text-brand-500 hover:text-brand-400 font-medium">Fale com vendas</a>
                    </p>
                </div>
            </div>
        </div>

        <div className="mt-8 flex justify-center gap-6 text-xs text-zinc-600">
            <a href="#" className="hover:text-zinc-400 transition-colors">Termos de Uso</a>
            <a href="#" className="hover:text-zinc-400 transition-colors">Política de Privacidade</a>
            <a href="#" className="hover:text-zinc-400 transition-colors">Suporte</a>
        </div>
      </div>
    </div>
  );
};

export default LoginPage;