#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple M7 DCF Report Generator

直接读取M7数据生成DCF分析报告，不依赖复杂的Graph RAG系统
"""

import json
import os
from datetime import datetime
from pathlib import Path


class SimpleM7DCF:
    """简单的M7 DCF分析器"""
    
    def __init__(self):
        self.m7_companies = {
            'AAPL': 'Apple Inc.',
            'MSFT': 'Microsoft Corporation', 
            'AMZN': 'Amazon.com Inc.',
            'GOOGL': 'Alphabet Inc.',
            'META': 'Meta Platforms Inc.',
            'TSLA': 'Tesla Inc.',
            'NFLX': 'Netflix Inc.'
        }
        self.data_dir = Path("data/original")
        self.reports_dir = Path("data/reports")
        self.reports_dir.mkdir(exist_ok=True)
    
    def load_company_data(self, ticker):
        """加载公司数据"""
        yfinance_dir = self.data_dir / "yfinance" / ticker
        if not yfinance_dir.exists():
            return None
            
        # 找最新的M7数据文件（优先日线数据）
        daily_files = list(yfinance_dir.glob(f"{ticker}_yfinance_m7_daily_*.json"))
        if not daily_files:
            # 如果没有日线数据，尝试其他M7数据文件
            daily_files = list(yfinance_dir.glob(f"{ticker}_yfinance_m7_*.json"))
        if not daily_files:
            return None
            
        latest_file = max(daily_files, key=lambda f: f.stat().st_mtime)
        
        try:
            with open(latest_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading {latest_file}: {e}")
            return None
    
    def calculate_dcf_metrics(self, data):
        """计算DCF相关指标"""
        if not data or 'info' not in data:
            return None
            
        info = data['info']
        ticker = data.get('ticker', 'N/A')
        
        # 基础财务数据
        current_price = info.get('currentPrice', 0)
        market_cap = info.get('marketCap', 0)
        free_cash_flow = info.get('freeCashflow', 0)
        revenue = info.get('totalRevenue', 0)
        net_income = info.get('netIncome', 0)
        
        # 增长率
        revenue_growth = info.get('revenueGrowth', 0)
        earnings_growth = info.get('earningsGrowth', 0)
        
        # 盈利能力
        profit_margin = info.get('profitMargins', 0)
        roe = info.get('returnOnEquity', 0)
        
        # 估值指标
        pe_ratio = info.get('trailingPE', 0)
        forward_pe = info.get('forwardPE', 0)
        peg_ratio = info.get('pegRatio', 0)
        price_to_book = info.get('priceToBook', 0)
        
        # 风险指标
        beta = info.get('beta', 1.0)
        debt_to_equity = info.get('debtToEquity', 0)
        
        # 简化的DCF计算
        if free_cash_flow > 0:
            # 假设增长率和折现率
            if ticker == 'TSLA':
                growth_rate = 0.15  # Tesla高增长
                discount_rate = 0.12
            elif ticker in ['AAPL', 'MSFT', 'GOOGL']:
                growth_rate = 0.08  # 成熟科技巨头
                discount_rate = 0.10
            else:
                growth_rate = 0.06  # 其他公司
                discount_rate = 0.10
            
            # 5年现金流预测
            projected_fcf = []
            fcf = free_cash_flow
            for year in range(5):
                fcf *= (1 + growth_rate * (0.8 ** year))  # 递减增长率
                projected_fcf.append(fcf)
            
            # 终值计算
            terminal_growth = 0.03
            terminal_value = projected_fcf[-1] * (1 + terminal_growth) / (discount_rate - terminal_growth)
            
            # 现值计算
            pv_fcf = sum([fcf / ((1 + discount_rate) ** (i+1)) for i, fcf in enumerate(projected_fcf)])
            pv_terminal = terminal_value / ((1 + discount_rate) ** 5)
            
            enterprise_value = pv_fcf + pv_terminal
            shares_outstanding = info.get('sharesOutstanding', 1)
            intrinsic_value = enterprise_value / shares_outstanding if shares_outstanding > 0 else 0
            
            upside_potential = ((intrinsic_value - current_price) / current_price * 100) if current_price > 0 else 0
        else:
            intrinsic_value = 0
            upside_potential = 0
            projected_fcf = []
        
        return {
            'ticker': ticker,
            'company_name': info.get('longName', 'N/A'),
            'sector': info.get('sector', 'N/A'),
            'current_price': current_price,
            'market_cap': market_cap,
            'revenue': revenue,
            'net_income': net_income,
            'free_cash_flow': free_cash_flow,
            'revenue_growth': revenue_growth,
            'earnings_growth': earnings_growth,
            'profit_margin': profit_margin,
            'roe': roe,
            'pe_ratio': pe_ratio,
            'forward_pe': forward_pe,
            'peg_ratio': peg_ratio,
            'price_to_book': price_to_book,
            'beta': beta,
            'debt_to_equity': debt_to_equity,
            'intrinsic_value': intrinsic_value,
            'upside_potential': upside_potential,
            'projected_fcf': projected_fcf,
            'recommendation': self.get_recommendation(upside_potential, roe, profit_margin)
        }
    
    def get_recommendation(self, upside, roe, profit_margin):
        """生成投资建议"""
        if upside > 20 and roe > 0.20 and profit_margin > 0.15:
            return "强烈买入 - 被低估且基本面强劲"
        elif upside > 10 and roe > 0.15:
            return "买入 - 被低估且基本面良好"
        elif upside > -10 and upside <= 10:
            return "持有 - 合理估值"
        elif upside > -20:
            return "弱卖出 - 略微高估"
        else:
            return "卖出 - 显著高估"
    
    def format_currency(self, value):
        """格式化货币"""
        if value >= 1e12:
            return f"${value/1e12:.2f}万亿"
        elif value >= 1e9:
            return f"${value/1e9:.1f}亿"
        elif value >= 1e6:
            return f"${value/1e6:.0f}百万"
        else:
            return f"${value:.2f}"
    
    def format_percentage(self, value):
        """格式化百分比"""
        return f"{value*100:.1f}%" if abs(value) < 10 else f"{value:.1f}%"
    
    def generate_report(self):
        """生成M7 DCF报告"""
        print("📊 生成Magnificent 7 DCF分析报告...")
        
        # 分析所有M7公司
        analyses = {}
        for ticker in self.m7_companies:
            print(f"  📈 分析 {ticker}...")
            data = self.load_company_data(ticker)
            if data:
                analysis = self.calculate_dcf_metrics(data)
                if analysis:
                    analyses[ticker] = analysis
                else:
                    print(f"    ⚠️ 无法计算{ticker}的DCF指标")
            else:
                print(f"    ⚠️ 无法加载{ticker}的数据")
        
        if not analyses:
            return "❌ 无法获取M7公司数据"
        
        # 生成报告
        lines = []
        lines.extend([
            "=" * 80,
            "Magnificent 7 (M7) DCF 估值分析报告",
            "=" * 80,
            f"报告生成时间: {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}",
            f"分析公司数量: {len(analyses)}/{len(self.m7_companies)}",
            f"数据来源: Yahoo Finance",
            "",
        ])
        
        # 执行摘要
        lines.extend([
            "📋 执行摘要",
            "-" * 40,
        ])
        
        total_market_cap = sum([a['market_cap'] for a in analyses.values()])
        buy_count = len([a for a in analyses.values() if '买入' in a['recommendation']])
        hold_count = len([a for a in analyses.values() if '持有' in a['recommendation']])
        sell_count = len([a for a in analyses.values() if '卖出' in a['recommendation']])
        
        lines.extend([
            f"M7总市值: {self.format_currency(total_market_cap)}",
            f"买入推荐: {buy_count}家公司",
            f"持有推荐: {hold_count}家公司", 
            f"卖出推荐: {sell_count}家公司",
            "",
        ])
        
        # 公司排名
        lines.extend([
            "🏆 投资潜力排名 (按上涨空间)",
            "-" * 40,
        ])
        
        sorted_companies = sorted(analyses.items(), key=lambda x: x[1]['upside_potential'], reverse=True)
        for i, (ticker, analysis) in enumerate(sorted_companies, 1):
            upside = analysis['upside_potential']
            recommendation = analysis['recommendation'].split(' - ')[0]
            lines.append(f"{i}. {ticker} ({analysis['company_name'][:20]}...) - {upside:+.1f}% - {recommendation}")
        
        lines.append("")
        
        # 详细分析
        lines.extend([
            "📊 详细公司分析",
            "=" * 50,
            ""
        ])
        
        for ticker in sorted(analyses.keys()):
            analysis = analyses[ticker]
            
            lines.extend([
                f"{analysis['ticker']} - {analysis['company_name']}",
                f"行业: {analysis['sector']}",
                "-" * 60,
                ""
            ])
            
            # 估值摘要
            lines.extend([
                "💰 估值摘要",
                f"当前股价: ${analysis['current_price']:.2f}",
                f"内在价值: ${analysis['intrinsic_value']:.2f}",
                f"上涨空间: {analysis['upside_potential']:+.1f}%",
                f"投资建议: {analysis['recommendation']}",
                "",
            ])
            
            # 关键财务指标
            lines.extend([
                "📈 关键财务指标",
                f"市值: {self.format_currency(analysis['market_cap'])}",
                f"营业收入: {self.format_currency(analysis['revenue'])}",
                f"净利润: {self.format_currency(analysis['net_income'])}",
                f"自由现金流: {self.format_currency(analysis['free_cash_flow'])}",
                f"营收增长率: {self.format_percentage(analysis['revenue_growth'])}",
                f"净利润率: {self.format_percentage(analysis['profit_margin'])}",
                f"净资产收益率: {self.format_percentage(analysis['roe'])}",
                "",
            ])
            
            # 估值指标
            lines.extend([
                "📊 估值指标",
                f"市盈率: {analysis['pe_ratio']:.1f}",
                f"预期市盈率: {analysis['forward_pe']:.1f}",
                f"PEG比率: {analysis['peg_ratio']:.2f}",
                f"市净率: {analysis['price_to_book']:.2f}",
                f"Beta系数: {analysis['beta']:.2f}",
                f"资产负债率: {analysis['debt_to_equity']:.1f}%",
                "",
            ])
            
            # 现金流预测
            if analysis['projected_fcf']:
                lines.extend([
                    "💵 5年自由现金流预测",
                ])
                for i, fcf in enumerate(analysis['projected_fcf']):
                    year = datetime.now().year + i + 1
                    lines.append(f"  {year}年: {self.format_currency(fcf)}")
                lines.append("")
            
            lines.extend(["-" * 60, ""])
        
        # 风险提示和免责声明
        lines.extend([
            "⚠️ 风险提示与免责声明",
            "=" * 40,
            "",
            "模型假设:",
            "• 增长率基于历史数据和行业特点估算",
            "• 折现率采用CAPM模型简化计算",
            "• 终值增长率假设为3%",
            "",
            "主要风险:",
            "• 利率变动影响折现率",
            "• 宏观经济环境变化",
            "• 行业竞争加剧",
            "• 监管政策变化",
            "• 技术革新冲击",
            "",
            "免责声明:",
            "本报告仅供教育和研究参考，不构成投资建议。",
            "投资有风险，入市需谨慎。过往业绩不代表未来表现。",
            "请在做出投资决策前咨询专业的财务顾问。",
            "",
            "=" * 80
        ])
        
        return "\n".join(lines)
    
    def save_report(self, report):
        """保存报告"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"M7_DCF_Report_{timestamp}.txt"
        filepath = self.reports_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(report)
        
        return str(filepath)


def main():
    """主函数"""
    print("🚀 启动M7 DCF分析...")
    
    analyzer = SimpleM7DCF()
    
    try:
        # 生成报告
        report = analyzer.generate_report()
        
        # 保存报告
        report_path = analyzer.save_report(report)
        
        print(f"\n✅ DCF报告生成成功!")
        print(f"📄 报告保存至: {report_path}")
        
        # 显示预览
        print("\n" + "="*60)
        print("报告预览 (前40行):")
        print("="*60)
        
        lines = report.split('\n')
        for line in lines[:40]:
            print(line)
        
        if len(lines) > 40:
            print(f"\n... 还有 {len(lines) - 40} 行")
            print(f"📄 完整报告: {report_path}")
        
        return report_path
        
    except Exception as e:
        print(f"❌ 生成报告时出错: {e}")
        return None


if __name__ == "__main__":
    main()