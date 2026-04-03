import React, { ReactNode } from 'react';
import { NavLink, Outlet } from 'react-router-dom';
import { LayoutDashboard, Bell, Tag, Settings, BrainCircuit } from 'lucide-react';

interface LayoutProps {
  children?: ReactNode;
}

const Layout: React.FC<LayoutProps> = () => {
  return (
    <div className="layout-container">
      {/* Sidebar */}
      <aside className="sidebar glass-panel" style={{ borderRadius: 0, borderTop: 0, borderBottom: 0, borderLeft: 0 }}>
        <div style={{ padding: '2rem', borderBottom: '1px solid var(--panel-border)' }}>
          <h2 style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--primary)', margin: 0 }}>
            <BrainCircuit size={28} />
            Gôndola.ai
          </h2>
          <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginTop: '0.5rem' }}>
            Smart Varejo MVP
          </p>
        </div>

        <nav style={{ padding: '1rem', display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
          <NavLink
            to="/"
            className={({ isActive }) =>
              `btn ${isActive ? 'btn-primary' : 'btn-outline'}`
            }
            style={{ justifyContent: 'flex-start', border: 'none' }}
          >
            <LayoutDashboard size={18} /> Dashboard
          </NavLink>
          <NavLink
            to="/alerts"
            className={({ isActive }) =>
              `btn ${isActive ? 'btn-primary' : 'btn-outline'}`
            }
            style={{ justifyContent: 'flex-start', border: 'none' }}
          >
            <Bell size={18} /> Alertas de Estoque
          </NavLink>
          <NavLink
            to="/pricing"
            className={({ isActive }) =>
              `btn ${isActive ? 'btn-primary' : 'btn-outline'}`
            }
            style={{ justifyContent: 'flex-start', border: 'none' }}
          >
            <Tag size={18} /> Pricing Preditivo
          </NavLink>
          <div style={{ flex: 1 }} />
          <NavLink
            to="/settings"
            className={({ isActive }) =>
              `btn ${isActive ? 'btn-primary' : 'btn-outline'}`
            }
            style={{ justifyContent: 'flex-start', border: 'none', marginTop: '2rem' }}
          >
            <Settings size={18} /> Configurações
          </NavLink>
        </nav>
      </aside>

      {/* Main Container */}
      <main className="main-content">
        <header className="glass-header flex items-center justify-between" style={{ padding: '1.25rem 2rem' }}>
          <div>
             <h3 style={{ margin: 0, fontSize: '1.1rem' }}>Supermercado Demo (Loja #1)</h3>
          </div>
          <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
            <span className="badge badge-success">API Conectada</span>
            <div style={{ width: '40px', height: '40px', borderRadius: '50%', background: 'var(--primary)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 'bold' }}>
              BL
            </div>
          </div>
        </header>

        <section className="page-container" style={{ overflowY: 'auto', flex: 1 }}>
          <Outlet />
        </section>
      </main>
    </div>
  );
};

export default Layout;
