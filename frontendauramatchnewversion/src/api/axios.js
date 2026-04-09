import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  headers: { 'Content-Type': 'application/json' },
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

// Favorites API
export const favoritesApi = {
  getIds: () => api.get('/favorites/ids'),
  add: (productId) => api.post(`/favorites/${productId}`),
  remove: (productId) => api.delete(`/favorites/${productId}`),
  getAll: () => api.get('/favorites/'),
}

// Skin Concerns API
export const skinConcernsApi = {
  getAll: () => api.get('/skin-concerns/'),
  getMine: () => api.get('/skin-concerns/me'),
  updateMine: (concerns) => api.put('/skin-concerns/me', { concerns }),
}

// Reviews API
export const reviewsApi = {
  getForProduct: (productId) => api.get(`/reviews/${productId}`),
  getSummary: (productId) => api.get(`/reviews/${productId}/summary`),
  submit: (productId, data) => api.post(`/reviews/${productId}`, data),
  remove: (productId) => api.delete(`/reviews/${productId}`),
}

// Blog API
export const blogApi = {
  getCategories: () => api.get('/blog/categories'),
  getPosts: (params) => api.get('/blog/posts', { params }),
  getPost: (slug) => api.get(`/blog/posts/${slug}`),
  trackView: (slug) => api.patch(`/blog/posts/${slug}/view`),
  // Admin
  adminGetPosts: (params) => api.get('/blog/admin/posts', { params }),
  adminCreatePost: (data) => api.post('/blog/admin/posts', data),
  adminUpdatePost: (id, data) => api.put(`/blog/admin/posts/${id}`, data),
  adminDeletePost: (id) => api.delete(`/blog/admin/posts/${id}`),
  adminCreateCategory: (data) => api.post('/blog/admin/categories', data),
  adminUpdateCategory: (id, data) => api.put(`/blog/admin/categories/${id}`, data),
  adminDeleteCategory: (id) => api.delete(`/blog/admin/categories/${id}`),
}

// Analytics API (admin)
export const analyticsApi = {
  getSummary:        (days = 30) => api.get('/behavior/analytics/summary', { params: { days } }),
  getTopProducts:    (days = 30, limit = 10) => api.get('/behavior/analytics/top-products', { params: { days, limit } }),
  getTopSearches:    (days = 30, limit = 20) => api.get('/behavior/analytics/top-searches', { params: { days, limit } }),
  getFilterUsage:    (days = 30) => api.get('/behavior/analytics/filter-usage', { params: { days } }),
  getMakeupBehavior: (days = 30) => api.get('/behavior/analytics/makeup-behavior', { params: { days } }),
  getPersonalColor:  (days = 30) => api.get('/behavior/analytics/personal-color-demand', { params: { days } }),
  getClickFunnel:    (days = 30) => api.get('/behavior/analytics/click-funnel', { params: { days } }),
}

// Banner API
export const bannerApi = {
  getActive: (position) => api.get('/banner/active', { params: position ? { position } : {} }),
  adminGetList: (params) => api.get('/banner/admin/list', { params }),
  adminCreate: (formData) => api.post('/banner/admin', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  }),
  adminUpdate: (id, formData) => api.put(`/banner/admin/${id}`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  }),
  adminDelete: (id) => api.delete(`/banner/admin/${id}`),
  adminToggle: (id) => api.patch(`/banner/admin/${id}/toggle`),
}

export default api
