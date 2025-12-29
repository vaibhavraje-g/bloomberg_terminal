import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterOutlet, RouterLink, RouterLinkActive } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [CommonModule, RouterOutlet, RouterLink, RouterLinkActive, FormsModule],
  template: `
    <div class="app-container">
      <!-- Header -->
      <header class="app-header">
        <div class="header-left">
          <div class="logo">
            <span class="logo-icon">📊</span>
            <span class="logo-text">TERMINAL</span>
          </div>
          
          <!-- Command Bar -->
          <div class="command-bar">
            <input 
              type="text" 
              [(ngModel)]="searchQuery"
              (keyup.enter)="onSearch()"
              placeholder="Enter symbol or command (e.g., AAPL)"
              class="command-input"
            />
            <button class="go-btn" (click)="onSearch()">GO</button>
          </div>
        </div>
        
        <div class="header-right">
          <div class="market-status">
            <span class="status-dot" [class.open]="isMarketOpen"></span>
            <span>{{ isMarketOpen ? 'MARKET OPEN' : 'MARKET CLOSED' }}</span>
          </div>
          <div class="time mono">{{ currentTime }}</div>
        </div>
      </header>

      <!-- Main Content -->
      <div class="app-main">
        <!-- Sidebar -->
        <nav class="app-sidebar">
          <div class="nav-section">
            <div class="nav-title">MAIN</div>
            <a routerLink="/dashboard" routerLinkActive="active" class="nav-item">
              <span class="nav-icon">📈</span>
              <span>Dashboard</span>
            </a>
            <a routerLink="/news" routerLinkActive="active" class="nav-item">
              <span class="nav-icon">📰</span>
              <span>News</span>
            </a>
            <a routerLink="/analyst" routerLinkActive="active" class="nav-item">
              <span class="nav-icon">🤖</span>
              <span>AI Analyst</span>
            </a>
          </div>
          
          <div class="nav-section">
            <div class="nav-title">TOOLS</div>
            <a routerLink="/portfolio" routerLinkActive="active" class="nav-item">
              <span class="nav-icon">💼</span>
              <span>Portfolio</span>
            </a>
            <a routerLink="/screener" routerLinkActive="active" class="nav-item">
              <span class="nav-icon">🔍</span>
              <span>Screener</span>
            </a>
          </div>
          
          <div class="nav-section">
            <div class="nav-title">WATCHLIST</div>
            <div class="watchlist-items">
              @for (item of quickWatchlist; track item.symbol) {
                <a [routerLink]="['/stock', item.symbol]" class="watchlist-item">
                  <span class="symbol">{{ item.symbol }}</span>
                  <span class="price" [class.positive]="item.change > 0" [class.negative]="item.change < 0">
                    {{ item.change > 0 ? '+' : '' }}{{ item.change | number:'1.2-2' }}%
                  </span>
                </a>
              }
            </div>
          </div>
        </nav>

        <!-- Content Area -->
        <main class="app-content">
          <router-outlet></router-outlet>
        </main>
      </div>
    </div>
  `,
  styles: [`
    .header-left {
      display: flex;
      align-items: center;
      gap: 24px;
    }

    .logo {
      display: flex;
      align-items: center;
      gap: 8px;
      
      .logo-icon {
        font-size: 20px;
      }
      
      .logo-text {
        font-size: 18px;
        font-weight: 700;
        color: #ff6600;
        letter-spacing: 2px;
      }
    }

    .command-bar {
      display: flex;
      align-items: center;
      background: #1a1a1f;
      border: 1px solid #2d2d3a;
      border-radius: 4px;
      overflow: hidden;
      
      .command-input {
        width: 300px;
        padding: 8px 12px;
        border: none;
        background: transparent;
        color: #fff;
        font-family: 'JetBrains Mono', monospace;
        font-size: 13px;
        
        &:focus {
          outline: none;
        }
        
        &::placeholder {
          color: #6b6b6b;
        }
      }
      
      .go-btn {
        padding: 8px 16px;
        background: #ff6600;
        border: none;
        color: white;
        font-weight: 600;
        font-size: 12px;
        cursor: pointer;
        letter-spacing: 1px;
        
        &:hover {
          background: #ff7722;
        }
      }
    }

    .header-right {
      display: flex;
      align-items: center;
      gap: 24px;
    }

    .market-status {
      display: flex;
      align-items: center;
      gap: 8px;
      font-size: 11px;
      text-transform: uppercase;
      letter-spacing: 0.5px;
      color: #a0a0a0;
      
      .status-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: #ff1744;
        
        &.open {
          background: #00c853;
          animation: pulse 2s infinite;
        }
      }
    }

    @keyframes pulse {
      0%, 100% { opacity: 1; }
      50% { opacity: 0.5; }
    }

    .time {
      font-size: 14px;
      color: #fff;
    }

    .nav-section {
      padding: 16px;
      border-bottom: 1px solid #2d2d3a;
    }

    .nav-title {
      font-size: 10px;
      font-weight: 600;
      color: #6b6b6b;
      text-transform: uppercase;
      letter-spacing: 1px;
      margin-bottom: 12px;
    }

    .nav-item {
      display: flex;
      align-items: center;
      gap: 10px;
      padding: 10px 12px;
      color: #a0a0a0;
      text-decoration: none;
      border-radius: 6px;
      font-size: 13px;
      font-weight: 500;
      transition: all 0.15s ease;
      margin-bottom: 4px;
      
      .nav-icon {
        font-size: 16px;
      }
      
      &:hover {
        background: #2a2a35;
        color: #fff;
      }
      
      &.active {
        background: rgba(255, 102, 0, 0.15);
        color: #ff6600;
      }
    }

    .watchlist-items {
      display: flex;
      flex-direction: column;
      gap: 4px;
    }

    .watchlist-item {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 8px 12px;
      border-radius: 4px;
      text-decoration: none;
      font-family: 'JetBrains Mono', monospace;
      font-size: 12px;
      transition: background 0.15s ease;
      
      &:hover {
        background: #2a2a35;
      }
      
      .symbol {
        color: #fff;
        font-weight: 500;
      }
      
      .price {
        font-weight: 500;
        
        &.positive { color: #00c853; }
        &.negative { color: #ff1744; }
      }
    }
  `]
})
export class AppComponent {
  searchQuery = '';
  currentTime = '';
  isMarketOpen = false;
  quickWatchlist = [
    { symbol: 'AAPL', change: 1.25 },
    { symbol: 'MSFT', change: -0.54 },
    { symbol: 'GOOGL', change: 0.89 },
    { symbol: 'AMZN', change: -1.12 },
    { symbol: 'NVDA', change: 2.34 }
  ];

  constructor(private router: Router) {
    this.updateTime();
    setInterval(() => this.updateTime(), 1000);
    this.checkMarketStatus();
  }

  updateTime() {
    const now = new Date();
    this.currentTime = now.toLocaleTimeString('en-US', { 
      hour: '2-digit', 
      minute: '2-digit',
      second: '2-digit',
      hour12: false 
    });
  }

  checkMarketStatus() {
    const now = new Date();
    const day = now.getDay();
    const hour = now.getHours();
    const minute = now.getMinutes();
    const time = hour * 60 + minute;
    
    // NYSE hours: 9:30 AM - 4:00 PM ET (approx check)
    const marketOpen = 9 * 60 + 30;
    const marketClose = 16 * 60;
    
    this.isMarketOpen = day >= 1 && day <= 5 && time >= marketOpen && time < marketClose;
  }

  onSearch() {
    if (this.searchQuery.trim()) {
      this.router.navigate(['/stock', this.searchQuery.trim().toUpperCase()]);
      this.searchQuery = '';
    }
  }
}
