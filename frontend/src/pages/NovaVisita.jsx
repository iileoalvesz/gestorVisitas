import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../api';

export default function NovaVisita() {
  const [escolas, setEscolas] = useState([]);
  const [form, setForm] = useState({ escola_id: '', escola_nome: '', data: new Date().toISOString().split('T')[0], turno: 'manha', oficina: '', observacoes: '', contribuicoes: '', combinados: '', mediador_nome: '', articulador_nome: '', gestor_nome: '' });
  const [anexos, setAnexos] = useState([]);
  const [saving, setSaving] = useState(false);
  const [msg, setMsg] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    api.get('/api/escolas').then(r => setEscolas(r.data.escolas || r.data));
  }, []);

  function onEscolaChange(e) {
    const id = e.target.value;
    const escola = escolas.find(e => String(e.id) === id);
    setForm(f => ({ ...f, escola_id: id, escola_nome: escola?.nome_usual || escola?.nome_oficial || '' }));
  }

  async function salvar(e) {
    e.preventDefault();
    setSaving(true); setMsg('');
    try {
      const fd = new FormData();
      Object.entries(form).forEach(([k, v]) => fd.append(k, v));
      for (const f of anexos) fd.append('anexos', f);
      const r = await api.post('/api/visitas', fd);
      navigate(`/visitas/${r.data.id}`);
    } catch (err) {
      setMsg(err.response?.data?.erro || 'Erro ao salvar visita.');
      setSaving(false);
    }
  }

  function campo(label, key, type = 'text', rows) {
    const props = { className: 'form-control', value: form[key], onChange: e => setForm(f => ({ ...f, [key]: e.target.value }) )};
    return (
      <div className="mb-3">
        <label className="form-label">{label}</label>
        {rows ? <textarea {...props} rows={rows} /> : <input type={type} {...props} />}
      </div>
    );
  }

  return (
    <div className="container">
      <div className="mb-3">
        <h1 className="page-title"><i className="bi bi-clipboard-plus me-2"></i>Nova Visita</h1>
      </div>
      <form onSubmit={salvar}>
        <div className="card mb-3">
          <div className="card-header">Informações da Visita</div>
          <div className="card-body">
            {msg && <div className="alert alert-danger">{msg}</div>}
            <div className="row g-3">
              <div className="col-md-6">
                <label className="form-label">Escola</label>
                <select className="form-select" value={form.escola_id} onChange={onEscolaChange}>
                  <option value="">Selecione...</option>
                  {escolas.map(e => <option key={e.id} value={e.id}>{e.nome_usual || e.nome_oficial}</option>)}
                </select>
              </div>
              <div className="col-md-3">
                <label className="form-label">Data</label>
                <input type="date" className="form-control" value={form.data} onChange={e => setForm(f => ({ ...f, data: e.target.value }))} required />
              </div>
              <div className="col-md-3">
                <label className="form-label">Turno</label>
                <select className="form-select" value={form.turno} onChange={e => setForm(f => ({ ...f, turno: e.target.value }))}>
                  <option value="manha">Manhã</option>
                  <option value="tarde">Tarde</option>
                  <option value="integral">Integral</option>
                </select>
              </div>
              <div className="col-md-4">{campo('Mediador', 'mediador_nome')}</div>
              <div className="col-md-4">{campo('Articulador', 'articulador_nome')}</div>
              <div className="col-md-4">{campo('Gestor', 'gestor_nome')}</div>
              <div className="col-12">{campo('Oficina', 'oficina')}</div>
              <div className="col-12">{campo('Observações das Oficinas', 'observacoes', 'text', 3)}</div>
              <div className="col-12">{campo('Contribuições / Sugestões', 'contribuicoes', 'text', 2)}</div>
              <div className="col-12">{campo('Combinados', 'combinados', 'text', 2)}</div>
            </div>
          </div>
        </div>

        <div className="card mb-3">
          <div className="card-header">Anexos</div>
          <div className="card-body">
            <input type="file" className="form-control" multiple accept=".pdf,.jpg,.jpeg,.png,.doc,.docx" onChange={e => setAnexos([...e.target.files])} />
            {anexos.length > 0 && (
              <ul className="list-unstyled mt-2 mb-0">
                {[...anexos].map((f, i) => <li key={i} className="small text-muted"><i className="bi bi-paperclip me-1"></i>{f.name}</li>)}
              </ul>
            )}
          </div>
        </div>

        <div className="d-flex gap-2">
          <button type="submit" className="btn btn-primary" disabled={saving}>
            {saving ? <span className="spinner-border spinner-border-sm me-1" /> : <i className="bi bi-check-circle me-1" />}
            Salvar Visita
          </button>
          <button type="button" className="btn btn-secondary" onClick={() => navigate('/visitas')}>Cancelar</button>
        </div>
      </form>
    </div>
  );
}
