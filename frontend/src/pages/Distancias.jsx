import { useEffect, useState } from 'react';
import api from '../api';

export default function Distancias() {
  const [escolas, setEscolas] = useState([]);
  const [origem, setOrigem] = useState('');
  const [destino, setDestino] = useState('');
  const [resultado, setResultado] = useState(null);
  const [proximas, setProximas] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    api.get('/api/escolas').then(r => setEscolas(r.data.escolas || r.data));
  }, []);

  async function calcular(e) {
    e.preventDefault();
    if (!origem || !destino) return;
    setLoading(true); setResultado(null);
    try {
      const r = await api.post('/api/distancia', { origem_id: parseInt(origem), destino_id: parseInt(destino) });
      setResultado(r.data);
    } catch { alert('Erro ao calcular distância.'); }
    setLoading(false);
  }

  async function buscarProximas() {
    if (!origem) return;
    setLoading(true);
    const r = await api.get(`/api/escolas/${origem}/proximas?limite=5`);
    setProximas(r.data);
    setLoading(false);
  }

  return (
    <div className="container">
      <div className="mb-3">
        <h1 className="page-title"><i className="bi bi-pin-map me-2"></i>Cálculo de Distâncias</h1>
        <p className="text-muted mb-0">Calcula distâncias entre escolas</p>
      </div>

      <div className="row g-3">
        <div className="col-md-6">
          <div className="card">
            <div className="card-header">Distância entre duas escolas</div>
            <div className="card-body">
              <form onSubmit={calcular}>
                <div className="mb-3">
                  <label className="form-label">Origem</label>
                  <select className="form-select" value={origem} onChange={e => setOrigem(e.target.value)} required>
                    <option value="">Selecione...</option>
                    {escolas.map(e => <option key={e.id} value={e.id}>{e.nome_usual || e.nome_oficial}</option>)}
                  </select>
                </div>
                <div className="mb-3">
                  <label className="form-label">Destino</label>
                  <select className="form-select" value={destino} onChange={e => setDestino(e.target.value)} required>
                    <option value="">Selecione...</option>
                    {escolas.map(e => <option key={e.id} value={e.id}>{e.nome_usual || e.nome_oficial}</option>)}
                  </select>
                </div>
                <button className="btn btn-primary w-100" type="submit" disabled={loading}>
                  {loading ? <span className="spinner-border spinner-border-sm me-1" /> : <i className="bi bi-calculator me-1" />}
                  Calcular
                </button>
              </form>
              {resultado && (
                <div className="alert alert-success mt-3 text-center">
                  <div className="fw-bold fs-4">{resultado.distancia_km?.toFixed(2)} km</div>
                  <div className="small">de {resultado.origem} até {resultado.destino}</div>
                </div>
              )}
            </div>
          </div>
        </div>

        <div className="col-md-6">
          <div className="card">
            <div className="card-header">Escolas mais próximas</div>
            <div className="card-body">
              <div className="d-flex gap-2 mb-3">
                <select className="form-select" value={origem} onChange={e => setOrigem(e.target.value)}>
                  <option value="">Selecione uma escola...</option>
                  {escolas.map(e => <option key={e.id} value={e.id}>{e.nome_usual || e.nome_oficial}</option>)}
                </select>
                <button className="btn btn-outline-primary" onClick={buscarProximas} disabled={loading || !origem}>
                  {loading ? <span className="spinner-border spinner-border-sm" /> : <i className="bi bi-search" />}
                </button>
              </div>
              {proximas.length > 0 && (
                <ol className="list-group list-group-numbered">
                  {proximas.map((p, i) => (
                    <li key={i} className="list-group-item d-flex justify-content-between align-items-center">
                      <span>{p.escola?.nome_usual || p.escola?.nome_oficial}</span>
                      <span className="badge bg-primary">{p.distancia_km?.toFixed(1)} km</span>
                    </li>
                  ))}
                </ol>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
