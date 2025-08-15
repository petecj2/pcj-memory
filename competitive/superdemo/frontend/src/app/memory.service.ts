import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface QueryRequest {
  user_id: string;
  query: string;
}

export interface QueryResponse {
  response: string;
  memory_saved: boolean;
  context_found: boolean;
  retrieved_memory: string[] | null;
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