import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface QueryRequest {
  user_id: string;
  query: string;
}

export interface PerformanceMetrics {
  user_setup_time_ms?: number;  // Optional, only for Zep
  thread_create_time_ms?: number;  // Optional, only for Zep
  search_time_ms: number;
  chain_invoke_time_ms: number;
  add_time_ms: number;
  total_time_ms: number;
}

export interface QueryResponse {
  response: string;
  memory_saved: boolean;
  context_found: boolean;
  retrieved_memory: string[] | null;
  performance_metrics?: PerformanceMetrics;
}

@Injectable({
  providedIn: 'root'
})
export class MemoryService {
  private baseUrl = 'http://localhost:8000';

  constructor(private http: HttpClient) { }

  queryMem0(request: QueryRequest): Observable<QueryResponse> {
    return this.http.post<QueryResponse>(`${this.baseUrl}/mem0/query`, request);
  }

  queryZep(request: QueryRequest): Observable<QueryResponse> {
    return this.http.post<QueryResponse>(`${this.baseUrl}/zep/query`, request);
  }
}