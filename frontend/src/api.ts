const BASE = import.meta.env.VITE_API_BASE_URL ?? "/api";

async function getJson<T>(path: string): Promise<T> {
  const r = await fetch(`${BASE}${path}`);
  if (!r.ok) throw new Error(`API ${r.status}`);
  return r.json() as Promise<T>;
}

export const api = {
  serials: (date: string) =>
    getJson<{serials:string[]}>(`/serials?date=${encodeURIComponent(date)}`),

  equipment: (serial: string, axis: number) =>
    getJson<any>(`/cycle/${encodeURIComponent(serial)}/equipment?axis=${axis}`),

  measurement: (serial: string) =>
    getJson<any>(`/cycle/${encodeURIComponent(serial)}/measurement`),

  changes: (serial: string) =>
    getJson<any>(`/cycle/${encodeURIComponent(serial)}/changes`),

  trace: (serial: string) =>
    getJson<any>(`/cycle/${encodeURIComponent(serial)}/traceability`),

  period: (start: string, end: string, machine: string, axis: number) =>
    getJson<any>(`/period/dashboard?start=${start}&end=${end}&machine=${machine}&axis=${axis}`)
};
