import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, catchError, of } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class ApiService {
  private baseUrl = 'http://localhost:8001/api';

  constructor(private http: HttpClient) {}

  // Market Data
  getQuote(symbol: string): Observable<any> {
    return this.http.get(`${this.baseUrl}/market/quote/${symbol}`).pipe(
      catchError(err => of({ error: err.message }))
    );
  }

  getQuotes(symbols: string[]): Observable<any> {
    return this.http.get(`${this.baseUrl}/market/quotes?symbols=${symbols.join(',')}`).pipe(
      catchError(err => of([]))
    );
  }

  getHistory(symbol: string, period: string = '1mo', interval: string = '1d'): Observable<any> {
    return this.http.get(`${this.baseUrl}/market/history/${symbol}?period=${period}&interval=${interval}`).pipe(
      catchError(err => of([]))
    );
  }

  getCompanyInfo(symbol: string): Observable<any> {
    return this.http.get(`${this.baseUrl}/market/company/${symbol}`).pipe(
      catchError(err => of({ error: err.message }))
    );
  }

  getFinancials(symbol: string): Observable<any> {
    return this.http.get(`${this.baseUrl}/market/financials/${symbol}`).pipe(
      catchError(err => of({ error: err.message }))
    );
  }

  getMarketIndices(): Observable<any> {
    return this.http.get(`${this.baseUrl}/market/indices`).pipe(
      catchError(err => of([]))
    );
  }

  getSectorPerformance(): Observable<any> {
    return this.http.get(`${this.baseUrl}/market/sectors`).pipe(
      catchError(err => of([]))
    );
  }

  searchSymbols(query: string): Observable<any> {
    return this.http.get(`${this.baseUrl}/market/search?q=${query}`).pipe(
      catchError(err => of([]))
    );
  }

  getTechnicalIndicators(symbol: string): Observable<any> {
    return this.http.get(`${this.baseUrl}/market/technical/${symbol}`).pipe(
      catchError(err => of({ error: err.message }))
    );
  }

  getChartData(symbol: string, period: string = '6mo', indicators: string[] = ['sma20', 'sma50', 'volume']): Observable<any> {
    return this.http.get(`${this.baseUrl}/market/chart/${symbol}?period=${period}&indicators=${indicators.join(',')}`).pipe(
      catchError(err => of({ error: err.message }))
    );
  }

  // News
  getNews(symbol?: string, limit: number = 20): Observable<any> {
    const url = symbol 
      ? `${this.baseUrl}/news/symbol/${symbol}?limit=${limit}`
      : `${this.baseUrl}/news/?limit=${limit}`;
    return this.http.get(url).pipe(
      catchError(err => of([]))
    );
  }

  getNewsSummary(symbol?: string): Observable<any> {
    return this.http.get(`${this.baseUrl}/news/summary${symbol ? '?symbol=' + symbol : ''}`).pipe(
      catchError(err => of({ summary: 'Unable to generate summary' }))
    );
  }

  // AI Analysis
  analyzeStock(symbol: string): Observable<any> {
    return this.http.get(`${this.baseUrl}/analysis/stock/${symbol}`).pipe(
      catchError(err => of({ error: err.message }))
    );
  }

  chat(message: string, context?: string): Observable<any> {
    return this.http.post(`${this.baseUrl}/analysis/chat`, { message, context }).pipe(
      catchError(err => of({ response: 'Error: Unable to process request' }))
    );
  }

  compareStocks(symbols: string[]): Observable<any> {
    return this.http.post(`${this.baseUrl}/analysis/compare`, { symbols }).pipe(
      catchError(err => of({ error: err.message }))
    );
  }

  // Portfolio
  getPortfolios(): Observable<any> {
    return this.http.get(`${this.baseUrl}/portfolio/`).pipe(
      catchError(err => of([]))
    );
  }

  getPortfolio(id: number): Observable<any> {
    return this.http.get(`${this.baseUrl}/portfolio/${id}`).pipe(
      catchError(err => of({ error: err.message }))
    );
  }

  addHolding(portfolioId: number, holding: any): Observable<any> {
    return this.http.post(`${this.baseUrl}/portfolio/${portfolioId}/holdings`, holding).pipe(
      catchError(err => of({ error: err.message }))
    );
  }

  removeHolding(portfolioId: number, symbol: string): Observable<any> {
    return this.http.delete(`${this.baseUrl}/portfolio/${portfolioId}/holdings/${symbol}`).pipe(
      catchError(err => of({ error: err.message }))
    );
  }

  // Watchlist
  getWatchlists(): Observable<any> {
    return this.http.get(`${this.baseUrl}/watchlist/`).pipe(
      catchError(err => of([]))
    );
  }

  getWatchlist(id: number): Observable<any> {
    return this.http.get(`${this.baseUrl}/watchlist/${id}`).pipe(
      catchError(err => of({ error: err.message }))
    );
  }

  addToWatchlist(watchlistId: number, symbol: string): Observable<any> {
    return this.http.post(`${this.baseUrl}/watchlist/${watchlistId}/items`, { symbol }).pipe(
      catchError(err => of({ error: err.message }))
    );
  }

  removeFromWatchlist(watchlistId: number, symbol: string): Observable<any> {
    return this.http.delete(`${this.baseUrl}/watchlist/${watchlistId}/items/${symbol}`).pipe(
      catchError(err => of({ error: err.message }))
    );
  }

  // Screener
  getTopGainers(): Observable<any> {
    return this.http.get(`${this.baseUrl}/screener/gainers`).pipe(
      catchError(err => of([]))
    );
  }

  getTopLosers(): Observable<any> {
    return this.http.get(`${this.baseUrl}/screener/losers`).pipe(
      catchError(err => of([]))
    );
  }

  getMostActive(): Observable<any> {
    return this.http.get(`${this.baseUrl}/screener/most-active`).pipe(
      catchError(err => of([]))
    );
  }

  screenStocks(criteria: any): Observable<any> {
    return this.http.post(`${this.baseUrl}/screener/screen`, criteria).pipe(
      catchError(err => of({ results: [] }))
    );
  }

  getPresetScreen(preset: string): Observable<any> {
    return this.http.get(`${this.baseUrl}/screener/presets/${preset}`).pipe(
      catchError(err => of({ results: [] }))
    );
  }
}
