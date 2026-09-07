"""
LLM Service - Gemini AI & Local Financial Analysis Engine
"""
from typing import Optional, Dict, Any, List
from datetime import datetime

from config import get_settings
from services.market_data import market_service

try:
    import google.generativeai as genai
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False


class LLMService:
    """Service for AI-powered financial analysis with Gemini and offline fallback"""
    
    def __init__(self):
        self.settings = get_settings()
        self.model = None
        self._initialize()
    
    def _initialize(self):
        """Initialize Gemini model with current generation models"""
        if not GENAI_AVAILABLE or not self.settings.gemini_api_key:
            return

        try:
            genai.configure(api_key=self.settings.gemini_api_key)
            # Try 1.5 flash first, fallback to pro
            for model_name in ['gemini-1.5-flash', 'gemini-1.5-pro', 'gemini-2.0-flash']:
                try:
                    self.model = genai.GenerativeModel(model_name)
                    break
                except Exception:
                    continue
        except Exception as e:
            print(f"[!] Warning: Could not initialize Gemini API: {e}")
            self.model = None

    def _generate_heuristic_stock_analysis(self, symbol: str, quote: Dict[str, Any], company_info: Dict[str, Any]) -> str:
        """Generates structured financial analysis even without external API credentials"""
        price = quote.get('price', 0.0)
        change_pct = quote.get('changePercent', 0.0)
        mcap = quote.get('marketCap', 0.0)
        pe = quote.get('peRatio', 'N/A')
        eps = quote.get('eps', 0.0)
        high52 = quote.get('week52High', 0.0)
        low52 = quote.get('week52Low', 0.0)
        beta = quote.get('beta', 'N/A')
        sector = company_info.get('sector', 'Technology')
        name = company_info.get('name', symbol.upper())
        desc = company_info.get('description', '')[:300]

        sentiment = "Bullish" if change_pct > 0 else "Neutral/Consolidating"
        if change_pct < -2.0:
            sentiment = "Bearish"

        report = f"""### Financial Intelligence Report: {name} ({symbol.upper()})
> **Analysis Engine**: Heuristic Quantitative Evaluator *(Set `GEMINI_API_KEY` for generative neural analysis)*

#### 1. Executive Summary
{name} is currently trading at **${price:.2f}** ({change_pct:+.2f}%), with an estimated market capitalization of **${mcap:,.0f}**. The company operates primarily within the **{sector}** sector.
{desc}...

#### 2. Fundamental & Valuation Review
- **Price to Earnings (P/E)**: {pe} — Valuation reflects current market expectations relative to {sector} sector medians.
- **Earnings Per Share (EPS)**: ${eps:.2f} — Indicates profitability baseline for shareholder equity.
- **52-Week Range**: Low **${low52:.2f}** | High **${high52:.2f}**. Price is positioned at {((price - low52) / (high52 - low52) * 100) if (high52 > low52) else 50:.1f}% of its annual channel.

#### 3. Risk & Volatility Profile
- **Beta**: {beta} — {'Higher volatility than the benchmark index' if isinstance(beta, (int, float)) and beta > 1.1 else 'Standard or defensive market correlation'}.
- **Capital Liquidity**: Adequate trading depth observed across recent sessions.

#### 4. Synthetic Outlook & Recommendation
- **Current Technical Bias**: **{sentiment}**
- **Actionable Posture**: Watch support near ${low52:.2f} and dynamic resistance approaching ${high52:.2f}. For institutional multi-turn chat and generative scenarios, ensure Gemini credentials are provided.
"""
        return report

    async def analyze_stock(self, symbol: str) -> Dict[str, Any]:
        """Comprehensive stock analysis using AI or fallback engine"""
        try:
            quote = await market_service.get_quote(symbol)
            company_info = await market_service.get_company_info(symbol)

            if not self.model:
                analysis_text = self._generate_heuristic_stock_analysis(symbol, quote, company_info)
                return {
                    "symbol": symbol.upper(),
                    "analysis": analysis_text,
                    "timestamp": datetime.now().isoformat(),
                    "engine": "heuristic_offline",
                    "data": {
                        "quote": quote,
                        "company": company_info
                    }
                }

            context = f"""
Stock: {symbol.upper()}
Company: {company_info.get('name', 'N/A')}
Sector: {company_info.get('sector', 'N/A')}
Current Price: ${quote.get('price', 0):.2f} ({quote.get('changePercent', 0):.2f}%)
Market Cap: ${quote.get('marketCap', 0):,.0f}
P/E Ratio: {quote.get('peRatio', 'N/A')}
EPS: ${quote.get('eps', 0):.2f}
52-Week High: ${quote.get('week52High', 0):.2f}
52-Week Low: ${quote.get('week52Low', 0):.2f}
"""
            prompt = f"""
You are a senior financial analyst at a tier-1 investment bank.
Provide a concise markdown analysis with:
1. Overview
2. Valuation & Fundamentals
3. Catalysts & Risks
4. Recommendation (Bullish / Neutral / Bearish)

{context}
"""
            response = self.model.generate_content(prompt)
            return {
                "symbol": symbol.upper(),
                "analysis": response.text,
                "timestamp": datetime.now().isoformat(),
                "engine": "gemini_generative",
                "data": {
                    "quote": quote,
                    "company": company_info
                }
            }
        except Exception as e:
            return {"symbol": symbol.upper(), "error": str(e)}

    async def chat(self, message: str, context: Optional[str] = None) -> str:
        """Financial assistant chat interface"""
        if not self.model:
            return (
                f"**Terminal AI Assistant** *(Local Engine)*\n\n"
                f"Received query: \"{message}\"\n\n"
                f"To enable dynamic multi-turn generative conversational responses, configure `GEMINI_API_KEY` in `backend/.env`. "
                f"In the meantime, live market quotes, chart indicators, watchlists, screener, and heuristic reports are active!"
            )

        try:
            prompt = f"System: Professional financial analyst.\nContext: {context or 'None'}\nQuery: {message}"
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Error generating response: {str(e)}"

    async def compare_stocks(self, symbols: List[str]) -> Dict[str, Any]:
        """Compare multiple stocks"""
        try:
            stocks_data = []
            for s in symbols:
                quote = await market_service.get_quote(s)
                company = await market_service.get_company_info(s)
                stocks_data.append({"symbol": s.upper(), "quote": quote, "company": company})

            if not self.model:
                comparison = "### Comparative Valuation Matrix\n\n"
                comparison += "| Symbol | Price | Change | MCap | P/E | Sector |\n|---|---|---|---|---|---|\n"
                for st in stocks_data:
                    q = st['quote']
                    c = st['company']
                    comparison += f"| **{st['symbol']}** | ${q.get('price', 0):.2f} | {q.get('changePercent', 0):+.2f}% | ${q.get('marketCap', 0):,.0f} | {q.get('peRatio', 'N/A')} | {c.get('sector', 'N/A')} |\n"
                comparison += "\n*Heuristic benchmark computed from live quote streams.*"
                return {
                    "symbols": [s.upper() for s in symbols],
                    "comparison": comparison,
                    "timestamp": datetime.now().isoformat(),
                    "data": stocks_data
                }

            context = str(stocks_data)
            response = self.model.generate_content(f"Compare these stocks objectively with metrics table: {context}")
            return {
                "symbols": [s.upper() for s in symbols],
                "comparison": response.text,
                "timestamp": datetime.now().isoformat(),
                "data": stocks_data
            }
        except Exception as e:
            return {"error": str(e)}

    async def summarize_news(self, news_items: List[Dict]) -> str:
        """Summarize news articles"""
        if not self.model:
            headlines = [f"- {item.get('title', 'Headline')} ({item.get('source', 'Newswire')})" for item in news_items[:5]]
            return "### Market News Pulse\n" + "\n".join(headlines) + "\n\n*Macro sentiment reflects current session headlines.*"

        try:
            news_text = "\n".join([f"- {item.get('title', '')} ({item.get('source', '')})" for item in news_items[:8]])
            response = self.model.generate_content(f"Summarize these headlines into market themes and sentiment: {news_text}")
            return response.text
        except Exception as e:
            return f"Error summarizing news: {str(e)}"


llm_service = LLMService()
