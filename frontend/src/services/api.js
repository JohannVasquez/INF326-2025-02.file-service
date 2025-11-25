import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || '/gateway';
const isBrowser = typeof window !== 'undefined';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
});

export const setAuthToken = (token) => {
  if (token) {
    api.defaults.headers.common.Authorization = `Bearer ${token}`;
    if (isBrowser) {
      localStorage.setItem('gatewayToken', token);
    }
  } else {
    delete api.defaults.headers.common.Authorization;
    if (isBrowser) {
      localStorage.removeItem('gatewayToken');
    }
  }
};

if (isBrowser) {
  const storedToken = localStorage.getItem('gatewayToken');
  if (storedToken) {
    setAuthToken(storedToken);
  }
}

// Users
export const usersAPI = {
  me: () => api.get('/users/me'),
  get: (id) => api.get(`/users/${id}`),
  getByUsername: (username) => api.get(`/users/username/${username}`),
  create: (data) => api.post('/users', data),
  update: (id, data) => api.put(`/users/${id}`, data),
  delete: (id) => api.delete(`/users/${id}`),
  login: (credentials) => api.post('/users/auth/login', credentials),
  health: () => api.get('/users/health'),
};

// Channels
export const channelsAPI = {
  list: (params = {}) => api.get('/channels', { params }),
  listByOwner: (ownerId) => api.get(`/channels/owner/${ownerId}`),
  listByMember: (userId) => api.get(`/channels/member/${userId}`),
  get: (id) => api.get(`/channels/${id}`),
  create: (data) => api.post('/channels', data), // data = { name, owner_id, users, channel_type }
  update: (id, data) => api.put(`/channels/${id}`, data),
  delete: (id) => api.delete(`/channels/${id}`),
};

// Messages - API basada en threads
export const messagesAPI = {
  list: (threadId, params = {}) => api.get(`/messages/threads/${threadId}`, { params }),
  get: (threadId, messageId) => api.get(`/messages/threads/${threadId}/messages/${messageId}`),
  create: (threadId, data, userId) => api.post(`/messages/threads/${threadId}`, { ...data, user_id: userId }),
  update: (threadId, messageId, data, userId) => api.put(
    `/messages/threads/${threadId}/messages/${messageId}`,
    { ...data, user_id: userId }
  ),
  delete: (threadId, messageId, userId) => api.delete(
    `/messages/threads/${threadId}/messages/${messageId}`,
    { params: { user_id: userId } }
  ),
};

// Files
export const filesAPI = {
  list: (params = {}) => api.get('/files', { params }),
  get: (id) => api.get(`/files/${id}`),
  upload: (formData) => api.post('/files', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  }),
  delete: (id) => api.delete(`/files/${id}`),
  getDownloadUrl: (id) => api.post(`/files/${id}/download-url`),
};

// Search
export const searchAPI = {
  global: (query, params = {}) => api.get('/search', {
    params: { q: query, ...params },
  }),
  searchMessages: (query, params = {}) => api.get('/search/messages', {
    params: { q: query, ...params },
  }),
  searchFiles: (query, params = {}) => api.get('/search/files', {
    params: { q: query, ...params },
  }),
  searchChannels: (query, params = {}) => api.get('/search/channels', {
    params: { q: query, ...params },
  }),
};

// Moderation
export const moderationAPI = {
  check: (data) => api.post('/moderation/check', data),
  analyze: (text) => api.post('/moderation/analyze', { text }),
  getUserStatus: (userId, channelId) => api.get(`/moderation/status/${userId}/${channelId}`),
  listBanned: () => api.get('/moderation/banned-users'),
  listBlacklist: () => api.get('/moderation/blacklist/words'),
};

// Threads
export const threadsAPI = {
  listByChannel: (channelId) => api.get(`/threads/channel/${channelId}`),
  listMine: (userId) => api.get(`/threads/mine/${userId}`),
  get: (threadId) => api.get(`/threads/${threadId}`),
  create: (data) => api.post('/threads', data),
  update: (threadId, data) => api.put(`/threads/${threadId}`, data),
};

// Presence
export const presenceAPI = {
  list: (status) => api.get('/presence', { params: status ? { status } : {} }),
  stats: () => api.get('/presence/stats'),
  get: (userId) => api.get(`/presence/${userId}`),
  register: (payload) => api.post('/presence', payload),
  update: (userId, payload) => api.patch(`/presence/${userId}`, payload),
  remove: (userId) => api.delete(`/presence/${userId}`),
};

// Chatbots
export const wikiAPI = {
  ask: (message) => api.post('/chat/wiki', { message }),
};

export const programmingChatAPI = {
  ask: (message) => api.post('/chat/programming', { message }),
};

export default api;
