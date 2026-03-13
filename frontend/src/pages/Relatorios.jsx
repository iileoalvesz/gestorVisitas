import { useState } from 'react';
import api from '../api';

export default function Relatorios() {
  const [ano, setAno] = useState(new Date().getFullYear());
  const [mes, setMes] = useState('');
  const [loading, setLoading] = useState('');

  async function gerarConsolidado() {
    setLoading('consolidado');
    try {
      const r = await api.post('/api/relatorios/consolidado', { ano: parseInt(ano), mes: mes ? parseInt(mes) : null }, { responseType: 'blob' });
      const url = URL.createObjectURL(r.data);
      const a = document.createElement('a'); a.href = url; a.download = `relatorio_consolidado_${ano}.docx`; a.click();
      URL.revokeObjectURL(url);
    } catch { alert('Erro ao gerar relatório.'); }
    setLoading('');
  }

  async function gerarFolha() {
    setLoading('folha');
    try {
      const r = await api.post('/api/relatorios/folha-oficinas', { ano: parseInt(ano), mes: mes ? parseInt(mes) : null }, { responseType: 'blob' });
      const url = URL.createObjectURL(r.data);
      const a = document.createElement('a'); a.href = url; a.download = `folha_oficinas_${ano}.docx`; a.click();
      URL.revokeObjectURL(url);
    } catch { alert('Erro ao gerar folha.'); }
    setLoading('');
  }

  const meses = ['Janeiro','Fevereiro','Março','Abril','Maio','Junho','Julho','Agosto','Setembro','Outubro','Novembro','Dezembro'];

  return (
    <div className="container">
      <div className="mb-3">
        <h1 className="page-title"><i className="bi bi-file-earmark-bar-graph me-2"></i>Relatórios</h1>
        <p className="text-muted mb-0">Geração de relatórios em Word</p>
      </div>

      <div className="card mb-3">
        <div className="card-header">Filtros</div>
        <div className="card-body">
          <div className="row g-3">
            <div className="col-md-4">
              <label className="form-label">Ano</label>
              <input type="number" className="form-control" value={ano} onChange={e => setAno(e.target.value)} min="2020" max="2030" />
            </div>
            <div className="col-md-4">
              <label className="form-label">Mês (opcional)</label>
              <select className="form-select" value={mes} onChange={e => setMes(e.target.value)}>
                <option value="">Todos</option>
                {meses.map((m, i) => <option key={i} value={i+1}>{m}</option>)}
              </select>
            </div>
          </div>
        </div>
      </div>

      <div className="row g-3">
        <div className="col-md-6">
          <div className="card h-100">
            <div className="card-body text-center">
              <i className="bi bi-file-earmark-word text-primary" style={{ fontSize: '3rem' }}></i>
              <h5 className="mt-2">Relatório Consolidado</h5>
              <p className="text-muted small">Visitas realizadas com avaliações e turmas</p>
              <button className="btn btn-primary w-100" onClick={gerarConsolidado} disabled={!!loading}>
                {loading === 'consolidado' ? <span className="spinner-border spinner-border-sm me-1" /> : <i className="bi bi-download me-1" />}
                Gerar e Baixar
              </button>
            </div>
          </div>
        </div>
        <div className="col-md-6">
          <div className="card h-100">
            <div className="card-body text-center">
              <i className="bi bi-file-earmark-spreadsheet text-success" style={{ fontSize: '3rem' }}></i>
              <h5 className="mt-2">Folha de Oficinas</h5>
              <p className="text-muted small">Lista de oficinas visitadas por escola</p>
              <button className="btn btn-success w-100" onClick={gerarFolha} disabled={!!loading}>
                {loading === 'folha' ? <span className="spinner-border spinner-border-sm me-1" /> : <i className="bi bi-download me-1" />}
                Gerar e Baixar
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
