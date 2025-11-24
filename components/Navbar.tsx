import React, { useState, useEffect } from 'react';
import { ShoppingCart, Menu, X, User } from 'lucide-react';

interface NavbarProps {
  onNavigate: (view: 'home' | 'pricing' | 'login', sectionId?: string) => void;
  currentView: 'home' | 'pricing' | 'login' | 'dashboard';
  onOpenModal: () => void;
}

const Navbar: React.FC<NavbarProps> = ({ onNavigate, currentView, onOpenModal }) => {
  const [scrolled, setScrolled] = useState(false);
  const [menuOpen, setMenuOpen] = useState(false);

  useEffect(() => {
    const handleScroll = () => setScrolled(window.scrollY > 20);
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const handleNavClick = (view: 'home' | 'pricing' | 'login', sectionId?: string) => {
    onNavigate(view, sectionId);
    setMenuOpen(false);
  };

  const handleOpenModal = () => {
    onOpenModal();
    setMenuOpen(false);
  };

  return (
    <nav className={`fixed top-0 w-full z-50 transition-all duration-300 border-b ${scrolled ? 'bg-zinc-900/90 backdrop-blur-lg border-zinc-800 py-3' : 'bg-transparent border-transparent py-5'}`}>
      <div className="max-w-7xl mx-auto px-6 flex items-center justify-between">
        
        {/* Logo - Sempre volta pro topo da Home */}
        <div 
          onClick={() => handleNavClick('home')}
          className="flex items-center gap-3 cursor-pointer group"
        >
          <div className="relative text-brand-500 transition-transform group-hover:scale-105 duration-300">
             <svg 
                width="40" 
                height="40" 
                viewBox="0 0 24 24" 
                fill="none" 
                stroke="currentColor" 
                strokeWidth="1.8" 
                strokeLinecap="round" 
                strokeLinejoin="round"
             >
                <path d="M1 1h4l2.68 13.39a2 2 0 0 0 2 1.61h9.72a2 2 0 0 0 2-1.61L23 6H6" />
                <circle cx="10" cy="20.5" r="1.5" />
                <circle cx="19" cy="20.5" r="1.5" />
                <path d="M7.5 10h3l2-3h2" className="opacity-90" />
                <circle cx="15" cy="7" r="1" fill="currentColor" className="stroke-none" />
                <path d="M10.5 10l2 3h2" className="opacity-90" />
                <circle cx="15" cy="13" r="1" fill="currentColor" className="stroke-none" />
             </svg>
             <div className="absolute inset-0 bg-brand-500/20 blur-xl rounded-full opacity-0 group-hover:opacity-100 transition-opacity"></div>
          </div>

          <span className="font-bold text-xl tracking-tight text-white font-mono">
            Gôndola<span className="text-brand-500">.ai</span>
          </span>
        </div>

        <div className="hidden md:flex items-center gap-8 text-sm font-medium text-zinc-400 font-mono">
          <button 
            onClick={() => handleNavClick('home', 'features')} 
            className="hover:text-brand-400 transition-colors uppercase"
          >
            Recursos
          </button>
          
          <button 
            onClick={() => handleNavClick('home', 'demo')} 
            className="hover:text-brand-400 transition-colors uppercase"
          >
            Simulador
          </button>
          
          <button 
            onClick={() => handleNavClick('pricing')} 
            className={`transition-colors uppercase ${currentView === 'pricing' ? 'text-brand-500 font-bold' : 'hover:text-brand-400'}`}
          >
            Planos
          </button>

          {/* Botão Login */}
          <button 
            onClick={() => handleNavClick('login')} 
            className={`transition-colors uppercase flex items-center gap-2 ${currentView === 'login' ? 'text-brand-500 font-bold' : 'hover:text-brand-400'}`}
          >
            <User size={16} />
            Entrar
          </button>
          
          <button 
            onClick={handleOpenModal}
            className="bg-white hover:bg-brand-50 text-zinc-950 font-bold px-5 py-2 rounded-sm transition-all flex items-center gap-2 text-xs uppercase tracking-wide border border-transparent hover:border-brand-200"
          >
            <ShoppingCart size={16} className="text-brand-600" />
            Agendar Demo
          </button>
        </div>

        <button className="md:hidden text-zinc-300" onClick={() => setMenuOpen(!menuOpen)}>
          {menuOpen ? <X /> : <Menu />}
        </button>
      </div>

      {menuOpen && (
        <div className="md:hidden absolute top-full left-0 w-full bg-zinc-900 border-b border-zinc-800 p-6 flex flex-col gap-4 font-medium font-mono">
          <button onClick={() => handleNavClick('home', 'features')} className="text-left text-zinc-300 hover:text-brand-400">RECURSOS</button>
          <button onClick={() => handleNavClick('home', 'demo')} className="text-left text-zinc-300 hover:text-brand-400">SIMULADOR</button>
          <button onClick={() => handleNavClick('pricing')} className={`text-left hover:text-brand-400 ${currentView === 'pricing' ? 'text-brand-500' : 'text-zinc-300'}`}>PLANOS</button>
          <button onClick={() => handleNavClick('login')} className={`text-left hover:text-brand-400 ${currentView === 'login' ? 'text-brand-500' : 'text-zinc-300'}`}>ENTRAR</button>
          <button 
            onClick={handleOpenModal}
            className="bg-brand-600 text-white font-bold px-5 py-3 rounded-sm w-full text-center uppercase tracking-wide"
          >
            Agendar Demo
          </button>
        </div>
      )}
    </nav>
  );
};

export default Navbar;