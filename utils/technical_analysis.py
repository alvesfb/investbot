# utils/technical_analysis.py
"""
Analisador Técnico Básico - Fase 3
Implementa indicadores técnicos simples para componente técnico das recomendações

Indicadores implementados:
- Médias Móveis (20, 50 períodos)
- RSI básico (14 períodos)
- Tendência de preços
- Volume confirmação
- Score técnico combinado (0-100)
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import json
import logging

logger = logging.getLogger(__name__)


class TechnicalAnalyzer:
    """
    Analisador Técnico para cálculo de score técnico básico
    
    Implementa indicadores simples que serão expandidos nas fases futuras:
    - Médias móveis para identificar tendência
    - RSI para identificar sobrecompra/sobrevenda
    - Análise de volume
    - Score técnico combinado
    """
    
    def __init__(self):
        """Inicializa o analisador técnico"""
        self.logger = logger
        
        # Parâmetros dos indicadores
        self.ma_short_period = 20    # Média móvel curta
        self.ma_long_period = 50     # Média móvel longa
        self.rsi_period = 14         # Período RSI
        
        # Thresholds para classificação
        self.rsi_overbought = 70
        self.rsi_oversold = 30
        
        # Pesos para score final
        self.weights = {
            "trend": 0.40,      # 40% peso para tendência
            "rsi": 0.30,        # 30% peso para RSI
            "volume": 0.20,     # 20% peso para volume
            "momentum": 0.10    # 10% peso para momentum
        }
        
        self.logger.info("TechnicalAnalyzer inicializado")
    
    async def calculate_score(self, stock_code: str, agent_response: str) -> float:
        """
        Calcula score técnico baseado na resposta do agente
        
        Args:
            stock_code: Código da ação
            agent_response: Resposta do agente com dados históricos
            
        Returns:
            Score técnico de 0-100
        """
        try:
            # Extrair dados da resposta do agente
            price_data = self._extract_price_data(agent_response)
            
            if not price_data or len(price_data) < self.ma_long_period:
                self.logger.warning(f"Dados insuficientes para análise técnica de {stock_code}")
                return 50.0  # Score neutro
            
            # Converter para DataFrame para facilitar cálculos
            df = pd.DataFrame(price_data)
            
            # Calcular indicadores
            trend_score = self._calculate_trend_score(df)
            rsi_score = self._calculate_rsi_score(df)
            volume_score = self._calculate_volume_score(df)
            momentum_score = self._calculate_momentum_score(df)
            
            # Combinar scores com pesos
            final_score = (
                trend_score * self.weights["trend"] +
                rsi_score * self.weights["rsi"] +
                volume_score * self.weights["volume"] +
                momentum_score * self.weights["momentum"]
            )
            
            self.logger.info(
                f"Score técnico para {stock_code}: {final_score:.1f} "
                f"(Trend: {trend_score:.1f}, RSI: {rsi_score:.1f}, "
                f"Volume: {volume_score:.1f}, Momentum: {momentum_score:.1f})"
            )
            
            return round(final_score, 1)
            
        except Exception as e:
            self.logger.error(f"Erro no cálculo do score técnico para {stock_code}: {str(e)}")
            return 50.0  # Score neutro como fallback
    
    def _extract_price_data(self, agent_response: str) -> Optional[List[Dict]]:
        """
        Extrai dados de preços da resposta do agente
        
        Espera formato similar a:
        [
            {"date": "2025-01-01", "close": 30.50, "volume": 1000000, "high": 31.00, "low": 30.00},
            ...
        ]
        """
        try:
            # Tentar encontrar JSON na resposta
            import re
            
            # Procurar por estruturas JSON na resposta
            json_pattern = r'\[.*?\]'
            matches = re.findall(json_pattern, agent_response, re.DOTALL)
            
            for match in matches:
                try:
                    data = json.loads(match)
                    if isinstance(data, list) and len(data) > 0:
                        # Verificar se tem estrutura de dados de preços
                        first_item = data[0]
                        if all(key in first_item for key in ['close', 'volume']):
                            return data
                except json.JSONDecodeError:
                    continue
            
            # Se não encontrar JSON, tentar extrair valores numéricos
            # (implementação básica para casos simples)
            return self._extract_simple_price_data(agent_response)
            
        except Exception as e:
            self.logger.warning(f"Erro ao extrair dados de preços: {str(e)}")
            return None
    
    def _extract_simple_price_data(self, response: str) -> Optional[List[Dict]]:
        """Extrai dados simples se não encontrar JSON estruturado"""
        try:
            # Implementação simplificada - gerar dados mock para desenvolvimento
            # Na implementação real, isso seria substituído por parsing mais robusto
            
            import random
            from datetime import datetime, timedelta
            
            # Gerar dados mock para desenvolvimento (TEMPORÁRIO)
            base_price = 30.0
            data = []
            
            for i in range(60):  # 60 dias de dados
                date = datetime.now() - timedelta(days=60-i)
                
                # Simular variação de preço
                price_change = random.uniform(-0.05, 0.05)
                base_price *= (1 + price_change)
                
                data.append({
                    "date": date.strftime("%Y-%m-%d"),
                    "close": round(base_price, 2),
                    "volume": random.randint(500000, 2000000),
                    "high": round(base_price * 1.02, 2),
                    "low": round(base_price * 0.98, 2)
                })
            
            self.logger.warning("Usando dados mock para análise técnica - implementar parsing real")
            return data
            
        except Exception as e:
            self.logger.error(f"Erro ao gerar dados simples: {str(e)}")
            return None
    
    def _calculate_trend_score(self, df: pd.DataFrame) -> float:
        """
        Calcula score de tendência baseado em médias móveis
        
        Args:
            df: DataFrame com dados de preços
            
        Returns:
            Score de 0-100 (100 = tendência muito positiva)
        """
        try:
            # Calcular médias móveis
            df['ma_short'] = df['close'].rolling(window=self.ma_short_period).mean()
            df['ma_long'] = df['ma_long_period'].rolling(window=self.ma_long_period).mean()
            
            # Pegar valores mais recentes
            current_price = df['close'].iloc[-1]
            ma_short = df['ma_short'].iloc[-1]
            ma_long = df['ma_long'].iloc[-1]
            
            score = 50.0  # Base neutra
            
            # Posição do preço em relação às médias
            if current_price > ma_short > ma_long:
                score += 30  # Tendência muito positiva
            elif current_price > ma_short:
                score += 20  # Tendência positiva
            elif current_price > ma_long:
                score += 10  # Tendência levemente positiva
            elif current_price < ma_short < ma_long:
                score -= 30  # Tendência muito negativa
            elif current_price < ma_short:
                score -= 20  # Tendência negativa
            elif current_price < ma_long:
                score -= 10  # Tendência levemente negativa
            
            # Direção das médias (últimos 5 dias)
            if len(df) >= 5:
                ma_short_direction = ma_short - df['ma_short'].iloc[-5]
                ma_long_direction = ma_long - df['ma_long'].iloc[-5]
                
                if ma_short_direction > 0 and ma_long_direction > 0:
                    score += 10  # Médias subindo
                elif ma_short_direction < 0 and ma_long_direction < 0:
                    score -= 10  # Médias descendo
            
            return max(0, min(100, score))
            
        except Exception as e:
            self.logger.warning(f"Erro no cálculo de tendência: {str(e)}")
            return 50.0
    
    def _calculate_rsi_score(self, df: pd.DataFrame) -> float:
        """
        Calcula score baseado no RSI
        
        Args:
            df: DataFrame com dados de preços
            
        Returns:
            Score de 0-100 baseado na posição do RSI
        """
        try:
            # Calcular RSI
            delta = df['close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=self.rsi_period).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=self.rsi_period).mean()
            
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            
            current_rsi = rsi.iloc[-1]
            
            # Converter RSI para score
            if pd.isna(current_rsi):
                return 50.0
            
            # RSI próximo a 50 é neutro (score 50)
            # RSI entre 30-70 é normal
            # RSI < 30 = oversold = potencial compra
            # RSI > 70 = overbought = potencial venda
            
            if current_rsi <= self.rsi_oversold:
                # Oversold - potencial de alta
                score = 70 + (30 - current_rsi) * 1.5
            elif current_rsi >= self.rsi_overbought:
                # Overbought - potencial de queda
                score = 30 - (current_rsi - 70) * 1.5
            else:
                # Zona normal - score baseado na posição
                if current_rsi > 50:
                    score = 50 + (current_rsi - 50) * 0.5
                else:
                    score = 50 - (50 - current_rsi) * 0.5
            
            return max(0, min(100, score))
            
        except Exception as e:
            self.logger.warning(f"Erro no cálculo do RSI: {str(e)}")
            return 50.0
    
    def _calculate_volume_score(self, df: pd.DataFrame) -> float:
        """
        Calcula score baseado na análise de volume
        
        Args:
            df: DataFrame com dados de preços e volume
            
        Returns:
            Score de 0-100 baseado no padrão de volume
        """
        try:
            # Média de volume dos últimos 20 dias
            avg_volume = df['volume'].rolling(window=20).mean()
            current_volume = df['volume'].iloc[-1]
            recent_avg = avg_volume.iloc[-1]
            
            if pd.isna(recent_avg) or recent_avg == 0:
                return 50.0
            
            # Ratio volume atual vs média
            volume_ratio = current_volume / recent_avg
            
            # Score baseado no volume relativo
            score = 50.0
            
            if volume_ratio >= 2.0:
                score += 25  # Volume muito alto
            elif volume_ratio >= 1.5:
                score += 15  # Volume alto
            elif volume_ratio >= 1.2:
                score += 10  # Volume acima da média
            elif volume_ratio <= 0.5:
                score -= 15  # Volume muito baixo
            elif volume_ratio <= 0.8:
                score -= 10  # Volume baixo
            
            # Tendência de volume (últimos 5 dias)
            if len(df) >= 5:
                volume_trend = df['volume'].iloc[-5:].mean() / df['volume'].iloc[-10:-5].mean()
                if volume_trend > 1.2:
                    score += 10  # Volume crescente
                elif volume_trend < 0.8:
                    score -= 5   # Volume decrescente
            
            return max(0, min(100, score))
            
        except Exception as e:
            self.logger.warning(f"Erro no cálculo de volume: {str(e)}")
            return 50.0
    
    def _calculate_momentum_score(self, df: pd.DataFrame) -> float:
        """
        Calcula score de momentum baseado na variação de preços
        
        Args:
            df: DataFrame com dados de preços
            
        Returns:
            Score de 0-100 baseado no momentum
        """
        try:
            # Momentum de diferentes períodos
            current_price = df['close'].iloc[-1]
            
            # Variação em 5, 10 e 20 dias
            price_5d_ago = df['close'].iloc[-6] if len(df) >= 6 else current_price
            price_10d_ago = df['close'].iloc[-11] if len(df) >= 11 else current_price
            price_20d_ago = df['close'].iloc[-21] if len(df) >= 21 else current_price
            
            # Calcular retornos
            return_5d = (current_price / price_5d_ago - 1) * 100 if price_5d_ago > 0 else 0
            return_10d = (current_price / price_10d_ago - 1) * 100 if price_10d_ago > 0 else 0
            return_20d = (current_price / price_20d_ago - 1) * 100 if price_20d_ago > 0 else 0
            
            # Score baseado nos retornos (pesos diferentes para cada período)
            momentum_score = (
                return_5d * 0.5 +    # 50% peso para 5 dias
                return_10d * 0.3 +   # 30% peso para 10 dias
                return_20d * 0.2     # 20% peso para 20 dias
            )
            
            # Converter para escala 0-100
            # Momentum de +10% = score 100, -10% = score 0
            score = 50 + (momentum_score * 2.5)
            
            return max(0, min(100, score))
            
        except Exception as e:
            self.logger.warning(f"Erro no cálculo de momentum: {str(e)}")
            return 50.0
    
    def get_technical_summary(self, stock_code: str, agent_response: str) -> Dict:
        """
        Retorna resumo completo da análise técnica
        
        Args:
            stock_code: Código da ação
            agent_response: Resposta do agente com dados
            
        Returns:
            Dict com resumo completo da análise técnica
        """
        try:
            price_data = self._extract_price_data(agent_response)
            
            if not price_data:
                return {"error": "Dados insuficientes para análise técnica"}
            
            df = pd.DataFrame(price_data)
            
            # Calcular todos os componentes
            trend_score = self._calculate_trend_score(df)
            rsi_score = self._calculate_rsi_score(df)
            volume_score = self._calculate_volume_score(df)
            momentum_score = self._calculate_momentum_score(df)
            
            # Score final
            final_score = (
                trend_score * self.weights["trend"] +
                rsi_score * self.weights["rsi"] +
                volume_score * self.weights["volume"] +
                momentum_score * self.weights["momentum"]
            )
            
            # Calcular indicadores atuais
            current_price = df['close'].iloc[-1]
            ma_20 = df['close'].rolling(20).mean().iloc[-1]
            ma_50 = df['close'].rolling(50).mean().iloc[-1] if len(df) >= 50 else None
            
            # RSI atual
            delta = df['close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            current_rsi = rsi.iloc[-1] if not pd.isna(rsi.iloc[-1]) else None
            
            return {
                "stock_code": stock_code,
                "final_score": round(final_score, 1),
                "components": {
                    "trend_score": round(trend_score, 1),
                    "rsi_score": round(rsi_score, 1),
                    "volume_score": round(volume_score, 1),
                    "momentum_score": round(momentum_score, 1)
                },
                "indicators": {
                    "current_price": current_price,
                    "ma_20": round(ma_20, 2) if not pd.isna(ma_20) else None,
                    "ma_50": round(ma_50, 2) if ma_50 and not pd.isna(ma_50) else None,
                    "rsi": round(current_rsi, 1) if current_rsi else None,
                    "current_volume": df['volume'].iloc[-1],
                    "avg_volume_20d": round(df['volume'].rolling(20).mean().iloc[-1], 0)
                },
                "signals": self._generate_technical_signals(df),
                "analysis_timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Erro no resumo técnico para {stock_code}: {str(e)}")
            return {"error": f"Erro na análise técnica: {str(e)}"}
    
    def _generate_technical_signals(self, df: pd.DataFrame) -> List[str]:
        """Gera sinais técnicos baseados nos indicadores"""
        signals = []
        
        try:
            current_price = df['close'].iloc[-1]
            ma_20 = df['close'].rolling(20).mean().iloc[-1]
            
            # Sinais de médias móveis
            if current_price > ma_20:
                signals.append("Preço acima da média móvel 20")
            else:
                signals.append("Preço abaixo da média móvel 20")
            
            # Sinais de RSI
            delta = df['close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            current_rsi = rsi.iloc[-1]
            
            if not pd.isna(current_rsi):
                if current_rsi > 70:
                    signals.append("RSI indica sobrecompra")
                elif current_rsi < 30:
                    signals.append("RSI indica sobrevenda")
                else:
                    signals.append("RSI em zona neutra")
            
            # Sinais de volume
            current_volume = df['volume'].iloc[-1]
            avg_volume = df['volume'].rolling(20).mean().iloc[-1]
            
            if current_volume > avg_volume * 1.5:
                signals.append("Volume acima da média")
            elif current_volume < avg_volume * 0.7:
                signals.append("Volume abaixo da média")
            
            # Sinal de momentum
            if len(df) >= 6:
                price_5d_ago = df['close'].iloc[-6]
                momentum = (current_price / price_5d_ago - 1) * 100
                
                if momentum > 5:
                    signals.append("Momentum positivo forte")
                elif momentum > 2:
                    signals.append("Momentum positivo")
                elif momentum < -5:
                    signals.append("Momentum negativo forte")
                elif momentum < -2:
                    signals.append("Momentum negativo")
            
        except Exception as e:
            self.logger.warning(f"Erro ao gerar sinais técnicos: {str(e)}")
            signals.append("Erro na análise de sinais")
        
        return signals[:5]  # Limitar a 5 sinais principais


# Exemplo de uso
if __name__ == "__main__":
    analyzer = TechnicalAnalyzer()
    
    # Dados mock para teste
    mock_response = """
    Dados históricos para PETR4:
    [
        {"date": "2025-01-01", "close": 30.50, "volume": 1500000, "high": 31.00, "low": 30.00},
        {"date": "2025-01-02", "close": 30.75, "volume": 1600000, "high": 31.25, "low": 30.25}
    ]
    """
    
    # Teste de cálculo de score
    import asyncio
    
    async def test():
        score = await analyzer.calculate_score("PETR4", mock_response)
        print(f"Score técnico: {score}")
        
        summary = analyzer.get_technical_summary("PETR4", mock_response)
        print(f"Resumo: {summary}")
    
    asyncio.run(test())
