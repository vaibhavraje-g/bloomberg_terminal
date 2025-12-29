import { Routes } from '@angular/router';
import { DashboardComponent } from './pages/dashboard/dashboard.component';
import { StockDetailComponent } from './pages/stock-detail/stock-detail.component';
import { NewsComponent } from './pages/news/news.component';
import { PortfolioComponent } from './pages/portfolio/portfolio.component';
import { ScreenerComponent } from './pages/screener/screener.component';
import { AiAnalystComponent } from './pages/ai-analyst/ai-analyst.component';

export const routes: Routes = [
  { path: '', redirectTo: 'dashboard', pathMatch: 'full' },
  { path: 'dashboard', component: DashboardComponent },
  { path: 'stock/:symbol', component: StockDetailComponent },
  { path: 'news', component: NewsComponent },
  { path: 'portfolio', component: PortfolioComponent },
  { path: 'screener', component: ScreenerComponent },
  { path: 'analyst', component: AiAnalystComponent }
];
