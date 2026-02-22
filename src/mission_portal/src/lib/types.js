// src/lib/types.ts
export interface LogEntry {
  stage: 'BRONZE' | 'SILVER' | 'VAULT' | 'MOCK';
  msg: string;
  latency: number;
}
