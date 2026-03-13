import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import api from '../api';

function StatCard({ icon, value, label, color, to }) {
  const content = (
    <div className="card text-center p-3 h-100">
      <i className={`bi ${icon} mb-2`} style={{ fontSize: '2rem', color }}></i>
      <div style={{ fontSize: '2rem', fontWeight: 700, color }}>{value ?? '–'}</div>
      <div className="text-muted small">{label}</div>
    </div>
  );
  return to ? <Link to={to} className="text-decoration-none">{content}</Link> : content;
}

export default function Dashboard() {
  const [stats, setStats] = useState(null);

  useEffect(() => {
    api.get('/api/estatisticas').then(r => setStats(r.data)).catch(() => {});
  }, []);

  const ano = new Date().getFullYear();

  return (
    <div className="container-fluid">
      <div className="d-flex justify-content-between align-items-center mb-4">
        <div>
          <h1 className="page-title"><i className="bi bi-house me-2"></i>Início</h1>
          <p className="text-muted mb-0">Visão geral do sistema</p>
        </div>
        <Link to="/visitas/nova" className="btn btn-primary">
          <i className="bi bi-plus-circle me-1"></i>Nova Visita
        </Link>
      </div>

      <div className="row g-3 mb-4">
        <div className="col-6 col-md-3">
          <StatCard icon="bi-building" value={stats?.total_escolas} label="Escolas" color="#1e40af" to="/escolas" />
        </div>
        <div className="col-6 col-md-3">
          <StatCard icon="bi-clipboard-check" value={stats?.visitas_ano} label={`Visitas ${ano}`} color="#059669" to="/visitas" />
        </div>
        <div className="col-6 col-md-3">
          <StatCard icon="bi-calendar-event" value={stats?.eventos_pendentes} label="Eventos Pendentes" color="#d97706" to="/agenda" />
        </div>
        <div className="col-6 col-md-3">
          <StatCard icon="bi-people" value={stats?.total_mediadores} label="Mediadores" color="#7c3aed" to="/mediadores" />
        </div>
      </div>

      <div className="row g-3">
        <div className="col-md-6">
          <div className="card">
            <div className="card-header"><i className="bi bi-lightning me-2"></i>Ações Rápidas</div>
            <div className="card-body d-grid gap-2">
              <Link to="/visitas/nova" className="btn btn-outline-primary text-start">
                <i className="bi bi-clipboard-plus me-2"></i>Registrar Visita
              </Link>
              <Link to="/agenda" className="btn btn-outline-warning text-start">
                <i className="bi bi-calendar-plus me-2"></i>Adicionar à Agenda
              </Link>
              <Link to="/relatorios" className="btn btn-outline-success text-start">
                <i className="bi bi-file-earmark-bar-graph me-2"></i>Gerar Relatório
              </Link>
              <Link to="/mapa" className="btn btn-outline-info text-start">
                <i className="bi bi-map me-2"></i>Ver Mapa de Escolas
              </Link>
            </div>
          </div>
        </div>
        <div className="col-md-6">
          <div className="card">
            <div className="card-header"><i className="bi bi-info-circle me-2"></i>Resumo</div>
            <div className="card-body">
              {stats ? (
                <table className="table table-sm mb-0">
                  <tbody>
                    <tr><td>Escolas no Bloco 1</td><td className="fw-bold">{stats.escolas_bloco1}</td></tr>
                    <tr><td>Escolas sem visita ({ano})</td><td className="fw-bold text-warning">{stats.escolas_sem_visita}</td></tr>
                    <tr><td>Visitas este mês</td><td className="fw-bold">{stats.visitas_mes}</td></tr>
                    <tr><td>Total de visitas</td><td className="fw-bold">{stats.total_visitas}</td></tr>
                  </tbody>
                </table>
              ) : <div className="text-center py-3"><div className="spinner-border spinner-border-sm text-primary"></div></div>}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
