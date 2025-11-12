import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

export const api = {
  getExperiments: () => apiClient.get('/api/experiments').then(res => res.data),
  getRunningExperiments: () => apiClient.get('/api/experiments/running').then(res => res.data),
  runExperiment: (name: string, namespace?: string) =>
    apiClient.post('/api/experiments/run', { name, namespace }).then(res => res.data),
  stopExperiment: (name: string, namespace?: string) =>
    apiClient.post(`/api/experiments/${name}/stop`, null, { params: { namespace } }).then(res => res.data),
  getExperimentStatus: (name: string, namespace?: string) =>
    apiClient.get(`/api/experiments/${name}/status`, { params: { namespace } }).then(res => res.data),
  getSchedules: () => apiClient.get('/api/schedules').then(res => res.data),
  createSchedule: (experiment: string, schedule: string, namespace?: string) =>
    apiClient.post('/api/schedules', { experiment, schedule, namespace }).then(res => res.data),
  deleteSchedule: (experiment: string) =>
    apiClient.delete(`/api/schedules/${experiment}`).then(res => res.data),
}
