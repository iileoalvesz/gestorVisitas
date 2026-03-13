import { useEffect, useState, useRef, useCallback } from 'react';
import api from '../api';

const DIAS = ['Dom', 'Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sab'];
const MESES = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'];
const TIPOS = ['visita', 'reuniao', 'apresentacao', 'capacitacao', 'planejamento', 'relatorio', 'feriado', 'outro'];
const fmtDate = d => d.toISOString().split('T')[0];
const hoje = () => { const d = new Date(); d.setHours(0,0,0,0); return d; };

function EventCard({ evt, onClick, onDragStart }) {
  const titulo = evt.titulo || evt.escola_nome || evt.tipo;
  return (
    <div
      className={`event-card tipo-${evt.tipo} status-${evt.status} rounded p-2 mb-1 cursor-pointer`}
      style={{ borderLeft: '3px solid', cursor: 'pointer', fontSize: '0.82rem' }}
      draggable onDragStart={onDragStart}
      onClick={onClick}
    >
      <div className="fw-semibold text-truncate">{titulo}</div>
      {(evt.hora_inicio || evt.turno) && (
        <div className="text-muted" style={{ fontSize: '0.73rem' }}>
          <i className="bi bi-clock me-1"></i>{evt.hora_inicio?.slice(0,5) || evt.turno}
        </div>
      )}
    </div>
  );
}

const EMPTY_EVT = { tipo: 'visita', titulo: '', data: '', turno: 'manha', hora_inicio: '', hora_fim: '', escola_id: '', escola_nome: '', local: '', descricao: '', mediador_nome: '', dia_inteiro: false };

