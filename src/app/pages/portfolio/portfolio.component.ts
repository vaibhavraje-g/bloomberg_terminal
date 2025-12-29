import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';
import { ApiService } from '../../services/api.service';

@Component({
  selector: 'app-portfolio',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink],
  template: `
    <div class="portfolio-page">
      <div class="page-header">
        <h2>💼 Portfolio</h2>
      </div>

      <!-- Portfolio Summary -->
      <div class="summary-cards" *ngIf="portfolio">
        <div class="summary-card">
          <div class="label">Total Value</div>
          <div class="value">\${{ portfolio.summary.totalValue | number:'1.2-2' }}</div>
        </div>
        <div class="summary-card">
          <div class="label">Total Cost</div>
          <div class="value">\${{ portfolio.summary.totalCost | number:'1.2-2' }}</div>
        </div>
        <div class="summary-card" [class.positive]="portfolio.summary.totalGainLoss > 0" [class.negative]="portfolio.summary.totalGainLoss < 0">
          <div class="label">Total Gain/Loss</div>
          <div class="value">\${{ portfolio.summary.totalGainLoss | number:'1.2-2' }} ({{ portfolio.summary.totalGainLossPercent | number:'1.2-2' }}%)</div>
        </div>
        <div class="summary-card">
          <div class="label">Holdings</div>
          <div class="value">{{ portfolio.summary.holdingsCount }}</div>
        </div>
      </div>

      <!-- Add Holding -->
      <div class="card">
        <div class="card-header"><h5>Add Holding</h5></div>
        <div class="card-body">
          <div class="add-form">
            <input [(ngModel)]="newSymbol" placeholder="Symbol (e.g., AAPL)" class="input">
            <input [(ngModel)]="newQuantity" type="number" placeholder="Quantity" class="input">
            <input [(ngModel)]="newCost" type="number" placeholder="Avg Cost" class="input">
            <button class="btn btn-primary" (click)="addHolding()">Add</button>
          </div>
        </div>
      </div>

      <!-- Holdings Table -->
      <div class="card">
        <div class="card-header"><h5>Holdings</h5></div>
        <div class="card-body">
          <div *ngIf="loading" class="loading-state"><div class="spinner"></div></div>
          <table *ngIf="!loading && portfolio?.holdings?.length" class="table">
            <thead>
              <tr>
                <th>Symbol</th>
                <th class="text-right">Qty</th>
                <th class="text-right">Avg Cost</th>
                <th class="text-right">Current</th>
                <th class="text-right">Value</th>
                <th class="text-right">Gain/Loss</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              <tr *ngFor="let h of portfolio.holdings" [routerLink]="['/stock', h.symbol]" style="cursor:pointer">
                <td><span class="symbol-badge">{{ h.symbol }}</span></td>
                <td class="text-right">{{ h.quantity }}</td>
                <td class="text-right">\${{ h.avg_cost | number:'1.2-2' }}</td>
                <td class="text-right">\${{ h.currentPrice | number:'1.2-2' }}</td>
                <td class="text-right">\${{ h.marketValue | number:'1.2-2' }}</td>
                <td class="text-right" [class.text-positive]="h.gainLoss > 0" [class.text-negative]="h.gainLoss < 0">
                  \${{ h.gainLoss | number:'1.2-2' }} ({{ h.gainLossPercent | number:'1.2-2' }}%)
                </td>
                <td><button class="btn btn-ghost btn-sm" (click)="removeHolding($event, h.symbol)">✕</button></td>
              </tr>
            </tbody>
          </table>
          <div *ngIf="!loading && !portfolio?.holdings?.length" class="empty-state">No holdings yet</div>
        </div>
      </div>

      <!-- Watchlist -->
      <div class="card">
        <div class="card-header">
          <h5>👁️ Watchlist</h5>
          <div class="add-watchlist">
            <input [(ngModel)]="newWatchSymbol" placeholder="Add symbol" class="input" style="width:120px">
            <button class="btn btn-secondary btn-sm" (click)="addToWatchlist()">Add</button>
          </div>
        </div>
        <div class="card-body">
          <div *ngIf="loadingWatchlist" class="loading-state"><div class="spinner"></div></div>
          <div *ngFor="let item of watchlistItems" class="watchlist-row" [routerLink]="['/stock', item.symbol]">
            <span class="symbol">{{ item.symbol }}</span>
            <span class="price">\${{ item.price | number:'1.2-2' }}</span>
            <span [class.text-positive]="item.changePercent > 0" [class.text-negative]="item.changePercent < 0">
              {{ item.changePercent > 0 ? '+' : '' }}{{ item.changePercent | number:'1.2-2' }}%
            </span>
            <button class="btn btn-ghost btn-sm" (click)="removeFromWatchlist($event, item.symbol)">✕</button>
          </div>
        </div>
      </div>
    </div>
  `,
  styles: [`
    .portfolio-page { display: flex; flex-direction: column; gap: 16px; }
    .page-header h2 { margin: 0; }
    .summary-cards { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; }
    .summary-card { padding: 16px; background: #1e1e26; border-radius: 8px; border: 1px solid #2d2d3a; }
    .summary-card .label { font-size: 11px; text-transform: uppercase; color: #6b6b6b; margin-bottom: 4px; }
    .summary-card .value { font-size: 20px; font-weight: 600; font-family: 'JetBrains Mono', monospace; }
    .summary-card.positive .value { color: #00c853; }
    .summary-card.negative .value { color: #ff1744; }
    .add-form { display: flex; gap: 8px; }
    .add-form .input { flex: 1; }
    .symbol-badge { padding: 2px 8px; background: rgba(255,102,0,0.15); color: #ff6600; border-radius: 4px; font-weight: 600; }
    .loading-state { display: flex; justify-content: center; padding: 40px; }
    .empty-state { text-align: center; color: #6b6b6b; padding: 40px; }
    .add-watchlist { display: flex; gap: 8px; }
    .watchlist-row { display: flex; align-items: center; gap: 16px; padding: 12px; border-bottom: 1px solid #2d2d3a; cursor: pointer; }
    .watchlist-row:hover { background: #2a2a35; }
    .watchlist-row .symbol { font-weight: 600; flex: 1; }
    .watchlist-row .price { font-family: 'JetBrains Mono', monospace; }
  `]
})
export class PortfolioComponent implements OnInit {
  portfolio: any = null;
  watchlistItems: any[] = [];
  loading = true;
  loadingWatchlist = true;
  
