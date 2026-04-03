import React, { useEffect, useState } from 'react';

const Pricing: React.FC = () => {
  const [suggestions, setSuggestions] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch('http://localhost:8000/api/pricing/suggestions?store_id=1')
      .then(res => res.json())
      .then(data => {
        setSuggestions(data);
        setLoading(false);
      })
      .catch(err => {
        console.error("API error", err);
        setLoading(false);
      });
  }, []);

  const triggerPricingPipeline = async () => {
    setLoading(true);
    await fetch('http://localhost:8000/api/pricing/generate?store_id=1', { method: 'POST' });
    const res = await fetch('http://localhost:8000/api/pricing/suggestions?store_id=1');
    const data = await res.json();
    setSuggestions(data);
    setLoading(false);
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
      <div className="flex items-center justify-between" style={{ width: '100%' }}>
        <div>
          <h1 style={{ fontSize: '1.75rem', marginBottom: '0.5rem' }}>Pricing & Markdowns</h1>
          <p style={{ color: 'var(--text-muted)' }}>Recomendações da inteligência artificial atuariais de elasticidade.</p>
        </div>
        <button className="btn btn-primary" onClick={triggerPricingPipeline} disabled={loading}>
          {loading ? 'Calculando...' : '⚙️ Recalcular Elasticidade'}
        </button>
      </div>

      <div className="grid-cards">
        {suggestions.length === 0 && !loading && (
          <div className="glass-panel p-6" style={{ gridColumn: '1 / -1', textAlign: 'center', opacity: 0.6 }}>
            <p>Nenhuma sugestão gerada. Clique em Recalcular para acionar o motor ML.</p>
          </div>
        )}

        {suggestions.map((sug) => (
          <div key={sug.id} className="glass-panel p-4" style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            <div className="flex justify-between items-center">
              <span style={{ fontSize: '0.875rem', color: 'var(--text-muted)' }}>EAN: {sug.product_ean}</span>
              {sug.suggested_action === 'MARKDOWN' 
                ? <span className="badge badge-warning">Markdown (📉 Reduzir)</span> 
                : <span className="badge badge-success">Markup (📈 Aumentar)</span>
              }
            </div>

            <h3 style={{ fontSize: '1.1rem' }}>{sug.product_name}</h3>
            
            <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', background: 'rgba(0,0,0,0.2)', padding: '1rem', borderRadius: '12px' }}>
              <div style={{ flex: 1 }}>
                <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Preço Atual</div>
                <div style={{ fontSize: '1.2rem', textDecoration: 'line-through', opacity: 0.6 }}>R$ {sug.current_price.toFixed(2)}</div>
              </div>
              <div style={{ fontSize: '1.5rem', color: 'var(--text-muted)' }}>→</div>
              <div style={{ flex: 1, textAlign: 'right' }}>
                <div style={{ fontSize: '0.75rem', color: sug.suggested_action === 'MARKUP' ? 'var(--success)' : 'var(--warning)' }}>Recomendado</div>
                <div style={{ fontSize: '1.5rem', fontWeight: 700, color: sug.suggested_action === 'MARKUP' ? 'var(--success)' : 'var(--warning)' }}>R$ {sug.suggested_price.toFixed(2)}</div>
              </div>
            </div>

            <p style={{ fontSize: '0.875rem', color: 'var(--text-muted)', lineHeight: 1.5 }}>
              {sug.reason}
            </p>

            <button className="btn btn-outline" style={{ marginTop: 'auto', width: '100%' }}>
              Aplicar ao ERP
            </button>
          </div>
        ))}
      </div>
    </div>
  );
};

export default Pricing;
