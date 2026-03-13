import axios from 'axios';

function getCsrf() {
  const c = document.cookie.split(';').find(c => c.trim().startsWith('csrftoken='));
  return c ? decodeURIComponent(c.trim().slice('csrftoken='.length)) : '';
}

const api = axios.create({ withCredentials: true });

api.interceptors.request.use(cfg => {
  if (['post', 'put', 'patch', 'delete'].includes(cfg.method?.toLowerCase())) {
    cfg.headers['X-CSRFToken'] = getCsrf();
  }
  return cfg;
});

export default api;
