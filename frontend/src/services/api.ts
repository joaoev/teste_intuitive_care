import axios from "axios";

export interface Operadora {
  CNPJ: string;
  RazaoSocial: string;
  RegistroANS: string;
  UF?: string;
  TotalDespesas?: number;
}

export interface DespesaHistorico {
  Ano: number;
  Trimestre: number;
  ValorDespesas: number;
}

export interface PaginatedResponse<T> {
  data: T[];
  total: number;
  page: number;
  limit: number;
}

export interface OperadorasParams {
  page: number;
  limit: number;
  search?: string;
}

const api = axios.create({
  baseURL: "http://localhost:8000",
  timeout: 10000,
});

export async function getOperadoras(params: OperadorasParams): Promise<PaginatedResponse<Operadora>> {
  const { data } = await api.get<PaginatedResponse<Operadora>>("/api/operadoras", { params });
  return data;
}

export async function getOperadora(cnpj: string): Promise<Operadora> {
  const { data } = await api.get<Operadora>(`/api/operadoras/${cnpj}`);
  return data;
}

export async function getDespesas(cnpj: string): Promise<{ data: DespesaHistorico[] }> {
  const { data } = await api.get<{ data: DespesaHistorico[] }>(`/api/operadoras/${cnpj}/despesas`);
  return data;
}

export async function getEstatisticas(): Promise<unknown> {
  const { data } = await api.get("/api/estatisticas");
  return data;
}
