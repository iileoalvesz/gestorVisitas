import { useEffect, useState, useRef } from 'react';
import api from '../api';

export default function Mapa() {
  const [escolas, setEscolas] = useState([]);
  const [loading, setLoading] = useState(true);
  const mapRef = useRef(null);
  const leafletMap = useRef(null);

  useEffect(() => {
    api.get('/api/escolas').then(r => {
      setEscolas((r.data.escolas || r.data).filter(e => e.latitude && e.longitude));
      setLoading(false);
    });
  }, []);

  useEffect(() => {
    if (loading || !mapRef.current) return;
    if (leafletMap.current) return;

    import('leaflet').then(L => {
      import('leaflet/dist/leaflet.css');

      // Fix marker icons
      delete L.Icon.Default.prototype._getIconUrl;
      L.Icon.Default.mergeOptions({
        iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
        iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
        shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
      });

      const map = L.map(mapRef.current).setView([-23.0, -45.55], 12);
      leafletMap.current = map;

      L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors'
      }).addTo(map);

      escolas.forEach(e => {
        const popup = `<strong>${e.nome_usual || e.nome_oficial}</strong><br/>${e.endereco || ''}${e.diretor ? `<br/>Dir: ${e.diretor}` : ''}`;
        L.marker([e.latitude, e.longitude]).addTo(map).bindPopup(popup);
      });

      if (escolas.length > 0) {
        const bounds = L.latLngBounds(escolas.map(e => [e.latitude, e.longitude]));
        map.fitBounds(bounds, { padding: [40, 40] });
      }
    });

    return () => {
      if (leafletMap.current) { leafletMap.current.remove(); leafletMap.current = null; }
    };
  }, [loading, escolas]);

  return (
    <div className="container-fluid">
      <div className="mb-3">
        <h1 className="page-title"><i className="bi bi-map me-2"></i>Mapa de Escolas</h1>
        <p className="text-muted mb-0">{escolas.length} escolas com localização definida</p>
      </div>
      {loading ? (
        <div className="text-center py-5"><div className="spinner-border text-primary"></div></div>
      ) : (
        <div className="card">
          <div className="card-body p-0" style={{ height: '70vh' }} ref={mapRef}></div>
        </div>
      )}
    </div>
  );
}
