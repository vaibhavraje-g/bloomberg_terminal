import { Component, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { ApiService } from '../../services/api.service';

@Component({
  selector: 'app-stock-detail',
  standalone: true,
  imports: [CommonModule, RouterLink],
  template: `
    <div class="stock-detail" *ngIf="quote">
      <!-- Header -->
      <div class="stock-header">
        <div class="stock-info">
          <div class="stock-title">
            <span class="symbol-badge">{{ symbol }}</span>
            <h1>{{ quote.name }}</h1>
            <span class="exchange">{{ quote.exchange }}</span>
          </div>
          <div class="stock-meta">
            <span class="tag tag-accent">{{ quote.sector }}</span>
            <span class="tag">{{ quote.industry }}</span>
          </div>
        </div>
        
        <div class="price-display">
          <div class="price mono">\${{ quote.price | number:'1.2-2' }}</div>
          <div class="change" [class.text-positive]="quote.changePercent > 0" [class.text-negative]="quote.changePercent < 0">
            <span class="amount">{{ quote.change > 0 ? '+' : '' }}{{ quote.change | number:'1.2-2' }}</span>
            <span class="percent">({{ quote.changePercent > 0 ? '+' : '' }}{{ quote.changePercent | number:'1.2-2' }}%)</span>
          </div>
        </div>
      </div>

      <!-- Main Content Grid -->
      <div class="stock-grid">
        <!-- Left Column -->
        <div class="stock-left">
          <!-- Chart Placeholder -->
          <div class="card">
            <div class="card-header">
              <h5>📈 Price Chart</h5>
              <div class="chart-controls">
                @for (period of chartPeriods; track period) {
                  <button 
                    class="btn btn-sm" 
                    [class.btn-primary]="selectedPeriod === period"
                    [class.btn-ghost]="selectedPeriod !== period"
                    (click)="changePeriod(period)">
                    {{ period }}
                  </button>
                }
              </div>
            </div>
            <div class="card-body">
              <div class="chart-placeholder">
                @if (loadingChart) {
                  <div class="spinner"></div>
                  <span>Loading chart data...</span>
                } @else if (chartData.length > 0) {
                  <!-- Simple ASCII-style chart representation -->
                  <div class="simple-chart">
                    <div class="chart-bars">
                      @for (point of getChartPoints(); track $index) {
                        <div class="chart-bar" [style.height.%]="point.height" [class.positive]="point.isPositive"></div>
                      }
                    </div>
                    <div class="chart-info">
                      <span>High: \${{ getMaxPrice() | number:'1.2-2' }}</span>
                      <span>Low: \${{ getMinPrice() | number:'1.2-2' }}</span>
                    </div>
                  </div>
                } @else {
                  <span>No chart data available</span>
                }
              </div>
            </div>
          </div>

          <!-- Key Statistics -->
          <div class="card">
            <div class="card-header">
              <h5>📊 Key Statistics</h5>
            </div>
            <div class="card-body">
              <div class="stats-grid">
                <div class="stat-item">
                  <div class="label">Open</div>
                  <div class="value mono">\${{ quote.open | number:'1.2-2' }}</div>
                </div>
                <div class="stat-item">
                  <div class="label">Day High</div>
                  <div class="value mono">\${{ quote.high | number:'1.2-2' }}</div>
                </div>
                <div class="stat-item">
                  <div class="label">Day Low</div>
                  <div class="value mono">\${{ quote.low | number:'1.2-2' }}</div>
                </div>
                <div class="stat-item">
                  <div class="label">Volume</div>
                  <div class="value mono">{{ formatVolume(quote.volume) }}</div>
                </div>
                <div class="stat-item">
                  <div class="label">Avg Volume</div>
                  <div class="value mono">{{ formatVolume(quote.avgVolume) }}</div>
                </div>
                <div class="stat-item">
                  <div class="label">Market Cap</div>
                  <div class="value mono">{{ formatMarketCap(quote.marketCap) }}</div>
                </div>
                <div class="stat-item">
                  <div class="label">P/E Ratio</div>
                  <div class="value mono">{{ quote.peRatio | number:'1.2-2' }}</div>
                </div>
                <div class="stat-item">
                  <div class="label">EPS</div>
                  <div class="value mono">\${{ quote.eps | number:'1.2-2' }}</div>
                </div>
                <div class="stat-item">
                  <div class="label">52W High</div>
                  <div class="value mono">\${{ quote.week52High | number:'1.2-2' }}</div>
                </div>
                <div class="stat-item">
                  <div class="label">52W Low</div>
                  <div class="value mono">\${{ quote.week52Low | number:'1.2-2' }}</div>
                </div>
                <div class="stat-item">
                  <div class="label">Beta</div>
                  <div class="value mono">{{ quote.beta | number:'1.2-2' }}</div>
                </div>
                <div class="stat-item">
                  <div class="label">Dividend Yield</div>
                  <div class="value mono">{{ (quote.dividend || 0) * 100 | number:'1.2-2' }}%</div>
                </div>
              </div>
            </div>
          </div>

          <!-- Technical Indicators -->
          <div class="card" *ngIf="technicals">
            <div class="card-header">
              <h5>📉 Technical Indicators</h5>
              <span class="tag" [class.tag-success]="technicals.trend === 'bullish'" [class.tag-danger]="technicals.trend === 'bearish'">
                {{ technicals.trend | uppercase }}
              </span>
            </div>
            <div class="card-body">
              <div class="tech-grid">
                <div class="tech-section">
                  <h6>Moving Averages</h6>
                  <div class="tech-items">
                    <div class="tech-item">
                      <span>SMA 20</span>
                      <span class="mono">\${{ technicals.indicators?.movingAverages?.sma20 | number:'1.2-2' }}</span>
                    </div>
                    <div class="tech-item">
                      <span>SMA 50</span>
                      <span class="mono">\${{ technicals.indicators?.movingAverages?.sma50 | number:'1.2-2' }}</span>
                    </div>
                    <div class="tech-item">
                      <span>SMA 200</span>
                      <span class="mono">{{ technicals.indicators?.movingAverages?.sma200 ? ('$' + (technicals.indicators?.movingAverages?.sma200 | number:'1.2-2')) : 'N/A' }}</span>
                    </div>
                  </div>
                </div>
                <div class="tech-section">
                  <h6>Momentum</h6>
                  <div class="tech-items">
                    <div class="tech-item">
                      <span>RSI (14)</span>
                      <span class="mono" [class.text-positive]="technicals.indicators?.momentum?.rsi < 30" [class.text-negative]="technicals.indicators?.momentum?.rsi > 70">
                        {{ technicals.indicators?.momentum?.rsi | number:'1.1-1' }}
                      </span>
                    </div>
                    <div class="tech-item">
                      <span>MACD</span>
                      <span class="mono">{{ technicals.indicators?.momentum?.macd | number:'1.2-2' }}</span>
                    </div>
                  </div>
                </div>
                <div class="tech-section">
                  <h6>Volatility</h6>
                  <div class="tech-items">
                    <div class="tech-item">
                      <span>ATR</span>
                      <span class="mono">\${{ technicals.indicators?.volatility?.atr | number:'1.2-2' }}</span>
                    </div>
                    <div class="tech-item">
                      <span>BB Upper</span>
                      <span class="mono">\${{ technicals.indicators?.volatility?.bollingerUpper | number:'1.2-2' }}</span>
                    </div>
                    <div class="tech-item">
                      <span>BB Lower</span>
                      <span class="mono">\${{ technicals.indicators?.volatility?.bollingerLower | number:'1.2-2' }}</span>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Signals -->
              <div class="signals" *ngIf="technicals.signals?.length">
                <h6>Signals</h6>
                <div class="signal-list">
                  @for (signal of technicals.signals; track $index) {
                    <div class="signal-item">
                      <span class="tag" [class.tag-success]="signal.signal === 'bullish' || signal.signal === 'oversold'"
                            [class.tag-danger]="signal.signal === 'bearish' || signal.signal === 'overbought'"
                            [class.tag-warning]="signal.signal === 'neutral'">
                        {{ signal.type | uppercase }}
                      </span>
                      <span>{{ signal.description }}</span>
                    </div>
                  }
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Right Column -->
        <div class="stock-right">
          <!-- AI Analysis -->
          <div class="card">
            <div class="card-header">
              <h5>🤖 AI Analysis</h5>
              <button class="btn btn-primary btn-sm" (click)="loadAIAnalysis()" [disabled]="loadingAnalysis">
                {{ loadingAnalysis ? 'Analyzing...' : 'Analyze' }}
              </button>
            </div>
            <div class="card-body">
              @if (loadingAnalysis) {
                <div class="loading-state">
                  <div class="spinner"></div>
                  <span>AI is analyzing {{ symbol }}...</span>
                </div>
              } @else if (aiAnalysis) {
                <div class="ai-content" [innerHTML]="formatMarkdown(aiAnalysis)"></div>
              } @else {
                <div class="empty-state">
                  <p>Click "Analyze" to get AI-powered insights about {{ symbol }}</p>
                </div>
              }
            </div>
          </div>

          <!-- Company Info -->
          <div class="card" *ngIf="company">
            <div class="card-header">
              <h5>🏢 Company Profile</h5>
            </div>
            <div class="card-body">
              <p class="company-description">{{ company.description | slice:0:300 }}{{ company.description?.length > 300 ? '...' : '' }}</p>
              
              <div class="company-details">
                <div class="detail-item">
                  <span class="label">Headquarters</span>
                  <span class="value">{{ company.headquarters }}</span>
                </div>
                <div class="detail-item">
                  <span class="label">Employees</span>
                  <span class="value">{{ company.employees | number }}</span>
                </div>
                <div class="detail-item">
                  <span class="label">Website</span>
                  <a [href]="company.website" target="_blank" class="value link">{{ company.website }}</a>
                </div>
              </div>
            </div>
          </div>

          <!-- News -->
          <div class="card">
            <div class="card-header">
              <h5>📰 Related News</h5>
            </div>
            <div class="card-body news-list">
              @if (loadingNews) {
                <div class="loading-state">
                  <div class="spinner"></div>
                </div>
              } @else {
                @for (news of newsItems; track news.id) {
                  <a [href]="news.url" target="_blank" class="news-item compact">
                    <div class="news-title">{{ news.title }}</div>
                    <div class="news-meta">
                      <span class="tag" [class.tag-success]="news.sentiment === 'positive'" 
                            [class.tag-danger]="news.sentiment === 'negative'">
                        {{ news.sentiment }}
                      </span>
                      <span>{{ news.source }}</span>
                    </div>
                  </a>
                }
              }
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Loading State -->
    <div class="loading-full" *ngIf="loading">
      <div class="spinner"></div>
      <span>Loading {{ symbol }}...</span>
    </div>
  `,
  styles: [`
    .stock-detail {
      display: flex;
      flex-direction: column;
      gap: 20px;
    }

    .stock-header {
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      padding: 20px;
      background: #1e1e26;
      border-radius: 12px;
      border: 1px solid #2d2d3a;
    }

    .symbol-badge {
      padding: 4px 12px;
      background: #ff6600;
      color: white;
      border-radius: 4px;
      font-weight: 700;
      font-size: 14px;
    }

    .stock-title {
      display: flex;
      align-items: center;
      gap: 12px;
      margin-bottom: 8px;

      h1 {
        font-size: 24px;
        margin: 0;
      }

      .exchange {
        font-size: 12px;
        color: #6b6b6b;
      }
    }

    .stock-meta {
      display: flex;
      gap: 8px;
    }

    .price-display {
      text-align: right;

      .price {
        font-size: 36px;
        font-weight: 700;
      }

      .change {
        display: flex;
        justify-content: flex-end;
        gap: 8px;
        font-size: 16px;
        font-weight: 500;
        font-family: 'JetBrains Mono', monospace;
      }
    }

    .stock-grid {
      display: grid;
      grid-template-columns: 1.2fr 1fr;
      gap: 16px;
    }

    .stock-left, .stock-right {
      display: flex;
      flex-direction: column;
      gap: 16px;
    }

    .chart-controls {
      display: flex;
      gap: 4px;
    }

    .chart-placeholder {
      height: 300px;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      color: #6b6b6b;
      gap: 12px;
    }

    .simple-chart {
      width: 100%;
      height: 100%;
      display: flex;
      flex-direction: column;

      .chart-bars {
        flex: 1;
        display: flex;
        align-items: flex-end;
        gap: 2px;
        padding: 0 4px;
      }

      .chart-bar {
        flex: 1;
        background: #ff1744;
        min-height: 2px;
        border-radius: 1px 1px 0 0;
        transition: height 0.3s ease;

        &.positive {
          background: #00c853;
        }
      }

      .chart-info {
        display: flex;
        justify-content: space-between;
        padding-top: 12px;
        border-top: 1px solid #2d2d3a;
        font-size: 12px;
        color: #a0a0a0;
        font-family: 'JetBrains Mono', monospace;
      }
    }

    .stats-grid {
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 16px;
    }

    .tech-grid {
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 20px;
      margin-bottom: 20px;
    }

    .tech-section {
      h6 {
        font-size: 11px;
        text-transform: uppercase;
        color: #6b6b6b;
        margin-bottom: 12px;
        letter-spacing: 0.5px;
      }
    }

    .tech-items {
      display: flex;
      flex-direction: column;
      gap: 8px;
    }

    .tech-item {
      display: flex;
      justify-content: space-between;
      font-size: 13px;

      span:first-child {
        color: #a0a0a0;
      }
    }

    .signals {
      padding-top: 16px;
      border-top: 1px solid #2d2d3a;

      h6 {
        font-size: 11px;
        text-transform: uppercase;
        color: #6b6b6b;
        margin-bottom: 12px;
      }
    }

    .signal-list {
      display: flex;
      flex-direction: column;
      gap: 8px;
    }

    .signal-item {
      display: flex;
      align-items: center;
      gap: 12px;
      font-size: 13px;
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

    .empty-state {
      text-align: center;
      color: #6b6b6b;
      padding: 20px;
    }

    .ai-content {
      font-size: 14px;
      line-height: 1.6;

      :deep(h2) { font-size: 16px; margin: 16px 0 8px; color: #ff6600; }
      :deep(h3) { font-size: 14px; margin: 12px 0 6px; }
      :deep(ul) { margin: 8px 0; padding-left: 20px; }
      :deep(li) { margin: 4px 0; }
      :deep(strong) { color: #fff; }
    }

    .company-description {
      font-size: 13px;
      line-height: 1.6;
      color: #a0a0a0;
      margin-bottom: 16px;
    }

    .company-details {
      display: flex;
      flex-direction: column;
      gap: 8px;
    }

    .detail-item {
      display: flex;
      justify-content: space-between;
      font-size: 13px;

      .label { color: #6b6b6b; }
      .link { color: #00d4ff; text-decoration: none; &:hover { text-decoration: underline; } }
    }

    .news-list {
      padding: 0 !important;
    }

    .news-item.compact {
      padding: 12px 16px;

      .news-title {
        font-size: 13px;
        margin-bottom: 6px;
      }
    }

    .loading-full {
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      height: 400px;
      color: #6b6b6b;
      gap: 16px;
    }

    @media (max-width: 1200px) {
      .stock-grid {
        grid-template-columns: 1fr;
      }

      .stats-grid {
        grid-template-columns: repeat(3, 1fr);
      }

      .tech-grid {
        grid-template-columns: 1fr;
      }
    }
  `]
})
export class StockDetailComponent implements OnInit {
  symbol = '';
  quote: any = null;
  company: any = null;
  technicals: any = null;
  chartData: any[] = [];
  newsItems: any[] = [];
  aiAnalysis = '';

  loading = true;
  loadingChart = true;
  loadingNews = true;
  loadingAnalysis = false;

  selectedPeriod = '6mo';
  chartPeriods = ['1mo', '3mo', '6mo', '1y', '2y'];

  constructor(
    private route: ActivatedRoute,
    private api: ApiService
  ) {}

  ngOnInit() {
    this.route.params.subscribe(params => {
      this.symbol = params['symbol']?.toUpperCase();
      if (this.symbol) {
        this.loadStockData();
      }
    });
  }

  loadStockData() {
    this.loading = true;
    
    this.api.getQuote(this.symbol).subscribe(data => {
      this.quote = data;
      this.loading = false;
    });

    this.api.getCompanyInfo(this.symbol).subscribe(data => {
      this.company = data;
    });

    this.api.getTechnicalIndicators(this.symbol).subscribe(data => {
      this.technicals = data;
    });

    this.loadChartData();

    this.api.getNews(this.symbol, 5).subscribe(data => {
      this.newsItems = data;
      this.loadingNews = false;
    });
  }

  loadChartData() {
    this.loadingChart = true;
    this.api.getHistory(this.symbol, this.selectedPeriod).subscribe(data => {
      this.chartData = data || [];
      this.loadingChart = false;
    });
  }

  changePeriod(period: string) {
    this.selectedPeriod = period;
    this.loadChartData();
  }

  loadAIAnalysis() {
    this.loadingAnalysis = true;
    this.api.analyzeStock(this.symbol).subscribe(data => {
      this.aiAnalysis = data.analysis || data.error || 'Analysis unavailable';
      this.loadingAnalysis = false;
    });
  }

  getChartPoints(): { height: number; isPositive: boolean }[] {
    if (!this.chartData.length) return [];
    
    const closes = this.chartData.map(d => d.close);
    const min = Math.min(...closes);
    const max = Math.max(...closes);
    const range = max - min || 1;
    
    // Get last 50 points
    const points = this.chartData.slice(-50);
    
    return points.map((d, i) => ({
      height: ((d.close - min) / range) * 80 + 10,
      isPositive: i === 0 ? d.close >= d.open : d.close >= points[i - 1].close
    }));
  }

  getMaxPrice(): number {
    return Math.max(...this.chartData.map(d => d.high));
  }

  getMinPrice(): number {
    return Math.min(...this.chartData.map(d => d.low));
  }

  formatVolume(vol: number): string {
    if (!vol) return 'N/A';
    if (vol >= 1e9) return (vol / 1e9).toFixed(2) + 'B';
    if (vol >= 1e6) return (vol / 1e6).toFixed(2) + 'M';
    if (vol >= 1e3) return (vol / 1e3).toFixed(2) + 'K';
    return vol.toString();
  }

  formatMarketCap(cap: number): string {
    if (!cap) return 'N/A';
    if (cap >= 1e12) return '$' + (cap / 1e12).toFixed(2) + 'T';
    if (cap >= 1e9) return '$' + (cap / 1e9).toFixed(2) + 'B';
    if (cap >= 1e6) return '$' + (cap / 1e6).toFixed(2) + 'M';
    return '$' + cap.toString();
  }

  formatMarkdown(text: string): string {
    // Basic markdown formatting
    return text
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/\*(.*?)\*/g, '<em>$1</em>')
      .replace(/^### (.*$)/gm, '<h3>$1</h3>')
      .replace(/^## (.*$)/gm, '<h2>$1</h2>')
      .replace(/^- (.*$)/gm, '<li>$1</li>')
      .replace(/(<li>.*<\/li>)/s, '<ul>$1</ul>')
      .replace(/\n/g, '<br>');
  }
}
