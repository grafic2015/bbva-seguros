// Manejo del token de autenticación en el frontend.

const KEY = "bbva_token";

export const getToken = (): string => localStorage.getItem(KEY) || "";
export const setToken = (t: string): void => localStorage.setItem(KEY, t);
export const clearToken = (): void => localStorage.removeItem(KEY);

const API = import.meta.env.VITE_API_URL || "";

/**
 * Parchea window.fetch para agregar el header Authorization en los pedidos al
 * API y, ante un 401, limpiar el token y volver al login.
 * Se llama una sola vez al iniciar la app.
 */
export function installAuthFetch(): void {
  const original = window.fetch.bind(window);

  window.fetch = async (input: RequestInfo | URL, init: RequestInit = {}) => {
    const url = typeof input === "string" ? input : (input as Request).url || String(input);
    const isApi = url.includes("/api/") || (!!API && url.startsWith(API));
    const isLogin = url.includes("/api/login");

    const token = getToken();
    if (isApi && token && !isLogin) {
      init = {
        ...init,
        headers: { ...(init.headers || {}), Authorization: `Bearer ${token}` },
      };
    }

    const res = await original(input, init);

    // Sesión inválida/expirada: limpiar y recargar (vuelve al login).
    if (res.status === 401 && !isLogin) {
      clearToken();
      location.reload();
    }
    return res;
  };
}
