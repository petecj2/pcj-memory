import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { HttpClientModule } from '@angular/common/http';
import { MemoryService, QueryRequest, QueryResponse, PerformanceMetrics } from './memory.service';
import { forkJoin } from 'rxjs';

export interface ConversationItem {
  query: string;
  response: string;
  retrievedMemory: string[] | null;
  timestamp: Date;
  performanceMetrics?: PerformanceMetrics;
}

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [CommonModule, FormsModule, HttpClientModule],
  template: `
    <div class="container">
      <div class="header">
        <h1>Memory Systems Comparison</h1>
        <p>Compare Mem0 and Zep memory retrieval systems</p>
      </div>

      <div class="input-section">
        <div class="input-group">
          <label for="userId">User ID:</label>
          <input 
            id="userId"
            type="text" 
            [(ngModel)]="userId" 
            placeholder="Enter user ID"
            [disabled]="isLoading">
        </div>
        
        <div class="input-group">
          <label for="query">Query:</label>
          <input 
            id="query"
            type="text" 
            [(ngModel)]="query" 
            placeholder="Enter your query"
            [disabled]="isLoading"
            (keyup.enter)="submitQuery()">
        </div>
        
        <button 
          class="submit-btn" 
          (click)="submitQuery()" 
          [disabled]="!userId || !query || isLoading">
          {{ isLoading ? 'Processing...' : 'Submit Query' }}
        </button>
      </div>

      <div *ngIf="error" class="error">
        {{ error }}
      </div>

      <div class="results-container">
        <div class="memory-column">
          <div class="system-header">
            <img src="assets/mem0-logo-light.svg" alt="Mem0" class="system-logo">
          </div>
          <div *ngIf="isLoading && mem0Conversation.length === 0" class="loading">
            Loading Mem0 response...
          </div>
          <div *ngIf="isLoading && mem0Conversation.length > 0" class="processing-indicator">
            <div class="spinner"></div>
            <span>Processing new query...</span>
          </div>
          <div *ngFor="let item of mem0Conversation; trackBy: trackByTimestamp" class="conversation-item">
            <div class="query"><strong>Q:</strong> {{ item.query }}</div>
            <div class="response"><strong>A:</strong> {{ item.response }}</div>
            <div *ngIf="item.retrievedMemory && item.retrievedMemory.length > 0" class="memory">
              <strong>Retrieved Memory:</strong>
              <ul>
                <li *ngFor="let memory of item.retrievedMemory">{{ memory }}</li>
              </ul>
            </div>
            <div *ngIf="!item.retrievedMemory || item.retrievedMemory.length === 0" class="memory">
              <strong>Retrieved Memory:</strong> <em>No previous memory found</em>
            </div>
            <div *ngIf="item.performanceMetrics" class="performance-metrics">
              <strong>Performance:</strong>
              <ul class="metrics-list">
                <li>Search: {{ item.performanceMetrics.search_time_ms.toFixed(1) }}ms</li>
                <li>LLM: {{ item.performanceMetrics.chain_invoke_time_ms.toFixed(1) }}ms</li>
                <li>Save: {{ item.performanceMetrics.add_time_ms.toFixed(1) }}ms</li>
                <li class="total">Total: {{ item.performanceMetrics.total_time_ms.toFixed(1) }}ms</li>
              </ul>
            </div>
          </div>
          <div *ngIf="!isLoading && mem0Conversation.length === 0" class="loading">
            No conversations yet. Enter a query to start.
          </div>
        </div>

        <div class="memory-column">
          <div class="system-header">
            <img src="assets/zep-logo.svg" alt="Zep" class="system-logo">
          </div>
          <div *ngIf="isLoading && zepConversation.length === 0" class="loading">
            Loading Zep response...
          </div>
          <div *ngIf="isLoading && zepConversation.length > 0" class="processing-indicator">
            <div class="spinner"></div>
            <span>Processing new query...</span>
          </div>
          <div *ngFor="let item of zepConversation; trackBy: trackByTimestamp" class="conversation-item">
            <div class="query"><strong>Q:</strong> {{ item.query }}</div>
            <div class="response"><strong>A:</strong> {{ item.response }}</div>
            <div *ngIf="item.retrievedMemory && item.retrievedMemory.length > 0" class="memory">
              <strong>Retrieved Memory:</strong>
              <ul>
                <li *ngFor="let memory of item.retrievedMemory">{{ memory }}</li>
              </ul>
            </div>
            <div *ngIf="!item.retrievedMemory || item.retrievedMemory.length === 0" class="memory">
              <strong>Retrieved Memory:</strong> <em>No previous memory found</em>
            </div>
            <div *ngIf="item.performanceMetrics" class="performance-metrics">
              <strong>Performance:</strong>
              <ul class="metrics-list">
                <li *ngIf="item.performanceMetrics.user_setup_time_ms !== undefined">User Setup: {{ item.performanceMetrics.user_setup_time_ms.toFixed(1) }}ms</li>
                <li *ngIf="item.performanceMetrics.thread_create_time_ms !== undefined">Thread Creation: {{ item.performanceMetrics.thread_create_time_ms.toFixed(1) }}ms</li>
                <li>Search: {{ item.performanceMetrics.search_time_ms.toFixed(1) }}ms</li>
                <li>LLM: {{ item.performanceMetrics.chain_invoke_time_ms.toFixed(1) }}ms</li>
                <li>Save: {{ item.performanceMetrics.add_time_ms.toFixed(1) }}ms</li>
                <li class="total">Total: {{ item.performanceMetrics.total_time_ms.toFixed(1) }}ms</li>
              </ul>
            </div>
          </div>
          <div *ngIf="!isLoading && zepConversation.length === 0" class="loading">
            No conversations yet. Enter a query to start.
          </div>
        </div>
      </div>
    </div>
  `,
  styles: []
})
export class AppComponent {
  userId: string = 'demo_user_123';
  query: string = '';
  isLoading: boolean = false;
  error: string = '';
  
  zepConversation: ConversationItem[] = [];
  mem0Conversation: ConversationItem[] = [];

  constructor(private memoryService: MemoryService) {}

  submitQuery() {
    if (!this.userId || !this.query || this.isLoading) {
      return;
    }

    this.isLoading = true;
    this.error = '';
    
    const request: QueryRequest = {
      user_id: this.userId,
      query: this.query
    };

    const currentQuery = this.query;
    
    // Make both API calls in parallel
    forkJoin({
      zep: this.memoryService.queryZep(request),
      mem0: this.memoryService.queryMem0(request)
    }).subscribe({
      next: (responses) => {
        // Add Zep response to conversation
        this.zepConversation.unshift({
          query: currentQuery,
          response: responses.zep.response,
          retrievedMemory: responses.zep.retrieved_memory,
          timestamp: new Date(),
          performanceMetrics: responses.zep.performance_metrics
        });

        // Add Mem0 response to conversation  
        this.mem0Conversation.unshift({
          query: currentQuery,
          response: responses.mem0.response,
          retrievedMemory: responses.mem0.retrieved_memory,
          timestamp: new Date(),
          performanceMetrics: responses.mem0.performance_metrics
        });

        // Reset query field
        this.query = '';
        this.isLoading = false;
      },
      error: (error) => {
        console.error('Error:', error);
        this.error = `Error processing query: ${error.error?.detail || error.message || 'Unknown error'}`;
        this.isLoading = false;
      }
    });
  }

  trackByTimestamp(index: number, item: ConversationItem): number {
    return item.timestamp.getTime();
  }
}