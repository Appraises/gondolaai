import React, { useEffect, useState } from 'react';
import { Play } from 'lucide-react';

const Alerts: React.FC = () => {
    const [alerts, setAlerts] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);
    const [dispatching, setDispatching] = useState(false);

    const loadAlerts = () => {
        setLoading(true);
        fetch('http://localhost:8000/api/alerts/?store_id=1')
            .then(res => res.json())
            .then(data => {
                setAlerts(data);
                setLoading(false);
            })
            .catch(err => {
                console.error("API error", err);
                setLoading(false);
            });
    }

    useEffect(() => {
        loadAlerts();
    }, []);

    const handleDispatch = async () => {
        setDispatching(true);
        try {
            await fetch('http://localhost:8000/api/alerts/dispatch?store_id=1', { method: 'POST' });
            alert("✨ Inteligência artificial resumiu tudo e os Alertas Críticos foram disparados ao Manager no WhatsApp com sucesso!");
            loadAlerts(); // recarrega pra atualizar o boolean if is_read!
        } catch (e) {
            console.error(e);
        }
        setDispatching(false);
    };

    return (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
            <div className="flex items-center justify-between" style={{ width: '100%' }}>
                <div>
                    <h1 style={{ fontSize: '1.75rem', marginBottom: '0.5rem' }}>Central de Alertas ML</h1>
                    <p style={{ color: 'var(--text-muted)' }}>Insights preditivos sobre o estoque rodados na madrugada passada pelo XGBoost.</p>
                </div>
                <button
                    className="btn btn-primary"
                    onClick={handleDispatch}
                    disabled={dispatching || alerts.filter(a => !a.is_read).length === 0}
                    style={{ background: 'var(--danger)', boxShadow: '0 0 15px rgba(239, 68, 68, 0.4)' }}
                >
                    <Play size={18} /> {dispatching ? 'Enviando...' : 'Fazer Push WhatsApp Agora (' + alerts.filter(a => !a.is_read && a.severity === 'critical').length + ' críticos)'}
                </button>
            </div>

            <div className="grid-cards">
                {alerts.map(a => (
                    <div key={a.id} className="glass-panel" style={{ display: 'flex', flexDirection: 'column' }}>
                        
                        <div style={{ padding: '1rem 1.5rem', borderBottom: '1px solid var(--panel-border)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                            <span className={`badge badge-${a.severity === 'critical' ? 'critical' : a.severity === 'warning' ? 'warning' : 'info'}`}>
                                {a.alert_type}
                            </span>
                            {!a.is_read && <span style={{ width: '8px', height: '8px', borderRadius: '50%', background: 'var(--primary)', boxShadow: '0 0 10px var(--primary-glow)' }}></span>}
                        </div>
                        
                        <div style={{ padding: '1.5rem', display: 'flex', flexDirection: 'column', gap: '1rem', flex: 1 }}>
                            <div>
                                <h3 style={{ fontSize: '1.25rem', marginBottom: '0.25rem' }}>{a.product_name}</h3>
                                <p style={{ fontSize: '0.875rem', color: 'var(--text-muted)' }}>EAN: {a.product_ean}</p>
                            </div>
                            
                            <p style={{ color: '#d1d5db', lineHeight: 1.5 }}>
                                {a.message}
                            </p>

                            <div style={{ marginTop: 'auto', background: 'rgba(0,0,0,0.3)', padding: '1rem', borderRadius: '8px', borderLeft: '4px solid var(--warning)' }}>
                                <p style={{ fontSize: '0.875rem', color: 'var(--text-main)', margin: 0, display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                                    💡 <strong>ML Sugere:</strong> {a.suggested_action}
                                </p>
                            </div>
                        </div>
                    </div>
                ))}
            </div>

        </div>
    );
};

export default Alerts;
