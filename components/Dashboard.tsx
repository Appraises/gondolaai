import React, { useState } from 'react';
import { 
    LayoutDashboard, 
    Package, 
    Bell, 
    Settings, 
    LogOut, 
    TrendingUp, 
    AlertTriangle, 
    DollarSign,
    Search,
    MoreVertical,
    Sparkles,
    CheckCircle2
} from 'lucide-react';

interface DashboardProps {
    onLogout: () => void;
}

const Dashboard: React.FC<DashboardProps> = ({ onLogout }) => {
    // Dados Mockados para o Dashboard
    const [alerts, setAlerts] = useState([
        { id: 1, name: 'Queijo Mussarela 500g', expiry: '2 dias', stock: 45, status: 'CRITICO' },
        { id: 2, name: 'Iogurte Grego Frutas', expiry: '4 dias', stock: 120, status: 'ALERTA' },
        { id: 3, name: 'Pão de Forma Integral', expiry: '5 dias', stock: 30, status: 'ALERTA' },
        { id: 4, name: 'Requeijão Cremoso', expiry: '6 dias', stock: 18, status: 'NORMAL' },
    ]);

    const [generatingId, setGeneratingId] = useState<number | null>(null);

    const handleAction = (id: number) => {
        setGeneratingId(id);
        // Simula ação da IA
        setTimeout(() => {
            setGeneratingId(null);
            setAlerts(prev => prev.map(item => item.id === id ? { ...item, status: 'RESOLVIDO' } : item));
        }, 1500);
    };

    return (
        <div className="min-h-screen bg-zinc-950 text-zinc-200 font-mono flex">
            
            {/* Sidebar */}
            <aside className="w-64 border-r border-zinc-800 bg-zinc-900/50 hidden md:flex flex-col">
                <div className="p-6 border-b border-zinc-800">
                    <div className="flex items-center gap-2 text-brand-500">
                        <div className="w-8 h-8 bg-brand-500/20 rounded flex items-center justify-center">
                            <span className="font-bold text-lg">G</span>
                        </div>
                        <span className="font-bold tracking-tight text-white">Gôndola OS</span>
                    </div>
                </div>

                <nav className="flex-1 p-4 space-y-2">
                    <div className="text-[10px] text-zinc-500 uppercase font-bold px-3 mb-2">Principal</div>
                    <button className="w-full flex items-center gap-3 px-3 py-2 bg-brand-500/10 text-brand-400 rounded border border-brand-500/20">
                        <LayoutDashboard size={18} />
                        <span className="font-bold text-sm">Visão Geral</span>
                    </button>
                    <button className="w-full flex items-center gap-3 px-3 py-2 text-zinc-400 hover:text-white hover:bg-zinc-800 rounded transition-colors">
                        <Package size={18} />
                        <span className="font-medium text-sm">Estoque</span>
                    </button>
                    <button className="w-full flex items-center gap-3 px-3 py-2 text-zinc-400 hover:text-white hover:bg-zinc-800 rounded transition-colors flex justify-between">
                        <div className="flex items-center gap-3">
                            <Bell size={18} />
                            <span className="font-medium text-sm">Alertas</span>
                        </div>
                        <span className="bg-red-500/20 text-red-400 text-[10px] px-1.5 py-0.5 rounded-full font-bold">3</span>
                    </button>
                    
                    <div className="text-[10px] text-zinc-500 uppercase font-bold px-3 mt-6 mb-2">Sistema</div>
                    <button className="w-full flex items-center gap-3 px-3 py-2 text-zinc-400 hover:text-white hover:bg-zinc-800 rounded transition-colors">
                        <Settings size={18} />
                        <span className="font-medium text-sm">Configurações</span>
                    </button>
                </nav>

                <div className="p-4 border-t border-zinc-800">
                    <div className="flex items-center gap-3 px-3 py-2">
                        <div className="w-8 h-8 rounded-full bg-zinc-800 border border-zinc-700"></div>
                        <div className="flex-1 overflow-hidden">
                            <div className="text-sm font-bold truncate">Loja Centro</div>
                            <div className="text-[10px] text-zinc-500 flex items-center gap-1">
                                <span className="w-1.5 h-1.5 rounded-full bg-emerald-500"></span>
                                Online
                            </div>
                        </div>
                    </div>
                    <button 
                        onClick={onLogout}
                        className="w-full mt-2 flex items-center justify-center gap-2 text-xs text-zinc-500 hover:text-red-400 transition-colors py-2"
                    >
                        <LogOut size={14} />
                        Sair do Sistema
                    </button>
                </div>
            </aside>

            {/* Main Content */}
            <main className="flex-1 flex flex-col h-screen overflow-hidden">
                
                {/* Topbar */}
                <header className="h-16 border-b border-zinc-800 bg-zinc-900/30 flex items-center justify-between px-6 backdrop-blur-sm">
                    <div className="flex items-center gap-4 text-zinc-400">
                        <span className="text-xs uppercase font-bold tracking-widest text-zinc-600">Dashboard // V.2.4.0</span>
                    </div>
                    <div className="flex items-center gap-4">
                        <div className="relative">
                            <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-zinc-600" size={14} />
                            <input 
                                type="text" 
                                placeholder="Buscar SKU..." 
                                className="bg-zinc-900 border border-zinc-800 rounded-full pl-9 pr-4 py-1.5 text-xs text-zinc-300 focus:outline-none focus:border-brand-500 transition-colors w-64 placeholder:text-zinc-700"
                            />
                        </div>
                        <button className="w-8 h-8 rounded border border-zinc-800 flex items-center justify-center hover:bg-zinc-800 text-zinc-400">
                            <Bell size={16} />
                        </button>
                    </div>
                </header>

                <div className="flex-1 overflow-y-auto p-6 space-y-6">
                    
                    {/* KPI Grid */}
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                        <div className="bg-zinc-900 border border-zinc-800 p-5 rounded-lg relative overflow-hidden group">
                            <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity">
                                <DollarSign size={64} />
                            </div>
                            <div className="text-zinc-500 text-xs font-bold uppercase mb-1">Prejuízo Evitado (Mês)</div>
                            <div className="text-3xl font-bold text-white tracking-tight">R$ 12.450<span className="text-zinc-600">,00</span></div>
                            <div className="mt-2 text-xs text-brand-500 flex items-center gap-1">
                                <TrendingUp size={12} />
                                +15% vs mês anterior
                            </div>
                        </div>

                        <div className="bg-zinc-900 border border-zinc-800 p-5 rounded-lg relative overflow-hidden group">
                            <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity">
                                <AlertTriangle size={64} />
                            </div>
                            <div className="text-zinc-500 text-xs font-bold uppercase mb-1">Itens em Risco (Crítico)</div>
                            <div className="text-3xl font-bold text-white tracking-tight">24 <span className="text-base text-zinc-500 font-normal">SKUs</span></div>
                            <div className="mt-2 text-xs text-red-400 flex items-center gap-1">
                                <AlertTriangle size={12} />
                                Ação necessária em 3 itens
                            </div>
                        </div>

                        <div className="bg-zinc-900 border border-zinc-800 p-5 rounded-lg relative overflow-hidden group">
                            <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity">
                                <Package size={64} />
                            </div>
                            <div className="text-zinc-500 text-xs font-bold uppercase mb-1">Promoções Ativas</div>
                            <div className="text-3xl font-bold text-white tracking-tight">8 <span className="text-base text-zinc-500 font-normal">Campanhas</span></div>
                            <div className="mt-2 text-xs text-zinc-400 flex items-center gap-1">
                                4 encerrando hoje
                            </div>
                        </div>
                    </div>

                    {/* Main Content Area */}
                    <div className="grid lg:grid-cols-3 gap-6">
                        
                        {/* Feed de Alertas */}
                        <div className="lg:col-span-2 bg-zinc-900 border border-zinc-800 rounded-lg overflow-hidden">
                            <div className="p-4 border-b border-zinc-800 flex justify-between items-center">
                                <h3 className="font-bold text-sm text-white flex items-center gap-2">
                                    <div className="w-2 h-2 rounded-full bg-red-500 animate-pulse"></div>
                                    Alertas de Validade
                                </h3>
                                <button className="text-xs text-brand-500 hover:underline">Ver todos</button>
                            </div>
                            
                            <div className="divide-y divide-zinc-800">
                                {alerts.map((item) => (
                                    <div key={item.id} className="p-4 flex items-center justify-between hover:bg-zinc-800/50 transition-colors">
                                        <div className="flex items-start gap-4">
                                            <div className={`w-10 h-10 rounded flex items-center justify-center border ${
                                                item.status === 'CRITICO' ? 'bg-red-500/10 border-red-500/30 text-red-500' :
                                                item.status === 'RESOLVIDO' ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-500' :
                                                'bg-yellow-500/10 border-yellow-500/30 text-yellow-500'
                                            }`}>
                                                {item.status === 'RESOLVIDO' ? <CheckCircle2 size={18} /> : <AlertTriangle size={18} />}
                                            </div>
                                            <div>
                                                <div className="font-bold text-sm text-zinc-200">{item.name}</div>
                                                <div className="text-xs text-zinc-500 mt-0.5">
                                                    Vence em: <span className={item.status === 'CRITICO' ? 'text-red-400 font-bold' : 'text-zinc-300'}>{item.expiry}</span> • Estoque: {item.stock} un.
                                                </div>
                                            </div>
                                        </div>

                                        {item.status !== 'RESOLVIDO' ? (
                                            <button 
                                                onClick={() => handleAction(item.id)}
                                                disabled={generatingId === item.id}
                                                className="bg-zinc-800 hover:bg-zinc-700 border border-zinc-700 text-zinc-300 text-xs px-3 py-1.5 rounded flex items-center gap-2 transition-all"
                                            >
                                                {generatingId === item.id ? (
                                                    <span className="animate-pulse">Gerando...</span>
                                                ) : (
                                                    <>
                                                        <Sparkles size={12} className="text-brand-500" />
                                                        Criar Oferta
                                                    </>
                                                )}
                                            </button>
                                        ) : (
                                            <span className="text-xs font-bold text-emerald-500 px-3 py-1.5 bg-emerald-500/10 rounded border border-emerald-500/20">
                                                OFERTA ATIVA
                                            </span>
                                        )}
                                    </div>
                                ))}
                            </div>
                        </div>

                        {/* Side Panel Stats */}
                        <div className="space-y-6">
                            <div className="bg-zinc-900 border border-zinc-800 rounded-lg p-5">
                                <h4 className="text-xs font-bold uppercase text-zinc-500 mb-4">Eficiência da IA</h4>
                                <div className="space-y-4">
                                    <div>
                                        <div className="flex justify-between text-sm mb-1">
                                            <span className="text-zinc-300">Margem Recuperada</span>
                                            <span className="text-brand-500 font-bold">84%</span>
                                        </div>
                                        <div className="h-2 bg-zinc-800 rounded-full overflow-hidden">
                                            <div className="h-full bg-brand-500 w-[84%]"></div>
                                        </div>
                                    </div>
                                    <div>
                                        <div className="flex justify-between text-sm mb-1">
                                            <span className="text-zinc-300">Redução de Quebra</span>
                                            <span className="text-brand-500 font-bold">92%</span>
                                        </div>
                                        <div className="h-2 bg-zinc-800 rounded-full overflow-hidden">
                                            <div className="h-full bg-brand-500 w-[92%]"></div>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            <div className="bg-zinc-900 border border-zinc-800 rounded-lg p-5">
                                <h4 className="text-xs font-bold uppercase text-zinc-500 mb-4">Top Sugestões Hoje</h4>
                                <ul className="space-y-3 text-sm">
                                    <li className="flex items-center gap-3 text-zinc-400">
                                        <div className="w-1.5 h-1.5 bg-brand-500 rounded-full"></div>
                                        Kit Leve 3 Pague 2 (Iogurtes)
                                    </li>
                                    <li className="flex items-center gap-3 text-zinc-400">
                                        <div className="w-1.5 h-1.5 bg-brand-500 rounded-full"></div>
                                        30% OFF Queijos Próx. Venc.
                                    </li>
                                    <li className="flex items-center gap-3 text-zinc-400">
                                        <div className="w-1.5 h-1.5 bg-brand-500 rounded-full"></div>
                                        Bundle Café + Pão
                                    </li>
                                </ul>
                            </div>
                        </div>
                    </div>

                </div>
            </main>
        </div>
    );
};

export default Dashboard;