import React, { useState } from 'react';
import { Send, KeyRound, Smartphone } from 'lucide-react';

const Settings: React.FC = () => {
    const [status] = useState('saved');

    return (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
            <div>
                <h1 style={{ fontSize: '1.75rem', marginBottom: '0.5rem' }}>Integrações IA</h1>
                <p style={{ color: 'var(--text-muted)' }}>Configure o GôndolaBot para disparar gatilhos ativos e conversar.</p>
            </div>

            <div className="glass-panel" style={{ padding: '2rem', maxWidth: '800px' }}>
                <h3 style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1.5rem', fontSize: '1.25rem' }}>
                    <Smartphone size={24} color="var(--primary)" />
                    Evolution API (WhatsApp)
                </h3>

                <form className="flex-col gap-4" style={{ display: 'flex', flexDirection: 'column' }}>
                    
                    <div className="flex-col" style={{ gap: '0.5rem', display: 'flex', flexDirection: 'column' }}>
                        <label style={{ fontSize: '0.875rem', color: 'var(--text-muted)' }}>Instance Name</label>
                        <input
                            type="text"
                            placeholder="gondola_bot_loja1"
                            className="glass-panel"
                            style={{ padding: '0.75rem', border: '1px solid var(--panel-border)', background: 'rgba(0,0,0,0.3)', color: 'white', borderRadius: '8px' }}
                            defaultValue="gondola_bot_loja1"
                        />
                    </div>

                    <div className="flex-col" style={{ gap: '0.5rem', display: 'flex', flexDirection: 'column' }}>
                        <label style={{ fontSize: '0.875rem', color: 'var(--text-muted)', display: 'flex', alignItems: 'center', gap: '4px' }}>
                            <KeyRound size={14} /> Instance Token (Senha)
                        </label>
                        <input
                            type="password"
                            placeholder="*************"
                            className="glass-panel"
                            style={{ padding: '0.75rem', border: '1px solid var(--panel-border)', background: 'rgba(0,0,0,0.3)', color: 'white', borderRadius: '8px' }}
                            defaultValue="faketoken123"
                        />
                    </div>

                    <hr style={{ border: 'none', borderTop: '1px solid var(--panel-border)', margin: '1rem 0' }} />

                    <div className="flex-col" style={{ gap: '0.5rem', display: 'flex', flexDirection: 'column' }}>
                        <label style={{ fontSize: '0.875rem', color: 'var(--text-muted)' }}>Telefone do Gerente (Permissão de Chat)</label>
                        <input
                            type="text"
                            placeholder="Ex: 5511999999999"
                            className="glass-panel"
                            style={{ padding: '0.75rem', border: '1px solid var(--panel-border)', background: 'rgba(0,0,0,0.3)', color: 'white', borderRadius: '8px' }}
                            defaultValue="5511999999999"
                        />
                        <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', opacity: 0.7 }}>Apenas este número pode conversar como Admin com o Cérebro Google Gemini.</span>
                    </div>

                    <div className="flex-col" style={{ gap: '0.5rem', display: 'flex', flexDirection: 'column', marginTop: '1rem' }}>
                        <label style={{ fontSize: '0.875rem', color: 'var(--text-muted)' }}>Listas de Alertas via Push</label>
                        <input
                            type="text"
                            placeholder="551199999999, 552188888888"
                            className="glass-panel"
                            style={{ padding: '0.75rem', border: '1px solid var(--panel-border)', background: 'rgba(0,0,0,0.3)', color: 'white', borderRadius: '8px' }}
                            defaultValue="5511999999999"
                        />
                        <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', opacity: 0.7 }}>Números separados por vírgula que receberão o Push quando Rupturas/Markdowns Urgentes forem detectadas de madrugada.</span>
                    </div>

                    <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: '2rem' }}>
                        <button type="button" className="btn btn-primary" style={{ padding: '0.75rem 2rem' }}>
                            <Send size={18} /> {status === 'saved' ? 'Configurações Salvas' : 'Salvar Alterações'}
                        </button>
                    </div>

                </form>

            </div>
        </div>
    );
};

export default Settings;
