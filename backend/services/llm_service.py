"""
LLM Service - Gemini AI integration for financial analysis
"""
import google.generativeai as genai
from typing import Optional, Dict, Any, List
from datetime import datetime

from config import get_settings
from services.market_data import market_service


class LLMService:
    """Service for AI-powered financial analysis using Gemini"""
    
    def __init__(self):
        self.settings = get_settings()
        self.model = None
        self._initialize()
    
    def _initialize(self):
        """Initialize the Gemini model"""
        if self.settings.gemini_api_key:
            genai.configure(api_key=self.settings.gemini_api_key)
            self.model = genai.GenerativeModel('gemini-pro')
    
    async def analyze_stock(self, symbol: str) -> Dict[str, Any]:
        """Comprehensive stock analysis using AI"""
        if not self.model:
            return {"error": "Gemini API key not configured"}
        
        try:
            # Fetch stock data
            quote = await market_service.get_quote(symbol)
            company_info = await market_service.get_company_info(symbol)
            
            # Build context
            context = f"""
            Stock: {symbol.upper()}
            Company: {company_info.get('name', 'N/A')}
            Sector: {company_info.get('sector', 'N/A')}
            Industry: {company_info.get('industry', 'N/A')}
            
            Current Price: ${quote.get('price', 0):.2f}
            Change: {quote.get('changePercent', 0):.2f}%
            Market Cap: ${quote.get('marketCap', 0):,.0f}
            P/E Ratio: {quote.get('peRatio', 'N/A')}
            EPS: ${quote.get('eps', 0):.2f}
            52-Week High: ${quote.get('week52High', 0):.2f}
            52-Week Low: ${quote.get('week52Low', 0):.2f}
            Beta: {quote.get('beta', 'N/A')}
            Dividend Yield: {(quote.get('dividend', 0) or 0) * 100:.2f}%
            
            Business Description: {company_info.get('description', 'N/A')[:500]}
            """
            
            prompt = f"""
            You are a professional financial analyst. Analyze the following stock and provide:
            
            1. **Overview**: Brief company summary
            2. **Key Metrics Analysis**: Interpret the financial metrics (P/E, EPS, etc.)
            3. **Strengths**: Main competitive advantages
            4. **Risks**: Key risks and concerns
            5. **Technical Position**: Analysis based on 52-week range and beta
            6. **Recommendation**: General outlook (Bullish/Neutral/Bearish) with reasoning
            
            Be concise but insightful. Format with markdown.
            
            {context}
            """
            
            response = self.model.generate_content(prompt)
            
            return {
                "symbol": symbol.upper(),
                "analysis": response.text,
                "timestamp": datetime.now().isoformat(),
                "data": {
                    "quote": quote,
                    "company": company_info
                }
            }
        except Exception as e:
            return {"symbol": symbol, "error": str(e)}
    
    async def chat(self, message: str, context: Optional[str] = None) -> str:
        """General financial chat with AI"""
        if not self.model:
            return "Error: Gemini API key not configured. Please add GEMINI_API_KEY to your .env file."
        
        try:
            system_prompt = """
            You are a professional financial analyst assistant for a Bloomberg Terminal-like application.
            You have expertise in:
            - Stock market analysis
            - Technical and fundamental analysis
            - Portfolio management
            - Economic indicators
            - Financial news interpretation
            
            Provide clear, concise, and actionable insights.
            Use markdown formatting for better readability.
            When discussing specific stocks, include key metrics when relevant.
            Always remind users that this is not financial advice.
            """
            
            full_prompt = f"{system_prompt}\n\n"
            if context:
                full_prompt += f"Context:\n{context}\n\n"
            full_prompt += f"User Query: {message}"
            
            response = self.model.generate_content(full_prompt)
            return response.text
        except Exception as e:
            return f"Error generating response: {str(e)}"
    
    async def compare_stocks(self, symbols: List[str]) -> Dict[str, Any]:
        """Compare multiple stocks"""
        if not self.model:
            return {"error": "Gemini API key not configured"}
        
        try:
            # Fetch data for all symbols
            stocks_data = []
            for symbol in symbols:
                quote = await market_service.get_quote(symbol)
                company = await market_service.get_company_info(symbol)
                stocks_data.append({
                    "symbol": symbol.upper(),
                    "quote": quote,
                    "company": company
                })
            
            # Build comparison context
            context = "Stock Comparison:\n\n"
            for stock in stocks_data:
                q = stock["quote"]
                c = stock["company"]
                context += f"""
                {stock['symbol']}:
                - Price: ${q.get('price', 0):.2f} ({q.get('changePercent', 0):.2f}%)
                - Market Cap: ${q.get('marketCap', 0):,.0f}
                - P/E: {q.get('peRatio', 'N/A')}
                - EPS: ${q.get('eps', 0):.2f}
                - Sector: {c.get('sector', 'N/A')}
                
                """
            
            prompt = f"""
            Compare these stocks and provide:
            
            1. **Overview**: Brief comparison summary
            2. **Valuation Comparison**: Which appears more fairly valued?
            3. **Growth Comparison**: Growth potential analysis
            4. **Risk Comparison**: Which carries more risk?
            5. **Recommendation**: Which would you prefer and why?
            
            Be objective and data-driven. Format with markdown.
            
            {context}
            """
            
            response = self.model.generate_content(prompt)
            
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
            return "Error: Gemini API key not configured"
        
        try:
            news_text = "\n".join([
                f"- {item.get('title', '')} ({item.get('source', '')})"
                for item in news_items[:10]
            ])
            
            prompt = f"""
            Summarize these financial news headlines into key market themes and insights.
            Identify any major trends or events that could impact the market.
            
            Headlines:
            {news_text}
            
            Provide:
            1. Key Themes (2-3 bullet points)
            2. Market Sentiment (bullish/neutral/bearish)
            3. Stocks/Sectors to Watch
            
            Be concise and actionable.
            """
            
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Error summarizing news: {str(e)}"


# Singleton instance
llm_service = LLMService()