  newSymbol = '';
  newQuantity: number | null = null;
  newCost: number | null = null;
  newWatchSymbol = '';

  constructor(private api: ApiService) {}

  ngOnInit() {
    this.loadData();
  }

  loadData() {
    this.api.getPortfolio(1).subscribe(data => {
      this.portfolio = data;
      this.loading = false;
    });
    this.api.getWatchlist(1).subscribe(data => {
      this.watchlistItems = data.items || [];
      this.loadingWatchlist = false;
    });
  }

  addHolding() {
    if (this.newSymbol && this.newQuantity && this.newCost) {
      this.api.addHolding(1, { symbol: this.newSymbol, quantity: this.newQuantity, avg_cost: this.newCost }).subscribe(() => {
        this.newSymbol = ''; this.newQuantity = null; this.newCost = null;
        this.loading = true; this.loadData();
      });
    }
  }

  removeHolding(e: Event, symbol: string) {
    e.stopPropagation();
    this.api.removeHolding(1, symbol).subscribe(() => { this.loading = true; this.loadData(); });
  }

  addToWatchlist() {
    if (this.newWatchSymbol) {
      this.api.addToWatchlist(1, this.newWatchSymbol).subscribe(() => {
        this.newWatchSymbol = ''; this.loadingWatchlist = true; this.loadData();
      });
    }
  }

  removeFromWatchlist(e: Event, symbol: string) {
    e.stopPropagation();
    this.api.removeFromWatchlist(1, symbol).subscribe(() => { this.loadingWatchlist = true; this.loadData(); });
  }
}
