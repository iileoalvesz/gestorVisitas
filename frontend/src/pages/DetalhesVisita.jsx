import { useEffect, useState } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import api from '../api';

export default function DetalhesVisita() {
  const { id } = useParams();
  const [visita, setVisita] = useState(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    api.get(`/api/visitas/${id}`).then(r => { setVisita(r.data); setLoading(false); }).catch(() => navigate('/visitas'));
  }, [id]);

  function fmt(d) {
    if (!d) return '–';
    const [y, m, day] = d.split('-');
    return `${day}/${m}/${y}`;
  }

  function isImage(nome) { return /\.(jpg|jpeg|png)$/i.test(nome); }
  function isPdf(nome) { return /\.pdf$/i.test(nome); }

  async function excluir() {
    if (!confirm('Remover esta visita permanentemente?')) return;
    await api.delete(`/api/visitas/${id}`);
    navigate('/visitas');
  }

  if (loading) return <div className="d-flex justify-content-center mt-5"><div className="spinner-border text-primary"></div></div>;
  if (!visita) return null;

  return (
    <div className="container">
      <div className="d-flex justify-content-between align-items-center mb-3 flex-wrap gap-2">
        <div>
          <h1 className="page-title"><i className="bi bi-clipboard-check me-2"></i>Detalhes da Visita</h1>
          <p className="text-muted mb-0">{visita.escola_nome} – {fmt(visita.data)}</p>
        </div>
        <div className="d-flex gap-2">
          <Link to="/visitas" className="btn btn-outline-secondary"><i className="bi bi-arrow-left me-1"></i>Voltar</Link>
          <button className="btn btn-outline-danger" onClick={excluir}><i className="bi bi-trash me-1"></i>Excluir</button>
        </div>
      </div>

      <div className="card mb-3">
        <div className="card-header">Informações Gerais</div>
        <div className="card-body">
          <div className="row g-3">
            {[['Escola', visita.escola_nome], ['Data', fmt(visita.data)], ['Turno', visita.turno], ['Oficina', visita.oficina], ['Mediador', visita.mediador_nome], ['Articulador', visita.articulador_nome], ['Gestor', visita.gestor_nome]].map(([l, v]) => (
              <div className="col-md-4" key={l}>
                <div className="small text-muted">{l}</div>
                <div className="fw-semibold">{v || '–'}</div>
              </div>
            ))}
          </div>
          {visita.observacoes && <><hr/><div className="small text-muted">Observações</div><p>{visita.observacoes}</p></>}
          {visita.contribuicoes && <><div className="small text-muted">Contribuições</div><p>{visita.contribuicoes}</p></>}
          {visita.combinados && <><div className="small text-muted">Combinados</div><p>{visita.combinados}</p></>}
        </div>
      </div>

      {visita.turmas?.length > 0 && (
        <div className="card mb-3">
          <div className="card-header">Turmas</div>
          <div className="card-body">
            <div className="table-responsive">
              <table className="table table-sm">
                <thead><tr><th>Turma</th><th>Qtd</th><th>Nível</th><th>Avaliação</th></tr></thead>
                <tbody>
                  {visita.turmas.map(t => (
                    <tr key={t.id}><td>{t.nome_turma}</td><td>{t.quantidade}</td><td>{t.nivel}</td><td>{t.avaliacao}</td></tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {visita.anexos?.length > 0 && (
        <div className="card mb-3">
          <div className="card-header">Anexos</div>
          <div className="card-body">
            <div className="row g-3">
              {visita.anexos.map(a => (
                <div className="col-md-3 col-6" key={a.id}>
                  {isImage(a.nome_original) ? (
                    <a href={`/${a.caminho}`} target="_blank" rel="noreferrer">
                      <img src={`/${a.caminho}`} className="img-fluid rounded" alt={a.nome_original} />
                    </a>
                  ) : isPdf(a.nome_original) ? (
                    <a href={`/${a.caminho}`} target="_blank" rel="noreferrer" className="d-flex align-items-center gap-2 text-danger">
                      <i className="bi bi-file-earmark-pdf fs-3"></i>{a.nome_original}
                    </a>
                  ) : (
                    <a href={`/${a.caminho}`} target="_blank" rel="noreferrer" className="d-flex align-items-center gap-2">
                      <i className="bi bi-file-earmark fs-3"></i>{a.nome_original}
                    </a>
                  )}
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
