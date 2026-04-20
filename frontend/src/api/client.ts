import axios from 'axios'

/**
 * Shared Axios instance for every backend call in the wizard.
 *
 * - `baseURL: '/api'` is proxied to the FastAPI server by Vite in dev and served
 *   directly from the same origin by `main_hf.py` in the HuggingFace build.
 * - `timeout: 450s` is generous on purpose: Step-7 AI insights trigger three
 *   parallel Gemma-4 reasoning calls that can each need up to 200s plus one
 *   retry, and SHAP/certificate generation on large datasets can still cross
 *   60s.
 *
 * The response interceptor normalises FastAPI validation errors (where
 * `response.data.detail` is an array of `{msg}` objects) into a single-string
 * `Error.message`, so UI code can always do `catch (e) { toast(e.message) }`
 * without worrying about DRF vs Pydantic shapes.
 */
export const api = axios.create({
  baseURL: '/api',
  timeout: 450_000,
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
