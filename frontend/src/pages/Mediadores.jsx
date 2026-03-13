import { useEffect, useState, useRef } from 'react';
import api from '../api';

const EMPTY = { nome: '', escola_id: '' };

export default function Mediadores() {
  const [mediadores, setMediadores] = useState([]);
  const [escolas, setEscolas] = useState([]);
  const [form, setForm] = useState(EMPTY);
  const [editId, setEditId] = useState(null);
  const [saving, setSaving] = useState(false);
  const [msg, setMsg] = useState('');
  const modalRef = useRef();
  const bsModal = useRef();

  useEffect(() => {
    load();
    api.get('/api/escolas').then(r => setEscolas(r.data.escolas || r.data));
  }, []);

  useEffect(() => {
    if (modalRef.current) {
      import('bootstrap/dist/js/bootstrap.bundle.min.js').then(({ Modal }) => {
        bsModal.current = new Modal(modalRef.current);
      });
    }
  }, []);

  async function load() {
    const r = await api.get('/api/mediadores');
    setMediadores(r.data);
  }

  function abrirNovo() { setForm(EMPTY); setEditId(null); setMsg(''); bsModal.current?.show(); }
  function abrirEditar(m) { setForm({ nome: m.nome, escola_id: m.escola_id || '' }); setEditId(m.id); setMsg(''); bsModal.current?.show(); }

  async function salvar() {
    setSaving(true); setMsg('');
    try {
      const payload = { nome: form.nome, escola_id: form.escola_id ? parseInt(form.escola_id) : null };
      if (editId) await api.put(`/api/mediadores/${editId}`, payload);
      else await api.post('/api/mediadores', payload);
      bsModal.current?.hide();
      await load();
    } catch (e) { setMsg(e.response?.data?.erro || 'Erro ao salvar.'); }
    setSaving(false);
  }

  return (
    <div className="container">
      <div className="d-flex justify-content-between align-items-center mb-3 flex-wrap gap-2">
        <div>
          <h1 className="page-title"><i className="bi bi-people me-2"></i>Mediadores</h1>
          <p className="text-muted mb-0">{mediadores.length} mediadores cadastrados</p>
        </div>
        <button className="btn btn-primary" onClick={abrirNovo}>
          <i className="bi bi-plus-circle me-1"></i>Novo Mediador
        </button>
      </div>

      <div className="card">
        <div className="card-body">
          {mediadores.length === 0 ? (
            <div className="text-center py-5">
              <i className="bi bi-people" style={{ fontSize: '3rem', color: '#ccc' }}></i>
              <p className="text-muted mt-3">Nenhum mediador cadastrado.</p>
            </div>
          ) : (
            <div className="table-responsive">
              <table className="table table-hover align-middle">
                <thead className="table-light">
                  <tr><th>Nome</th><th>Escola</th><th className="text-center">Status</th><th className="text-center">Ações</th></tr>
                </thead>
                <tbody>
                  {mediadores.map(m => (
                    <tr key={m.id}>
                      <td><i className="bi bi-person-fill text-primary me-1"></i><strong>{m.nome}</strong></td>
                      <td>{m.escola_nome || <span className="text-muted">–</span>}</td>
                      <td className="text-center">
                        <span className={`badge ${m.ativo ? 'bg-success' : 'bg-secondary'}`}>{m.ativo ? 'Ativo' : 'Inativo'}</span>
                      </td>
                      <td className="text-center">
                        <button className="btn btn-sm btn-outline-primary" onClick={() => abrirEditar(m)}>
                          <i className="bi bi-pencil"></i>
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>

      <div className="modal fade" ref={modalRef} tabIndex="-1">
        <div className="modal-dialog">
          <div className="modal-content">
            <div className="modal-header">
              <h5 className="modal-title"><i className="bi bi-person me-2"></i>{editId ? 'Editar Mediador' : 'Novo Mediador'}</h5>
              <button type="button" className="btn-close" data-bs-dismiss="modal"></button>
            </div>
            <div className="modal-body">
              {msg && <div className="alert alert-danger py-2">{msg}</div>}
              <div className="mb-3">
                <label className="form-label">Nome *</label>
                <input className="form-control" value={form.nome} onChange={e => setForm(f => ({ ...f, nome: e.target.value }))} />
              </div>
              <div className="mb-3">
                <label className="form-label">Escola Vinculada</label>
                <select className="form-select" value={form.escola_id} onChange={e => setForm(f => ({ ...f, escola_id: e.target.value }))}>
                  <option value="">Nenhuma</option>
                  {escolas.map(e => <option key={e.id} value={e.id}>{e.nome_usual || e.nome_oficial}</option>)}
                </select>
              </div>
            </div>
            <div className="modal-footer">
              <button className="btn btn-secondary" data-bs-dismiss="modal">Cancelar</button>
              <button className="btn btn-primary" onClick={salvar} disabled={saving}>
                {saving ? <span className="spinner-border spinner-border-sm me-1" /> : <i className="bi bi-check-circle me-1" />}Salvar
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
