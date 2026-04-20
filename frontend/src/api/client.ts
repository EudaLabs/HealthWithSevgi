import axios from 'axios'

/**
 * Shared Axios instance for every backend call in the wizard.
 *
 * - `baseURL: '/api'` is proxied to the FastAPI server by Vite in dev and served
 *   directly from the same origin by `main_hf.py` in the HuggingFace build.
 * - `timeout: 120s` is generous on purpose: SHAP explainability and certificate
 *   generation on large datasets can cross 60s.
 *
 * The response interceptor normalises FastAPI validation errors (where
 * `response.data.detail` is an array of `{msg}` objects) into a single-string
 * `Error.message`, so UI code can always do `catch (e) { toast(e.message) }`
 * without worrying about DRF vs Pydantic shapes.
 */
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
