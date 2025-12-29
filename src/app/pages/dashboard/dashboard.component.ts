import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { ApiService } from '../../services/api.service';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule, RouterLink],
  template: `
    <div class="dashboard">
      <!-- Market Indices Ticker -->
      <div class="ticker-tape">
        @for (index of indices; track index.symbol) {
          <div class="ticker-item">
            <span class="symbol">{{ index.name }}</span>
            <span class="price mono">{{ index.price | number:'1.2-2' }}</span>
            <span class="change mono" [class.text-positive]="index.changePercent > 0" [class.text-negative]="index.changePercent < 0">
              {{ index.changePercent > 0 ? '+' : '' }}{{ index.changePercent | number:'1.2-2' }}%
            </span>
          </div>
        }
        @if (loadingIndices) {
          <div class="ticker-item">Loading indices...</div>
        }
      </div>

      <!-- Main Grid -->
      <div class="dashboard-grid">
        <!-- Left Column -->
        <div class="dashboard-left">
          <!-- Market Movers -->
          <div class="card">
            <div class="card-header">
              <h5>🔥 Market Movers</h5>
              <div class="tabs">
                <button 
                  class="tab" 
                  [class.active]="activeTab === 'gainers'"
                  (click)="switchTab('gainers')">
                  Gainers
                </button>
                <button 
                  class="tab" 
                  [class.active]="activeTab === 'losers'"
                  (click)="switchTab('losers')">
                  Losers
                </button>
                <button 
                  class="tab" 
                  [class.active]="activeTab === 'active'"
                  (click)="switchTab('active')">
                  Active
                </button>
              </div>
            </div>
            <div class="card-body">
              @if (loadingMovers) {
                <div class="loading-state">
                  <div class="spinner"></div>
                  <span>Loading market data...</span>
                </div>
              } @else {
                <table class="table">
                  <thead>
                    <tr>
                      <th>Symbol</th>
                      <th>Name</th>
                      <th class="text-right">Price</th>
                      <th class="text-right">Change</th>
                    </tr>
                  </thead>
                  <tbody>
                    @for (stock of marketMovers; track stock.symbol) {
                      <tr [routerLink]="['/stock', stock.symbol]" style="cursor: pointer;">
                        <td>
                          <span class="symbol-badge">{{ stock.symbol }}</span>
                        </td>
                        <td class="text-secondary">{{ stock.name | slice:0:25 }}{{ stock.name?.length > 25 ? '...' : '' }}</td>
                        <td class="text-right">{{ stock.price | number:'1.2-2' }}</td>
                        <td class="text-right" [class.text-positive]="stock.changePercent > 0" [class.text-negative]="stock.changePercent < 0">
                          {{ stock.changePercent > 0 ? '+' : '' }}{{ stock.changePercent | number:'1.2-2' }}%
                        </td>
                      </tr>
                    }
                  </tbody>
                </table>
              }
            </div>
          </div>

          <!-- Sector Performance -->
          <div class="card">
            <div class="card-header">
              <h5>📊 Sector Performance</h5>
            </div>
            <div class="card-body">
              @if (loadingSectors) {
                <div class="loading-state">
                  <div class="spinner"></div>
                </div>
              } @else {
                <div class="sector-grid">
                  @for (sector of sectors; track sector.symbol) {
                    <div class="sector-item" [class.positive]="sector.changePercent > 0" [class.negative]="sector.changePercent < 0">
                      <div class="sector-name">{{ sector.sector }}</div>
                      <div class="sector-change">{{ sector.changePercent > 0 ? '+' : '' }}{{ sector.changePercent | number:'1.2-2' }}%</div>
                    </div>
                  }
                </div>
              }
            </div>
          </div>
        </div>

        <!-- Right Column - News & Watchlist -->
        <div class="dashboard-right">
          <!-- Watchlist -->
          <div class="card">
            <div class="card-header">
              <h5>👁️ Watchlist</h5>
              <a routerLink="/portfolio" class="btn btn-ghost btn-sm">Manage</a>
            </div>
            <div class="card-body">
              @if (loadingWatchlist) {
                <div class="loading-state">
                  <div class="spinner"></div>
                </div>
              } @else {
                @for (item of watchlistItems; track item.symbol) {
                  <div class="watchlist-row" [routerLink]="['/stock', item.symbol]">
                    <div class="watch-info">
                      <span class="watch-symbol">{{ item.symbol }}</span>
                      <span class="watch-name">{{ item.name | slice:0:20 }}</span>
                    </div>
                    <div class="watch-data">
                      <span class="watch-price">{{ item.price | number:'1.2-2' }}</span>
                      <span class="watch-change" [class.text-positive]="item.changePercent > 0" [class.text-negative]="item.changePercent < 0">
                        {{ item.changePercent > 0 ? '+' : '' }}{{ item.changePercent | number:'1.2-2' }}%
                      </span>
                    </div>
                  </div>
                }
              }
            </div>
          </div>

          <!-- Latest News -->
          <div class="card">
            <div class="card-header">
              <h5>📰 Latest News</h5>
              <a routerLink="/news" class="btn btn-ghost btn-sm">View All</a>
            </div>
            <div class="card-body news-list">
              @if (loadingNews) {
                <div class="loading-state">
                  <div class="spinner"></div>
                </div>
              } @else {
                @for (news of newsItems; track news.id) {
                  <a [href]="news.url" target="_blank" class="news-item">
                    <div class="news-content">
                      <div class="news-title">{{ news.title }}</div>
                      <div class="news-meta">
                        <span class="tag" [class.tag-success]="news.sentiment === 'positive'" 
                              [class.tag-danger]="news.sentiment === 'negative'">
                          {{ news.sentiment }}
                        </span>
                        <span>{{ news.source }}</span>
                        <span class="news-time">{{ getTimeAgo(news.publishedAt) }}</span>
                      </div>
                    </div>
                    @if (news.thumbnail) {
                      <img [src]="news.thumbnail" class="news-image" alt="">
                    }
                  </a>
                }
              }
            </div>
          </div>
        </div>
      </div>
    </div>
  `,
  styles: [`
    .dashboard {
      display: flex;
      flex-direction: column;
      gap: 16px;
    }

    .dashboard-grid {
      display: grid;
      grid-template-columns: 1.2fr 1fr;
      gap: 16px;
    }

    .dashboard-left, .dashboard-right {
      display: flex;
      flex-direction: column;
      gap: 16px;
    }

    .tabs {
      display: flex;
      gap: 4px;
    }

    .tab {
      padding: 4px 12px;
      background: transparent;
      border: 1px solid #2d2d3a;
      border-radius: 4px;
      color: #a0a0a0;
      font-size: 11px;
      cursor: pointer;
      transition: all 0.15s ease;

      &:hover {
        background: #2a2a35;
        color: #fff;
      }

      &.active {
        background: #ff6600;
        border-color: #ff6600;
        color: white;
      }
    }

    .symbol-badge {
      padding: 2px 8px;
      background: rgba(255, 102, 0, 0.15);
      color: #ff6600;
      border-radius: 4px;
      font-weight: 600;
      font-size: 12px;
    }

    .loading-state {
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      padding: 40px;
      color: #6b6b6b;
      gap: 12px;
    }

    .sector-grid {
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 8px;
    }

    .sector-item {
      padding: 12px;
      background: #1a1a1f;
      border-radius: 6px;
      border: 1px solid #2d2d3a;
      text-align: center;

      &.positive {
        border-color: rgba(0, 200, 83, 0.3);
        background: rgba(0, 200, 83, 0.05);
        
        .sector-change { color: #00c853; }
      }

      &.negative {
        border-color: rgba(255, 23, 68, 0.3);
        background: rgba(255, 23, 68, 0.05);
        
        .sector-change { color: #ff1744; }
      }

      .sector-name {
        font-size: 11px;
        color: #a0a0a0;
        margin-bottom: 4px;
      }

      .sector-change {
        font-family: 'JetBrains Mono', monospace;
        font-size: 14px;
        font-weight: 600;
      }
    }

    .watchlist-row {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 12px;
      border-bottom: 1px solid #2d2d3a;
      cursor: pointer;
      transition: background 0.15s ease;

      &:hover {
        background: #2a2a35;
      }

      &:last-child {
        border-bottom: none;
      }

      .watch-info {
        display: flex;
        flex-direction: column;
        gap: 2px;

        .watch-symbol {
          font-weight: 600;
          font-size: 14px;
        }

        .watch-name {
          font-size: 11px;
          color: #6b6b6b;
        }
      }

      .watch-data {
        display: flex;
        flex-direction: column;
        align-items: flex-end;
        gap: 2px;

        .watch-price {
          font-family: 'JetBrains Mono', monospace;
          font-size: 14px;
        }

        .watch-change {
          font-family: 'JetBrains Mono', monospace;
          font-size: 12px;
          font-weight: 500;
        }
      }
    }

    .news-list {
      padding: 0 !important;
    }

    @media (max-width: 1200px) {
      .dashboard-grid {
        grid-template-columns: 1fr;
      }
      
      .sector-grid {
        grid-template-columns: repeat(2, 1fr);
      }
    }
  `]
})
export class DashboardComponent implements OnInit {
  indices: any[] = [];
  marketMovers: any[] = [];
  sectors: any[] = [];
  watchlistItems: any[] = [];
  newsItems: any[] = [];
  
