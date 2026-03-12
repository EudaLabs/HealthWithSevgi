import axios from 'axios'

export const api = axios.create({
  baseURL: '/api',
  timeout: 120_000,
})

api.interceptors.response.use(
  (res) => res,
  (err) => {
    const detail = err.response?.data?.detail
    const message =
      typeof detail === 'string'
        ? detail
        : Array.isArray(detail)
          ? detail.map((d: { msg: string }) => d.msg).join(', ')
          : err.message || 'An unexpected error occurred'
    return Promise.reject(new Error(message))
  }
)
