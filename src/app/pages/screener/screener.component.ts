import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';
import { ApiService } from '../../services/api.service';

@Component({
  selector: 'app-screener',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink],
  template: `
    <div class="screener-page">
      <div class="page-header">
        <h2>🔍 Stock Screener</h2>
      </div>

      <!-- Presets -->
      <div class="card">
        <div class="card-header"><h5>Quick Screens</h5></div>
        <div class="card-body">
          <div class="preset-buttons">
            <button *ngFor="let p of presets" class="btn" [class.btn-primary]="activePreset === p.id" [class.btn-secondary]="activePreset !== p.id" (click)="runPreset(p.id)">
              {{ p.label }}
            </button>
          </div>
        </div>
      </div>

      <!-- Custom Filters -->
      <div class="card">
        <div class="card-header"><h5>Custom Filters</h5></div>
        <div class="card-body">
          <div class="filter-grid">
            <div class="filter-item">
              <label>Min Market Cap</label>
              <select [(ngModel)]="filters.minMarketCap" class="input">
                <option [ngValue]="null">Any</option>
                <option [ngValue]="1e9">$1B+</option>
                <option [ngValue]="10e9">$10B+</option>
                <option [ngValue]="50e9">$50B+</option>
                <option [ngValue]="200e9">$200B+</option>
              </select>
            </div>
            <div class="filter-item">
              <label>Max P/E</label>
              <select [(ngModel)]="filters.maxPE" class="input">
                <option [ngValue]="null">Any</option>
                <option [ngValue]="10">10</option>
                <option [ngValue]="15">15</option>
                <option [ngValue]="20">20</option>
                <option [ngValue]="30">30</option>
              </select>
            </div>
            <div class="filter-item">
              <label>Min Dividend %</label>
              <select [(ngModel)]="filters.minDividendYield" class="input">
                <option [ngValue]="null">Any</option>
                <option [ngValue]="1">1%+</option>
                <option [ngValue]="2">2%+</option>
                <option [ngValue]="3">3%+</option>
                <option [ngValue]="5">5%+</option>
              </select>
            </div>
            <div class="filter-item">
              <label>Sector</label>
              <select [(ngModel)]="filters.sector" class="input">
                <option [ngValue]="null">Any</option>
                <option value="Technology">Technology</option>
                <option value="Healthcare">Healthcare</option>
                <option value="Financial Services">Financial Services</option>
                <option value="Consumer Cyclical">Consumer</option>
                <option value="Energy">Energy</option>
              </select>
            </div>
          </div>
          <button class="btn btn-primary" (click)="runScreen()" style="margin-top:16px">Run Screen</button>
        </div>
      </div>

      <!-- Results -->
      <div class="card">
        <div class="card-header">
          <h5>Results</h5>
          <span class="text-muted">{{ results.length }} stocks found</span>
        </div>
        <div class="card-body">
          <div *ngIf="loading" class="loading-state"><div class="spinner"></div></div>
          <table *ngIf="!loading && results.length" class="table">
            <thead>
              <tr>
                <th>Symbol</th>
                <th>Name</th>
                <th>Sector</th>
                <th class="text-right">Price</th>
                <th class="text-right">Change</th>
                <th class="text-right">Market Cap</th>
                <th class="text-right">P/E</th>
              </tr>
            </thead>
            <tbody>
              <tr *ngFor="let s of results" [routerLink]="['/stock', s.symbol]" style="cursor:pointer">
                <td><span class="symbol-badge">{{ s.symbol }}</span></td>
                <td>{{ s.name | slice:0:25 }}</td>
                <td class="text-muted">{{ s.sector }}</td>
                <td class="text-right">\${{ s.price | number:'1.2-2' }}</td>
                <td class="text-right" [class.text-positive]="s.changePercent > 0" [class.text-negative]="s.changePercent < 0">
                  {{ s.changePercent > 0 ? '+' : '' }}{{ s.changePercent | number:'1.2-2' }}%
                </td>
                <td class="text-right">\${{ formatCap(s.marketCap) }}</td>
                <td class="text-right">{{ s.peRatio | number:'1.1-1' }}</td>
              </tr>
            </tbody>
          </table>
          <div *ngIf="!loading && !results.length" class="empty-state">No stocks match your criteria</div>
        </div>
      </div>
    </div>
  `,
  styles: [`
    .screener-page { display: flex; flex-direction: column; gap: 16px; }
    .page-header h2 { margin: 0; }
    .preset-buttons { display: flex; flex-wrap: wrap; gap: 8px; }
    .filter-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; }
    .filter-item { display: flex; flex-direction: column; gap: 4px; }
    .filter-item label { font-size: 11px; text-transform: uppercase; color: #6b6b6b; }
    .symbol-badge { padding: 2px 8px; background: rgba(255,102,0,0.15); color: #ff6600; border-radius: 4px; font-weight: 600; font-size: 12px; }
    .loading-state { display: flex; justify-content: center; padding: 40px; }
    .empty-state { text-align: center; color: #6b6b6b; padding: 40px; }
  `]
})
export class ScreenerComponent implements OnInit {
  presets = [
    { id: 'gainers', label: '🚀 Top Gainers' },
    { id: 'losers', label: '📉 Top Losers' },
    { id: 'value', label: '💎 Value' },
    { id: 'dividend', label: '💰 Dividend' },
    { id: 'largecap', label: '🏢 Large Cap' },
    { id: 'tech', label: '💻 Tech' }
  ];

  filters: any = { minMarketCap: null, maxPE: null, minDividendYield: null, sector: null };
  activePreset = '';
  results: any[] = [];
  loading = false;

  constructor(private api: ApiService) {}

  ngOnInit() { this.runPreset('gainers'); }

  runPreset(preset: string) {
    this.activePreset = preset;
    this.loading = true;
    if (preset === 'gainers') {
      this.api.getTopGainers().subscribe(d => { this.results = d; this.loading = false; });
    } else if (preset === 'losers') {
      this.api.getTopLosers().subscribe(d => { this.results = d; this.loading = false; });
    } else {
      this.api.getPresetScreen(preset).subscribe(d => { this.results = d.results || []; this.loading = false; });
    }
  }

  runScreen() {
    this.activePreset = '';
    this.loading = true;
    this.api.screenStocks(this.filters).subscribe(d => { this.results = d.results || []; this.loading = false; });
  }

  formatCap(cap: number): string {
    if (!cap) return 'N/A';
    if (cap >= 1e12) return (cap / 1e12).toFixed(1) + 'T';
    if (cap >= 1e9) return (cap / 1e9).toFixed(1) + 'B';
    return (cap / 1e6).toFixed(1) + 'M';
  }
}
