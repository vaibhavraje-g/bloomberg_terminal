import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ApiService } from '../../services/api.service';

interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
}

@Component({
  selector: 'app-ai-analyst',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <div class="ai-page">
      <div class="page-header">
        <h2>🤖 AI Financial Analyst</h2>
        <p>Ask questions about stocks, markets, or get analysis</p>
      </div>

      <div class="chat-container">
        <div class="chat-messages">
          <div *ngIf="!messages.length" class="welcome-message">
            <h3>Welcome! I can help you with:</h3>
            <div class="suggestions">
              <button *ngFor="let s of suggestions" class="suggestion-btn" (click)="sendMessage(s)">{{ s }}</button>
            </div>
          </div>
          
          <div *ngFor="let msg of messages" class="chat-message" [class.user]="msg.role === 'user'" [class.assistant]="msg.role === 'assistant'">
            <div class="message-content" [innerHTML]="formatMessage(msg.content)"></div>
          </div>
          
          <div *ngIf="loading" class="chat-message assistant">
            <div class="typing-indicator"><span></span><span></span><span></span></div>
          </div>
        </div>

        <div class="chat-input">
          <input [(ngModel)]="inputMessage" (keyup.enter)="sendMessage()" placeholder="Ask about stocks, markets, analysis..." class="input">
          <button class="btn btn-primary" (click)="sendMessage()" [disabled]="loading || !inputMessage.trim()">Send</button>
        </div>
      </div>

      <!-- Quick Actions -->
      <div class="quick-actions">
        <div class="action-card" (click)="analyzeStock('AAPL')">
          <span class="icon">📊</span>
          <span>Analyze AAPL</span>
        </div>
        <div class="action-card" (click)="compareStocks()">
          <span class="icon">⚖️</span>
          <span>Compare MSFT vs GOOGL</span>
        </div>
        <div class="action-card" (click)="marketOutlook()">
          <span class="icon">🌍</span>
          <span>Market Outlook</span>
        </div>
      </div>
    </div>
  `,
  styles: [`
    .ai-page { display: flex; flex-direction: column; gap: 16px; height: calc(100vh - 120px); }
    .page-header { flex-shrink: 0; }
    .page-header h2 { margin: 0 0 4px; }
    .page-header p { margin: 0; color: #6b6b6b; }
    
    .chat-container { flex: 1; display: flex; flex-direction: column; background: #1e1e26; border-radius: 12px; border: 1px solid #2d2d3a; overflow: hidden; }
    .chat-messages { flex: 1; overflow-y: auto; padding: 20px; display: flex; flex-direction: column; gap: 16px; }
    
    .welcome-message { text-align: center; padding: 40px 20px; }
    .welcome-message h3 { margin-bottom: 20px; color: #a0a0a0; }
    .suggestions { display: flex; flex-wrap: wrap; justify-content: center; gap: 8px; }
    .suggestion-btn { padding: 10px 16px; background: #252530; border: 1px solid #2d2d3a; border-radius: 20px; color: #fff; cursor: pointer; font-size: 13px; }
    .suggestion-btn:hover { background: #2a2a35; border-color: #ff6600; }
    
    .chat-message { max-width: 80%; padding: 14px 18px; border-radius: 16px; line-height: 1.6; }
    .chat-message.user { align-self: flex-end; background: #ff6600; color: white; border-bottom-right-radius: 4px; }
    .chat-message.assistant { align-self: flex-start; background: #252530; border: 1px solid #2d2d3a; border-bottom-left-radius: 4px; }
    
    .message-content { font-size: 14px; }
    .message-content :deep(strong) { color: #ff6600; }
    .message-content :deep(h2), .message-content :deep(h3) { margin: 12px 0 8px; font-size: 15px; }
    
    .typing-indicator { display: flex; gap: 4px; }
    .typing-indicator span { width: 8px; height: 8px; background: #6b6b6b; border-radius: 50%; animation: bounce 1.4s infinite ease-in-out both; }
    .typing-indicator span:nth-child(1) { animation-delay: -0.32s; }
    .typing-indicator span:nth-child(2) { animation-delay: -0.16s; }
    @keyframes bounce { 0%, 80%, 100% { transform: scale(0); } 40% { transform: scale(1); } }
    
    .chat-input { display: flex; gap: 12px; padding: 16px; border-top: 1px solid #2d2d3a; background: #1a1a1f; }
    .chat-input .input { flex: 1; }
    
    .quick-actions { display: flex; gap: 12px; flex-shrink: 0; }
    .action-card { flex: 1; display: flex; align-items: center; gap: 12px; padding: 16px; background: #1e1e26; border: 1px solid #2d2d3a; border-radius: 8px; cursor: pointer; transition: all 0.15s; }
    .action-card:hover { background: #2a2a35; border-color: #ff6600; }
    .action-card .icon { font-size: 24px; }
  `]
})
export class AiAnalystComponent {
  messages: ChatMessage[] = [];
  inputMessage = '';
  loading = false;
  
  suggestions = [
    'What are the top tech stocks to watch?',
    'Explain P/E ratio',
    'Should I invest in index funds?',
    'What affects stock prices?'
  ];

  constructor(private api: ApiService) {}

  sendMessage(text?: string) {
    const message = text || this.inputMessage.trim();
    if (!message) return;
    
    this.messages.push({ role: 'user', content: message });
    this.inputMessage = '';
    this.loading = true;
    
    this.api.chat(message).subscribe(data => {
      this.messages.push({ role: 'assistant', content: data.response });
      this.loading = false;
    });
  }

  analyzeStock(symbol: string) {
    this.sendMessage(`Analyze ${symbol} stock - give me a comprehensive overview`);
  }

  compareStocks() {
    this.sendMessage('Compare Microsoft (MSFT) and Google (GOOGL) - which is the better investment?');
  }

  marketOutlook() {
    this.sendMessage('What is the current market outlook? Any sectors to watch?');
  }

  formatMessage(text: string): string {
    return text
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/\*(.*?)\*/g, '<em>$1</em>')
      .replace(/^### (.*$)/gm, '<h3>$1</h3>')
      .replace(/^## (.*$)/gm, '<h2>$1</h2>')
      .replace(/\n/g, '<br>');
  }
}
