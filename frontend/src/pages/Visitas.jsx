import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import api from '../api';

export default function Visitas() {
  const [visitas, setVisitas] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.get('/api/visitas').then(r => { setVisitas(r.data.visitas || r.data); setLoading(false); });
  }, []);

  function formatData(d) {
    if (!d) return '–';
    const [y, m, day] = d.split('-');
    return `${day}/${m}/${y}`;
  }

  return (
    <div className="container-fluid">
      <div className="d-flex justify-content-between align-items-center mb-3 flex-wrap gap-2">
        <div>
          <h1 className="page-title"><i className="bi bi-clipboard-check me-2"></i>Visitas</h1>
          <p className="text-muted mb-0">Registro de visitas realizadas</p>
        </div>
        <Link to="/visitas/nova" className="btn btn-primary">
          <i className="bi bi-plus-circle me-1"></i>Nova Visita
        </Link>
      </div>

      <div className="card">
        <div className="card-body">
          {loading ? (
            <div className="text-center py-4"><div className="spinner-border text-primary"></div></div>
          ) : visitas.length === 0 ? (
            <div className="text-center py-5">
              <i className="bi bi-clipboard" style={{ fontSize: '3rem', color: '#ccc' }}></i>
              <p className="text-muted mt-3">Nenhuma visita registrada.</p>
              <Link to="/visitas/nova" className="btn btn-primary">Registrar Primeira Visita</Link>
            </div>
          ) : (
            <div className="table-responsive">
              <table className="table table-hover align-middle">
                <thead className="table-light">
                  <tr>
                    <th>Data</th>
                    <th>Escola</th>
                    <th>Turno</th>
                    <th>Mediador</th>
                    <th>Observações</th>
                    <th className="text-center">Anexos</th>
                    <th></th>
                  </tr>
                </thead>
                <tbody>
                  {visitas.map(v => (
                    <tr key={v.id}>
                      <td className="fw-semibold text-nowrap">{formatData(v.data)}</td>
                      <td>{v.escola_nome || <span className="text-muted">–</span>}</td>
                      <td>
                        {v.turno === 'manha' && <span className="badge bg-warning text-dark">Manhã</span>}
                        {v.turno === 'tarde' && <span className="badge bg-primary">Tarde</span>}
                        {v.turno === 'integral' && <span className="badge bg-success">Integral</span>}
                        {!v.turno && <span className="text-muted">–</span>}
                      </td>
                      <td>{v.mediador_nome || <span className="text-muted">–</span>}</td>
                      <td className="small text-muted">{v.observacoes ? v.observacoes.slice(0, 50) + (v.observacoes.length > 50 ? '…' : '') : '–'}</td>
                      <td className="text-center">
                        {v.anexos?.length > 0 ? (
                          <span className="badge bg-secondary"><i className="bi bi-paperclip me-1"></i>{v.anexos.length}</span>
                        ) : '–'}
                      </td>
                      <td>
                        <Link to={`/visitas/${v.id}`} className="btn btn-sm btn-outline-primary">
                          <i className="bi bi-eye"></i>
                        </Link>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
