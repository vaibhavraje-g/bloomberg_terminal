import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ApiService } from '../../services/api.service';

@Component({
  selector: 'app-news',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="news-page">
      <div class="page-header">
        <h2>📰 Financial News</h2>
      </div>

      <div class="card summary-card">
        <div class="card-header">
          <h5>🤖 AI News Summary</h5>
          <button class="btn btn-primary btn-sm" (click)="loadSummary()" [disabled]="loadingSummary">
            {{ loadingSummary ? 'Generating...' : 'Generate' }}
          </button>
        </div>
        <div class="card-body">
          <div *ngIf="loadingSummary" class="loading-state"><div class="spinner"></div></div>
          <div *ngIf="newsSummary && !loadingSummary" class="summary-content">{{ newsSummary }}</div>
          <div *ngIf="!newsSummary && !loadingSummary" class="empty-state">Click Generate for AI summary</div>
        </div>
      </div>

      <div class="card">
        <div class="card-header"><h5>Headlines</h5></div>
        <div class="card-body">
          <div *ngIf="loading" class="loading-state"><div class="spinner"></div></div>
          <div *ngFor="let news of newsItems" class="news-row">
            <a [href]="news.url" target="_blank">
              <div class="news-title">{{ news.title }}</div>
              <div class="news-meta">
                <span class="tag" [ngClass]="{'tag-success': news.sentiment==='positive', 'tag-danger': news.sentiment==='negative'}">{{ news.sentiment }}</span>
                <span>{{ news.source }}</span>
              </div>
            </a>
          </div>
        </div>
      </div>
    </div>
  `,
  styles: [`
    .news-page { display: flex; flex-direction: column; gap: 16px; }
    .page-header h2 { margin: 0; }
    .loading-state { display: flex; justify-content: center; padding: 40px; }
    .empty-state { text-align: center; color: #6b6b6b; padding: 20px; }
    .summary-content { line-height: 1.7; white-space: pre-wrap; }
    .news-row { padding: 12px 0; border-bottom: 1px solid #2d2d3a; }
    .news-row a { text-decoration: none; color: inherit; }
    .news-title { font-weight: 500; margin-bottom: 6px; }
    .news-meta { display: flex; gap: 12px; font-size: 12px; color: #6b6b6b; }
  `]
})
export class NewsComponent implements OnInit {
  newsItems: any[] = [];
  newsSummary = '';
  loading = true;
  loadingSummary = false;

  constructor(private api: ApiService) {}

  ngOnInit() {
    this.api.getNews(undefined, 20).subscribe(data => {
      this.newsItems = data;
      this.loading = false;
    });
  }

  loadSummary() {
    this.loadingSummary = true;
    this.api.getNewsSummary().subscribe(data => {
      this.newsSummary = data.summary;
      this.loadingSummary = false;
    });
  }
}