  activeTab = 'gainers';
  loadingIndices = true;
  loadingMovers = true;
  loadingSectors = true;
  loadingWatchlist = true;
  loadingNews = true;

  constructor(private api: ApiService) {}

  ngOnInit() {
    this.loadData();
  }

  loadData() {
    this.api.getMarketIndices().subscribe(data => {
      this.indices = data || [];
      this.loadingIndices = false;
    });

    this.loadMarketMovers();

    this.api.getSectorPerformance().subscribe(data => {
      this.sectors = data || [];
      this.loadingSectors = false;
    });

    this.api.getWatchlist(1).subscribe(data => {
      this.watchlistItems = data.items || [];
      this.loadingWatchlist = false;
    });

    this.api.getNews(undefined, 5).subscribe(data => {
      this.newsItems = data || [];
      this.loadingNews = false;
    });
  }

  loadMarketMovers() {
    this.loadingMovers = true;
    
    if (this.activeTab === 'gainers') {
      this.api.getTopGainers().subscribe(data => {
        this.marketMovers = data || [];
        this.loadingMovers = false;
      });
    } else if (this.activeTab === 'losers') {
      this.api.getTopLosers().subscribe(data => {
        this.marketMovers = data || [];
        this.loadingMovers = false;
      });
    } else {
      this.api.getMostActive().subscribe(data => {
        this.marketMovers = data || [];
        this.loadingMovers = false;
      });
    }
  }

  switchTab(tab: string) {
    this.activeTab = tab;
    this.loadMarketMovers();
  }

  getTimeAgo(dateString: string): string {
    if (!dateString) return '';
    const date = new Date(dateString);
    const now = new Date();
    const diff = now.getTime() - date.getTime();
    const hours = Math.floor(diff / (1000 * 60 * 60));
    
    if (hours < 1) return 'Just now';
    if (hours < 24) return `${hours}h ago`;
    return `${Math.floor(hours / 24)}d ago`;
  }
}