export default function Agenda() {
  const [view, setView] = useState('semana');
  const [cur, setCur] = useState(new Date());
  const [data, setData] = useState(null);
  const [eventos, setEventos] = useState([]);
  const [escolas, setEscolas] = useState([]);
  // modal evento
  const [evtForm, setEvtForm] = useState(EMPTY_EVT);
  const [evtId, setEvtId] = useState(null);
  const [evtMsg, setEvtMsg] = useState('');
  const [evtSaving, setEvtSaving] = useState(false);
  const [escolasParaAdd, setEscolasParaAdd] = useState([]);
  // modal ações
  const [acaoEvt, setAcaoEvt] = useState(null);

  const modalEvtRef = useRef();
  const modalAcoesRef = useRef();
  const bsEvt = useRef();
  const bsAcoes = useRef();

  useEffect(() => {
    import('bootstrap/dist/js/bootstrap.bundle.min.js').then(({ Modal }) => {
      if (modalEvtRef.current) bsEvt.current = new Modal(modalEvtRef.current);
      if (modalAcoesRef.current) bsAcoes.current = new Modal(modalAcoesRef.current);
    });
    api.get('/api/escolas').then(r => setEscolas(r.data.escolas || r.data));
  }, []);

  const carregar = useCallback(async () => {
    let url;
    if (view === 'semana') url = `/api/agenda/semana?data=${fmtDate(cur)}`;
    else url = `/api/agenda/mes?ano=${cur.getFullYear()}&mes=${cur.getMonth() + 1}`;
    const r = await api.get(url);
    setData(r.data);
    const evts = [];
    Object.values(r.data.eventos || {}).forEach(arr => evts.push(...arr));
    setEventos(evts);
  }, [view, cur]);

  useEffect(() => { carregar(); }, [carregar]);

  function navAnterior() {
    setCur(d => { const n = new Date(d); view === 'semana' ? n.setDate(n.getDate() - 7) : n.setMonth(n.getMonth() - 1); return n; });
  }
  function navProximo() {
    setCur(d => { const n = new Date(d); view === 'semana' ? n.setDate(n.getDate() + 7) : n.setMonth(n.getMonth() + 1); return n; });
  }

  function titulo() {
    if (!data) return '...';
    if (view === 'semana') {
      const ini = new Date(data.semana_inicio + 'T12:00:00');
      const fim = new Date(data.semana_fim + 'T12:00:00');
      return `${ini.getDate()}/${ini.getMonth()+1} a ${fim.getDate()}/${fim.getMonth()+1}/${fim.getFullYear()}`;
    }
    return `${MESES[data.mes - 1]} ${data.ano}`;
  }

  function abrirNovo(dataStr) {
    setEvtForm({ ...EMPTY_EVT, data: dataStr || fmtDate(new Date()) });
    setEvtId(null); setEvtMsg(''); setEscolasParaAdd([]);
    bsEvt.current?.show();
  }

  function abrirAcoes(id) {
    const e = eventos.find(e => e.id === id);
    if (e) { setAcaoEvt(e); bsAcoes.current?.show(); }
  }

  function editarEvento() {
    bsAcoes.current?.hide();
    setTimeout(() => {
      setEvtForm({ ...EMPTY_EVT, ...acaoEvt, hora_inicio: acaoEvt.hora_inicio?.slice(0,5) || '', hora_fim: acaoEvt.hora_fim?.slice(0,5) || '' });
      setEvtId(acaoEvt.id); setEvtMsg(''); setEscolasParaAdd([]);
      bsEvt.current?.show();
    }, 300);
  }

  const isVisita = t => t === 'visita' || t === 'apresentacao';

  async function salvarEvento() {
    setEvtSaving(true); setEvtMsg('');
    try {
      if (isVisita(evtForm.tipo) && !evtId) {
        if (escolasParaAdd.length === 0) { setEvtMsg('Adicione pelo menos uma escola.'); setEvtSaving(false); return; }
        for (const esc of escolasParaAdd) {
          await api.post('/api/agenda/eventos', { tipo: evtForm.tipo, titulo: esc.escola_nome, data: evtForm.data, turno: esc.turno, escola_id: esc.escola_id, escola_nome: esc.escola_nome, descricao: esc.descricao, mediador_nome: esc.mediador_nome, dia_inteiro: false });
        }
      } else {
        const payload = { ...evtForm, hora_inicio: evtForm.hora_inicio || null, hora_fim: evtForm.hora_fim || null };
        if (evtId) await api.put(`/api/agenda/eventos/${evtId}`, payload);
        else await api.post('/api/agenda/eventos', payload);
      }
      bsEvt.current?.hide();
      await carregar();
    } catch (e) { setEvtMsg(e.response?.data?.erro || 'Erro ao salvar.'); }
    setEvtSaving(false);
  }

  async function marcarExecutado() {
    bsAcoes.current?.hide();
    await api.post(`/api/agenda/eventos/${acaoEvt.id}/executar`);
    await carregar();
  }
  async function cancelarEvento() {
    if (!confirm('Cancelar este evento?')) return;
    bsAcoes.current?.hide();
    await api.post(`/api/agenda/eventos/${acaoEvt.id}/cancelar`);
    await carregar();
  }
  async function removerEvento() {
    if (!confirm('Remover permanentemente?')) return;
    bsAcoes.current?.hide();
    await api.delete(`/api/agenda/eventos/${acaoEvt.id}`);
    await carregar();
  }
  async function duplicarEvento() {
    const novaData = prompt('Data (YYYY-MM-DD):', fmtDate(new Date()));
    if (!novaData) return;
    bsAcoes.current?.hide();
    await api.post(`/api/agenda/eventos/${acaoEvt.id}/duplicar`, { data: novaData });
    await carregar();
  }

  async function onDrop(dataStr, eventoId) {
    await api.put(`/api/agenda/eventos/${eventoId}/mover`, { data: dataStr });
    await carregar();
  }

  // Escolas para adicionar (visitas múltiplas)
  function adicionarEscola() {
    const sel = document.getElementById('ag-escola-sel');
    const turno = document.getElementById('ag-turno-sel')?.value || 'manha';
    const med = document.getElementById('ag-med-inp')?.value || '';
    const obs = document.getElementById('ag-obs-inp')?.value || '';
    if (!sel?.value) { setEvtMsg('Selecione uma escola.'); return; }
    const id = parseInt(sel.value);
    if (escolasParaAdd.some(e => e.escola_id === id)) { setEvtMsg('Escola já adicionada.'); return; }
    const esc = escolas.find(e => e.id === id);
    setEscolasParaAdd(prev => [...prev, { escola_id: id, escola_nome: esc?.nome_usual || esc?.nome_oficial || '', turno, mediador_nome: med, descricao: obs }]);
    sel.value = '';
    setEvtMsg('');
  }

  // Renderização semana
  function renderSemana() {
    if (!data) return null;
    const ini = new Date(data.semana_inicio + 'T12:00:00');
    const hj = hoje();
    return (
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(7, 1fr)', gap: '1px', background: '#e2e8f0' }}>
        {Array.from({ length: 7 }, (_, i) => {
          const dia = new Date(ini); dia.setDate(ini.getDate() + i);
          const ds = fmtDate(dia);
          const isToday = dia.toDateString() === hj.toDateString();
          const isWknd = dia.getDay() === 0 || dia.getDay() === 6;
          const evts = data.eventos[ds] || [];
          return (
            <div key={ds} style={{ background: 'white', minHeight: 300 }}>
              <div className={`text-center py-2 border-bottom ${isToday ? 'bg-primary text-white' : isWknd ? 'bg-danger bg-opacity-10' : 'bg-light'}`}>
                <div style={{ fontSize: '0.75rem', fontWeight: 600, textTransform: 'uppercase' }}>{DIAS[dia.getDay()]}</div>
                <div style={{ fontSize: '1.4rem', fontWeight: 700 }}>{dia.getDate()}</div>
              </div>
              <div className="p-2"
                onDragOver={e => e.preventDefault()}
                onDrop={e => { e.preventDefault(); onDrop(ds, e.dataTransfer.getData('eventoId')); }}
              >
                {evts.map(ev => (
                  <EventCard key={ev.id} evt={ev}
                    onClick={() => abrirAcoes(ev.id)}
                    onDragStart={e => e.dataTransfer.setData('eventoId', ev.id)}
                  />
                ))}
                <button className="btn btn-sm w-100 text-muted" style={{ border: '2px dashed #cbd5e1', background: 'transparent', fontSize: '0.75rem' }} onClick={() => abrirNovo(ds)}>
                  <i className="bi bi-plus"></i>
                </button>
              </div>
            </div>
          );
        })}
      </div>
    );
  }

  // Renderização mês
  function renderMes() {
    if (!data) return null;
    const hj = hoje();
    const primeiroDia = new Date(data.ano, data.mes - 1, 1);
    const diasNoMes = data.total_dias;
    const inicioSemana = primeiroDia.getDay();
    const cells = [];

    DIAS.forEach(d => cells.push(<div key={'h'+d} style={{ background: '#f1f5f9', padding: '0.5rem', textAlign: 'center', fontWeight: 600, fontSize: '0.8rem', color: '#64748b' }}>{d}</div>));

    for (let i = inicioSemana - 1; i >= 0; i--) {
      cells.push(<div key={'prev'+i} style={{ background: '#f8fafc', opacity: 0.5, minHeight: 80, padding: '0.4rem' }}><div style={{ fontWeight: 600, fontSize: '0.85rem', color: '#374151' }}>{new Date(data.ano, data.mes - 2, new Date(data.ano, data.mes - 1, 0).getDate() - i).getDate()}</div></div>);
    }

    for (let d = 1; d <= diasNoMes; d++) {
      const dia = new Date(data.ano, data.mes - 1, d);
      const ds = fmtDate(dia);
      const isToday = dia.toDateString() === hj.toDateString();
      const isWknd = dia.getDay() === 0 || dia.getDay() === 6;
      const evts = data.eventos[ds] || [];
      cells.push(
        <div key={ds} onClick={() => abrirNovo(ds)} style={{ background: isToday ? '#dbeafe' : isWknd ? '#fef2f2' : 'white', minHeight: 80, padding: '0.4rem', cursor: 'pointer' }}>
          <div style={{ fontWeight: 600, fontSize: '0.85rem', color: isWknd ? '#dc2626' : '#374151' }}>{d}</div>
          {evts.slice(0, 3).map(ev => (
            <div key={ev.id} className={`dot-${ev.tipo} rounded`} style={{ padding: '1px 4px', fontSize: '0.7rem', color: 'white', marginBottom: 2, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}
              onClick={e => { e.stopPropagation(); abrirAcoes(ev.id); }}>
              {ev.titulo || ev.escola_nome || ev.tipo}
            </div>
          ))}
          {evts.length > 3 && <div style={{ fontSize: '0.65rem', color: '#64748b' }}>+{evts.length - 3} mais</div>}
        </div>
      );
    }

    const rem = (7 - ((inicioSemana + diasNoMes) % 7)) % 7;
    for (let i = 1; i <= rem; i++) cells.push(<div key={'next'+i} style={{ background: '#f8fafc', opacity: 0.5, minHeight: 80, padding: '0.4rem' }}><div style={{ fontWeight: 600, fontSize: '0.85rem', color: '#374151' }}>{i}</div></div>);

    return <div style={{ display: 'grid', gridTemplateColumns: 'repeat(7, 1fr)', gap: '1px', background: '#e2e8f0' }}>{cells}</div>;
  }

  return (
    <div className="container-fluid">
      <div className="d-flex justify-content-between align-items-center mb-3 flex-wrap gap-2">
        <div>
          <h1 className="page-title"><i className="bi bi-calendar-week me-2"></i>Agenda</h1>
          <p className="text-muted mb-0">Planejamento de visitas e eventos</p>
        </div>
        <div className="d-flex gap-2">
          <button className="btn btn-outline-secondary btn-sm" onClick={() => setCur(new Date())}>Hoje</button>
          <button className="btn btn-primary btn-sm" onClick={() => abrirNovo()}>
            <i className="bi bi-plus-circle me-1"></i>Novo Evento
          </button>
        </div>
      </div>

      <div className="card overflow-hidden">
        {/* Header */}
        <div className="d-flex justify-content-between align-items-center p-3 text-white" style={{ background: 'linear-gradient(135deg, #1e40af, #3b82f6)' }}>
          <div className="d-flex gap-1">
            <button className="btn btn-sm" style={{ background: 'rgba(255,255,255,0.2)', color: 'white', border: 'none' }} onClick={navAnterior}><i className="bi bi-chevron-left"></i></button>
            <button className="btn btn-sm" style={{ background: 'rgba(255,255,255,0.2)', color: 'white', border: 'none' }} onClick={navProximo}><i className="bi bi-chevron-right"></i></button>
          </div>
          <h5 className="mb-0 fw-bold">{titulo()}</h5>
          <div className="btn-group btn-group-sm">
            <button className={`btn ${view === 'semana' ? 'btn-light' : ''}`} style={view !== 'semana' ? { background: 'rgba(255,255,255,0.15)', border: '1px solid rgba(255,255,255,0.3)', color: 'white' } : { color: '#1e40af' }} onClick={() => setView('semana')}>Semana</button>
            <button className={`btn ${view === 'mes' ? 'btn-light' : ''}`} style={view !== 'mes' ? { background: 'rgba(255,255,255,0.15)', border: '1px solid rgba(255,255,255,0.3)', color: 'white' } : { color: '#1e40af' }} onClick={() => setView('mes')}>Mês</button>
          </div>
        </div>

        {/* Stats */}
        <div className="d-flex gap-4 px-3 py-2 border-bottom flex-wrap">
          {[['Total', eventos.length, ''], ['Visitas', eventos.filter(e=>e.tipo==='visita').length, 'text-warning'], ['Reuniões', eventos.filter(e=>e.tipo==='reuniao').length, 'text-primary'], ['Feriados', eventos.filter(e=>e.tipo==='feriado').length, 'text-danger']].map(([l, v, c]) => (
            <div key={l} className="d-flex align-items-center gap-1">
              <span className={`fw-bold fs-5 ${c}`}>{v}</span>
              <span className="text-muted small">{l}</span>
            </div>
          ))}
        </div>

        {/* Grid */}
        <div>{!data ? <div className="text-center py-4"><div className="spinner-border text-primary"></div></div> : view === 'semana' ? renderSemana() : renderMes()}</div>

        {/* Legenda */}
        <div className="d-flex gap-3 px-3 py-2 border-top flex-wrap" style={{ background: '#f8fafc' }}>
          {TIPOS.map(t => (
            <div key={t} className="d-flex align-items-center gap-1" style={{ fontSize: '0.75rem', color: '#64748b' }}>
              <div className={`dot-${t} rounded`} style={{ width: 10, height: 10 }}></div>
              {t.charAt(0).toUpperCase() + t.slice(1)}
            </div>
          ))}
        </div>
      </div>

      {/* Modal Novo/Editar Evento */}
      <div className="modal fade" ref={modalEvtRef} tabIndex="-1">
        <div className="modal-dialog modal-lg">
          <div className="modal-content">
            <div className="modal-header">
              <h5 className="modal-title"><i className="bi bi-calendar-plus me-2"></i>{evtId ? 'Editar Evento' : 'Novo Evento'}</h5>
              <button type="button" className="btn-close" data-bs-dismiss="modal"></button>
            </div>
            <div className="modal-body">
              {evtMsg && <div className="alert alert-warning py-2">{evtMsg}</div>}
              <div className="row g-3 mb-3">
                <div className="col-md-6">
                  <label className="form-label">Tipo</label>
                  <select className="form-select" value={evtForm.tipo} onChange={e => setEvtForm(f => ({ ...f, tipo: e.target.value }))}>
                    <option value="visita">Visita à Escola</option>
                    <option value="reuniao">Reunião</option>
                    <option value="apresentacao">Apresentação</option>
                    <option value="capacitacao">Capacitação</option>
                    <option value="planejamento">Planejamento</option>
                    <option value="relatorio">Relatório</option>
                    <option value="feriado">Feriado</option>
                    <option value="outro">Outro</option>
                  </select>
                </div>
                <div className="col-md-6">
                  <label className="form-label">Data</label>
                  <input type="date" className="form-control" value={evtForm.data} onChange={e => setEvtForm(f => ({ ...f, data: e.target.value }))} />
                </div>
              </div>

              {/* Seção visitas (múltiplas escolas) */}
              {isVisita(evtForm.tipo) && !evtId ? (
                <div>
                  {escolasParaAdd.length > 0 && (
                    <div className="mb-3">
                      <label className="form-label">Escolas adicionadas</label>
                      {escolasParaAdd.map((e, i) => (
                        <div key={i} className="d-flex align-items-center justify-content-between p-2 mb-1 bg-light border rounded">
                          <div><strong>{e.escola_nome}</strong> <span className="badge bg-secondary ms-2">{e.turno}</span></div>
                          <button type="button" className="btn btn-sm btn-outline-danger" onClick={() => setEscolasParaAdd(prev => prev.filter((_, j) => j !== i))}><i className="bi bi-x"></i></button>
                        </div>
                      ))}
                    </div>
                  )}
                  <div className="card bg-light">
                    <div className="card-body">
                      <h6 className="card-title"><i className="bi bi-plus-circle me-1"></i>Adicionar Escola</h6>
                      <div className="row g-2 mb-2">
                        <div className="col-md-6">
                          <select className="form-select form-select-sm" id="ag-escola-sel">
                            <option value="">Selecione...</option>
                            {escolas.map(e => <option key={e.id} value={e.id}>{e.nome_usual || e.nome_oficial}</option>)}
                          </select>
                        </div>
                        <div className="col-md-3">
                          <select className="form-select form-select-sm" id="ag-turno-sel">
                            <option value="manha">Manhã</option>
                            <option value="tarde">Tarde</option>
                            <option value="integral">Integral</option>
                          </select>
                        </div>
                        <div className="col-md-3">
                          <input type="text" className="form-control form-control-sm" id="ag-med-inp" placeholder="Responsável" />
                        </div>
                      </div>
                      <div className="d-flex justify-content-end">
                        <button type="button" className="btn btn-sm btn-primary" onClick={adicionarEscola}><i className="bi bi-plus me-1"></i>Adicionar</button>
                      </div>
                    </div>
                  </div>
                </div>
              ) : (
                /* Formulário simples para outros tipos */
                <div className="row g-3">
                  {!isVisita(evtForm.tipo) && (
                    <div className="col-12">
                      <label className="form-label">Título</label>
                      <input className="form-control" value={evtForm.titulo} onChange={e => setEvtForm(f => ({ ...f, titulo: e.target.value }))} />
                    </div>
                  )}
                  {isVisita(evtForm.tipo) && evtId && (
                    <div className="col-md-8">
                      <label className="form-label">Escola</label>
                      <select className="form-select" value={evtForm.escola_id} onChange={e => { const esc = escolas.find(s => String(s.id) === e.target.value); setEvtForm(f => ({ ...f, escola_id: e.target.value, escola_nome: esc?.nome_usual || '' })); }}>
                        <option value="">Selecione...</option>
                        {escolas.map(e => <option key={e.id} value={e.id}>{e.nome_usual || e.nome_oficial}</option>)}
                      </select>
                    </div>
                  )}
                  <div className="col-md-4">
                    <label className="form-label">Turno</label>
                    <select className="form-select" value={evtForm.turno} onChange={e => setEvtForm(f => ({ ...f, turno: e.target.value }))}>
                      <option value="manha">Manhã</option>
                      <option value="tarde">Tarde</option>
                      <option value="integral">Integral</option>
                    </select>
                  </div>
                  {['reuniao', 'capacitacao'].includes(evtForm.tipo) && (
                    <>
                      <div className="col-md-6"><label className="form-label">Local</label><input className="form-control" value={evtForm.local} onChange={e => setEvtForm(f => ({ ...f, local: e.target.value }))} /></div>
                      <div className="col-md-3"><label className="form-label">Início</label><input type="time" className="form-control" value={evtForm.hora_inicio} onChange={e => setEvtForm(f => ({ ...f, hora_inicio: e.target.value }))} /></div>
                      <div className="col-md-3"><label className="form-label">Fim</label><input type="time" className="form-control" value={evtForm.hora_fim} onChange={e => setEvtForm(f => ({ ...f, hora_fim: e.target.value }))} /></div>
                    </>
                  )}
                  <div className="col-md-6"><label className="form-label">Responsável</label><input className="form-control" value={evtForm.mediador_nome} onChange={e => setEvtForm(f => ({ ...f, mediador_nome: e.target.value }))} /></div>
                  <div className="col-12"><label className="form-label">Descrição</label><textarea className="form-control" rows={2} value={evtForm.descricao} onChange={e => setEvtForm(f => ({ ...f, descricao: e.target.value }))} /></div>
                </div>
              )}
            </div>
            <div className="modal-footer">
              <button className="btn btn-secondary" data-bs-dismiss="modal">Cancelar</button>
              <button className="btn btn-primary" onClick={salvarEvento} disabled={evtSaving}>
                {evtSaving ? <span className="spinner-border spinner-border-sm me-1" /> : <i className="bi bi-check-circle me-1" />}Salvar
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Modal Ações */}
      <div className="modal fade" ref={modalAcoesRef} tabIndex="-1">
        <div className="modal-dialog modal-sm">
          <div className="modal-content">
            <div className="modal-header">
              <h5 className="modal-title text-truncate">{acaoEvt?.titulo || acaoEvt?.escola_nome || acaoEvt?.tipo}</h5>
              <button type="button" className="btn-close" data-bs-dismiss="modal"></button>
            </div>
            <div className="modal-body">
              <div className="d-grid gap-2">
                <button className="btn btn-outline-primary" onClick={editarEvento}><i className="bi bi-pencil me-1"></i>Editar</button>
                <button className="btn btn-success" onClick={marcarExecutado}><i className="bi bi-check-circle me-1"></i>Marcar Executado</button>
                <button className="btn btn-outline-warning" onClick={cancelarEvento}><i className="bi bi-x-circle me-1"></i>Cancelar Evento</button>
                <button className="btn btn-outline-info" onClick={duplicarEvento}><i className="bi bi-copy me-1"></i>Duplicar</button>
                <hr className="my-1" />
                <button className="btn btn-outline-danger" onClick={removerEvento}><i className="bi bi-trash me-1"></i>Remover</button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
