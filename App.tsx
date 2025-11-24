import React, { useState } from 'react';
import Navbar from './components/Navbar';
import Hero from './components/Hero';
import Features from './components/Features';
import DemoSection from './components/DemoSection';
import PricingSection from './components/PricingSection';
import Footer from './components/Footer';
import ContactModal from './components/ContactModal';
import LoginPage from './components/LoginPage';
import Dashboard from './components/Dashboard';

type ViewState = 'home' | 'pricing' | 'login' | 'dashboard';

const App: React.FC = () => {
  const [currentView, setCurrentView] = useState<ViewState>('home');
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isLoggedIn, setIsLoggedIn] = useState(false);

  const handleNavigate = (view: ViewState, sectionId?: string) => {
    // Se tentar ir para dashboard sem logar, vai pro login
    if (view === 'dashboard' && !isLoggedIn) {
      setCurrentView('login');
      return;
    }

    setCurrentView(view);
    
    if (view === 'home' && sectionId) {
      setTimeout(() => {
        const element = document.getElementById(sectionId);
        if (element) {
          element.scrollIntoView({ behavior: 'smooth' });
        }
      }, 100);
    } else {
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }
  };

  const handleLoginSuccess = () => {
    setIsLoggedIn(true);
    setCurrentView('dashboard');
  };

  // Renderização condicional de visualização
  const renderContent = () => {
    switch (currentView) {
      case 'dashboard':
        return <Dashboard onLogout={() => { setIsLoggedIn(false); setCurrentView('home'); }} />;
      case 'login':
        return <LoginPage onLoginSuccess={handleLoginSuccess} />;
      case 'pricing':
        return (
          <div className="animate-in fade-in duration-500 pt-10">
            <PricingSection />
          </div>
        );
      case 'home':
      default:
        return (
          <>
            <Hero onNavigate={handleNavigate} />
            <Features />
            <DemoSection />
            <section className="py-24 border-t border-zinc-800 relative overflow-hidden bg-zinc-900">
              <div className="absolute inset-0 bg-brand-900/5"></div>
              <div className="max-w-4xl mx-auto px-6 text-center relative z-10">
                <h2 className="text-4xl md:text-5xl font-bold text-white mb-6 tracking-tight">
                  Pare de perder dinheiro na prateleira.
                </h2>
                <p className="text-zinc-400 text-xl mb-10">
                  Junte-se a mais de 500 supermercados que automatizaram a gestão de validade com a Gôndola.ai.
                </p>
                <div className="flex flex-col sm:flex-row justify-center gap-4">
                  <button 
                    onClick={() => setIsModalOpen(true)}
                    className="bg-brand-600 hover:bg-brand-500 text-black font-bold text-lg px-8 py-4 rounded-sm transition-all shadow-[0_0_20px_rgba(34,197,94,0.3)] hover:shadow-[0_0_30px_rgba(34,197,94,0.5)]"
                  >
                    Agendar Demonstração
                  </button>
                  <button className="bg-zinc-950 border border-zinc-800 text-zinc-300 hover:text-white hover:border-zinc-600 font-bold px-8 py-4 rounded-sm transition-all">
                    Fale com Vendas
                  </button>
                </div>
              </div>
            </section>
          </>
        );
    }
  };

  return (
    <div className="min-h-screen bg-zinc-900 text-zinc-100 selection:bg-brand-500/30 selection:text-brand-200 font-mono">
      {/* Navbar aparece em todas as telas EXCETO Dashboard, que tem nav própria */}
      {currentView !== 'dashboard' && (
        <Navbar 
          onNavigate={handleNavigate} 
          currentView={currentView}
          onOpenModal={() => setIsModalOpen(true)}
        />
      )}
      
      <main>
        {renderContent()}
      </main>
      
      <ContactModal isOpen={isModalOpen} onClose={() => setIsModalOpen(false)} />
      
      {/* Footer aparece em todas as telas EXCETO Dashboard */}
      {currentView !== 'dashboard' && <Footer />}
    </div>
  );
};

export default App;