import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || '/gateway';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
});

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
  listByOwner: (ownerId) => api.get(`/channels/owner/${ownerId}`),
  get: (id) => api.get(`/channels/${id}`),
  create: (data) => api.post('/channels', data), // data = { name, owner_id, users, channel_type }
  update: (id, data) => api.put(`/channels/${id}`, data),
  delete: (id) => api.delete(`/channels/${id}`),
};

// Messages - API basada en threads
export const messagesAPI = {
  list: (threadId, params = {}) => api.get(`/messages/threads/${threadId}`, { params }),
  get: (threadId, messageId) => api.get(`/messages/threads/${threadId}/messages/${messageId}`),
  create: (threadId, data) => api.post(`/messages/threads/${threadId}`, data),
  update: (threadId, messageId, data) => api.put(`/messages/threads/${threadId}/messages/${messageId}`, data),
  delete: (threadId, messageId) => api.delete(`/messages/threads/${threadId}/messages/${messageId}`),
};

// Files
export const filesAPI = {
  list: (params) => api.get('/files', { params }),
  get: (id) => api.get(`/files/${id}`),
  upload: (formData) => api.post('/files', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  }),
  delete: (id) => api.delete(`/files/${id}`),
  getDownloadUrl: (id) => api.post(`/files/${id}/download-url`),
};

// Search
export const searchAPI = {
  search: (query, channelId) => api.get('/search', { 
    params: { q: query, channel_id: channelId } 
  }),
  searchMessages: (query, channelId) => api.get('/search/messages', { 
    params: { q: query, channel_id: channelId } 
  }),
  searchFiles: (query) => api.get('/search/files', { 
    params: { q: query } 
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

export default api;
