import { useEffect, useState, useRef } from 'react';
import api from '../api';

const EMPTY = { nome_oficial: '', nome_usual: '', diretor: '', mediador: '', endereco: '', cep: '', bloco_1: false, origem: 'manual' };

export default function Escolas() {
  const [escolas, setEscolas] = useState([]);
  const [loading, setLoading] = useState(true);
  const [busca, setBusca] = useState('');
  const [form, setForm] = useState(EMPTY);
  const [editId, setEditId] = useState(null);
  const [saving, setSaving] = useState(false);
  const [msg, setMsg] = useState('');
  const modalRef = useRef(null);
  const bsModal = useRef(null);

  useEffect(() => {
    load();
  }, []);

  useEffect(() => {
    if (modalRef.current) {
      import('bootstrap/dist/js/bootstrap.bundle.min.js').then(({ Modal }) => {
        bsModal.current = new Modal(modalRef.current);
      });
    }
  }, []);

  async function load() {
    setLoading(true);
    const r = await api.get('/api/escolas');
    setEscolas(r.data.escolas || r.data);
    setLoading(false);
  }

  function abrirNovo() {
    setForm(EMPTY); setEditId(null); setMsg('');
    bsModal.current?.show();
  }

  function abrirEditar(e) {
    setForm({ ...e }); setEditId(e.id); setMsg('');
    bsModal.current?.show();
  }

  async function salvar() {
    setSaving(true); setMsg('');
    try {
      if (editId) {
        await api.put(`/api/escolas/${editId}`, form);
      } else {
        await api.post('/api/escolas', form);
      }
      bsModal.current?.hide();
      await load();
    } catch (e) {
      setMsg(e.response?.data?.erro || 'Erro ao salvar');
    } finally {
      setSaving(false);
    }
  }

  async function excluir(id) {
    if (!confirm('Remover esta escola?')) return;
    await api.delete(`/api/escolas/${id}`);
    setEscolas(prev => prev.filter(e => e.id !== id));
  }

  async function geocodificar(id) {
    if (!confirm('Geocodificar esta escola? Pode demorar alguns segundos.')) return;
    try {
      await api.post('/api/escolas/geocodificar', { escola_id: id });
      await load();
    } catch { alert('Erro ao geocodificar.'); }
  }

  const filtradas = escolas.filter(e =>
    [e.nome_oficial, e.nome_usual, e.diretor, e.mediador].join(' ').toLowerCase().includes(busca.toLowerCase())
  );

  return (
    <div className="container-fluid">
      <div className="d-flex justify-content-between align-items-center mb-3 flex-wrap gap-2">
        <div>
          <h1 className="page-title"><i className="bi bi-building me-2"></i>Escolas</h1>
          <p className="text-muted mb-0">{escolas.length} escolas cadastradas</p>
        </div>
        <button className="btn btn-primary" onClick={abrirNovo}>
          <i className="bi bi-plus-circle me-1"></i>Nova Escola
        </button>
      </div>

      <div className="card">
        <div className="card-body">
          <input className="form-control mb-3" placeholder="Buscar escola..." value={busca} onChange={e => setBusca(e.target.value)} />
          {loading ? (
            <div className="text-center py-4"><div className="spinner-border text-primary"></div></div>
          ) : (
            <div className="table-responsive">
              <table className="table table-hover align-middle">
                <thead className="table-light">
                  <tr>
                    <th>Nome</th>
                    <th>Diretor</th>
                    <th>Mediador</th>
                    <th>Endereço</th>
                    <th className="text-center">Bloco 1</th>
                    <th className="text-center">Coords</th>
                    <th className="text-center">Ações</th>
                  </tr>
                </thead>
                <tbody>
                  {filtradas.map(e => (
                    <tr key={e.id}>
                      <td>
                        <div className="fw-semibold">{e.nome_usual || e.nome_oficial}</div>
                        {e.nome_usual && <div className="small text-muted">{e.nome_oficial}</div>}
                      </td>
                      <td>{e.diretor || <span className="text-muted">–</span>}</td>
                      <td>{e.mediador || <span className="text-muted">–</span>}</td>
                      <td className="small">{e.endereco || <span className="text-muted">–</span>}</td>
                      <td className="text-center">
                        {e.bloco_1 ? <span className="badge bg-primary">Sim</span> : <span className="badge bg-secondary">Não</span>}
                      </td>
                      <td className="text-center">
                        {e.latitude ? (
                          <span className="text-success"><i className="bi bi-geo-alt-fill"></i></span>
                        ) : (
                          <button className="btn btn-sm btn-outline-secondary" onClick={() => geocodificar(e.id)} title="Geocodificar">
                            <i className="bi bi-geo-alt"></i>
                          </button>
                        )}
                      </td>
                      <td className="text-center">
                        <button className="btn btn-sm btn-outline-primary me-1" onClick={() => abrirEditar(e)}>
                          <i className="bi bi-pencil"></i>
                        </button>
                        {e.origem === 'manual' && (
                          <button className="btn btn-sm btn-outline-danger" onClick={() => excluir(e.id)}>
                            <i className="bi bi-trash"></i>
                          </button>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
              {filtradas.length === 0 && <p className="text-center text-muted py-3">Nenhuma escola encontrada.</p>}
            </div>
          )}
        </div>
      </div>

      {/* Modal */}
      <div className="modal fade" ref={modalRef} tabIndex="-1">
        <div className="modal-dialog modal-lg">
          <div className="modal-content">
            <div className="modal-header">
              <h5 className="modal-title"><i className="bi bi-building me-2"></i>{editId ? 'Editar Escola' : 'Nova Escola'}</h5>
              <button type="button" className="btn-close" data-bs-dismiss="modal"></button>
            </div>
            <div className="modal-body">
              {msg && <div className="alert alert-danger py-2">{msg}</div>}
              <div className="row g-3">
                <div className="col-md-6">
                  <label className="form-label">Nome Oficial *</label>
                  <input className="form-control" value={form.nome_oficial} onChange={e => setForm(f => ({ ...f, nome_oficial: e.target.value }))} />
                </div>
                <div className="col-md-6">
                  <label className="form-label">Nome Usual</label>
                  <input className="form-control" value={form.nome_usual} onChange={e => setForm(f => ({ ...f, nome_usual: e.target.value }))} />
                </div>
                <div className="col-md-6">
                  <label className="form-label">Diretor</label>
                  <input className="form-control" value={form.diretor} onChange={e => setForm(f => ({ ...f, diretor: e.target.value }))} />
                </div>
                <div className="col-md-6">
                  <label className="form-label">Mediador</label>
                  <input className="form-control" value={form.mediador} onChange={e => setForm(f => ({ ...f, mediador: e.target.value }))} />
                </div>
                <div className="col-md-8">
                  <label className="form-label">Endereço</label>
                  <input className="form-control" value={form.endereco} onChange={e => setForm(f => ({ ...f, endereco: e.target.value }))} />
                </div>
                <div className="col-md-4">
                  <label className="form-label">CEP</label>
                  <input className="form-control" value={form.cep} onChange={e => setForm(f => ({ ...f, cep: e.target.value }))} />
                </div>
                <div className="col-12">
                  <div className="form-check">
                    <input className="form-check-input" type="checkbox" id="bloco1" checked={form.bloco_1} onChange={e => setForm(f => ({ ...f, bloco_1: e.target.checked }))} />
                    <label className="form-check-label" htmlFor="bloco1">Escola do Bloco 1</label>
                  </div>
                </div>
              </div>
            </div>
            <div className="modal-footer">
              <button className="btn btn-secondary" data-bs-dismiss="modal">Cancelar</button>
              <button className="btn btn-primary" onClick={salvar} disabled={saving}>
                {saving ? <span className="spinner-border spinner-border-sm me-1" /> : <i className="bi bi-check-circle me-1" />}
                Salvar
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
