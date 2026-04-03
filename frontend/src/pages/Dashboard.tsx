import React, { useEffect, useState } from 'react';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

const dummyData = [
  { name: 'Seg', uv: 4000, pv: 2400 },
  { name: 'Ter', uv: 3000, pv: 1398 },
  { name: 'Qua', uv: 2000, pv: 9800 },
  { name: 'Qui', uv: 2780, pv: 3908 },
  { name: 'Sex', uv: 1890, pv: 4800 },
  { name: 'Sab', uv: 2390, pv: 3800 },
  { name: 'Dom', uv: 3490, pv: 4300 },
];

const Dashboard: React.FC = () => {
  const [summary, setSummary] = useState<any>(null);

  useEffect(() => {
    // Busca do Backend FastAPI
    fetch('http://localhost:8000/api/alerts/summary?store_id=1')
      .then(res => res.json())
      .then(data => setSummary(data))
      .catch(err => console.error("API error", err));
  }, []);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
      <div>
        <h1 style={{ fontSize: '1.75rem', marginBottom: '0.5rem' }}>Visão Geral</h1>
        <p style={{ color: 'var(--text-muted)' }}>Métricas inteligentes e predições para a sua loja.</p>
      </div>

      <div className="grid-cards">
        <div className="glass-panel stat-card">
          <h3>Faturamento (7 dias)</h3>
          <div className="value" style={{ color: 'var(--success)' }}>R$ 14.520,00</div>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.875rem', marginTop: '0.5rem' }}>+12% vs semana anterior</p>
        </div>
        <div className="glass-panel stat-card">
          <h3>Alertas Ativos de Estoque</h3>
          <div className="value" style={{ color: 'var(--danger)' }}>
            {summary ? summary.total : '...'}
          </div>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.875rem', marginTop: '0.5rem' }}>
            Rupturas e encalhes gerados via ML
          </p>
        </div>
        <div className="glass-panel stat-card">
          <h3>Status do Motor IA</h3>
          <div className="value" style={{ color: 'var(--primary)' }}>Online</div>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.875rem', marginTop: '0.5rem' }}>Modelos XGBoost e Prophet operantes</p>
        </div>
      </div>

      <div className="glass-panel p-6">
        <h3 style={{ marginBottom: '1.5rem', fontWeight: 600 }}>Projeção de Demanda vs Realidade</h3>
        <div style={{ width: '100%', height: 350 }}>
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={dummyData} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
              <defs>
                <linearGradient id="colorUv" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="var(--primary)" stopOpacity={0.8}/>
                  <stop offset="95%" stopColor="var(--primary)" stopOpacity={0}/>
                </linearGradient>
                <linearGradient id="colorPv" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="var(--secondary)" stopOpacity={0.8}/>
                  <stop offset="95%" stopColor="var(--secondary)" stopOpacity={0}/>
                </linearGradient>
              </defs>
              <XAxis dataKey="name" stroke="var(--text-muted)" />
              <YAxis stroke="var(--text-muted)" />
              <CartesianGrid strokeDasharray="3 3" stroke="var(--panel-border)" />
              <Tooltip 
                contentStyle={{ background: 'var(--panel-bg)', borderColor: 'var(--panel-border)', borderRadius: '8px', color: 'var(--text-main)' }} 
                itemStyle={{ color: 'var(--text-main)' }}
              />
              <Area type="monotone" dataKey="uv" stroke="var(--primary)" fillOpacity={1} fill="url(#colorUv)" name="Venda Real" />
              <Area type="monotone" dataKey="pv" stroke="var(--secondary)" fillOpacity={1} fill="url(#colorPv)" name="Previsão ML" />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
