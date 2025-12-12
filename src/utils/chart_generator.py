"""Generate charts and graphs for PowerPoint presentations."""

import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import tempfile

logger = logging.getLogger(__name__)


class ChartGenerator:
    """Generate charts for financial and metric data."""
    
    def __init__(self):
        self.temp_dir = Path(tempfile.gettempdir()) / "techscope_charts"
        self.temp_dir.mkdir(exist_ok=True)
    
    def create_revenue_chart(self, data: Dict, output_path: Optional[Path] = None) -> Optional[Path]:
        """
        Create a revenue growth chart.
        
        Args:
            data: Dict with revenue data (e.g., {"2023": 500000, "2024": 1200000})
            output_path: Optional output path
            
        Returns:
            Path to chart image file
        """
        try:
            import matplotlib.pyplot as plt
            import matplotlib
            matplotlib.use('Agg')  # Non-interactive backend
            
            years = list(data.keys())
            values = [float(str(v).replace('$', '').replace(',', '').replace('K', '000').replace('M', '000000')) 
                     for v in data.values()]
            
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.plot(years, values, marker='o', linewidth=3, markersize=10, color='#3b82f6')
            ax.fill_between(years, values, alpha=0.3, color='#3b82f6')
            ax.set_xlabel('Year', fontsize=12, fontweight='bold')
            ax.set_ylabel('Revenue ($)', fontsize=12, fontweight='bold')
            ax.set_title('Revenue Growth', fontsize=16, fontweight='bold', pad=20)
            ax.grid(True, alpha=0.3)
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            
            # Format y-axis as currency
            ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x/1000:.0f}K' if x < 1000000 else f'${x/1000000:.1f}M'))
            
            plt.tight_layout()
            
            if not output_path:
                output_path = self.temp_dir / "revenue_chart.png"
            
            plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
            plt.close()
            
            logger.info(f"Created revenue chart: {output_path}")
            return output_path
            
        except ImportError:
            logger.warning("matplotlib not installed. Charts will be skipped.")
            return None
        except Exception as e:
            logger.error(f"Error creating revenue chart: {e}", exc_info=True)
            return None
    
    def create_metrics_chart(self, metrics: Dict, output_path: Optional[Path] = None) -> Optional[Path]:
        """
        Create a bar chart for key metrics.
        
        Args:
            metrics: Dict with metric names and values
            output_path: Optional output path
            
        Returns:
            Path to chart image file
        """
        try:
            import matplotlib.pyplot as plt
            import matplotlib
            matplotlib.use('Agg')
            
            names = list(metrics.keys())
            values = [float(str(v).replace('%', '').replace('$', '').replace(',', '')) 
                     for v in metrics.values()]
            
            fig, ax = plt.subplots(figsize=(10, 6))
            bars = ax.barh(names, values, color='#10b981', alpha=0.8)
            ax.set_xlabel('Value', fontsize=12, fontweight='bold')
            ax.set_title('Key Metrics', fontsize=16, fontweight='bold', pad=20)
            ax.grid(True, alpha=0.3, axis='x')
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            
            # Add value labels on bars
            for i, (bar, val) in enumerate(zip(bars, values)):
                ax.text(val, i, f' {val}', va='center', fontweight='bold')
            
            plt.tight_layout()
            
            if not output_path:
                output_path = self.temp_dir / "metrics_chart.png"
            
            plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
            plt.close()
            
            logger.info(f"Created metrics chart: {output_path}")
            return output_path
            
        except ImportError:
            logger.warning("matplotlib not installed. Charts will be skipped.")
            return None
        except Exception as e:
            logger.error(f"Error creating metrics chart: {e}", exc_info=True)
            return None
    
    def should_include_financial_data(self, company_data: Dict) -> Tuple[bool, str]:
        """
        Intelligently determine if financial data should be included.
        
        Args:
            company_data: Company data dictionary
            
        Returns:
            Tuple of (should_include, reason)
        """
        stage = company_data.get('company_stage', '').lower()
        
        # If just an idea, don't include financials
        if 'idea' in stage:
            return False, "Company is in idea stage - financials not applicable"
        
        revenue = company_data.get('annual_revenue', '')
        ebitda = company_data.get('ebitda', '')
        
        # Check if revenue exists and is meaningful
        if revenue and revenue.lower() not in ['n/a', 'not applicable', 'none', '']:
            try:
                # Try to parse revenue value
                rev_val = str(revenue).replace('$', '').replace(',', '').replace('K', '000').replace('M', '000000')
                rev_num = float(rev_val)
                if rev_num > 0:
                    return True, "Revenue data available and positive"
            except:
                pass
        
        # Check EBITDA - if negative but small, might still include
        if ebitda and ebitda.lower() not in ['n/a', 'not applicable', 'none', '']:
            try:
                ebitda_val = str(ebitda).replace('$', '').replace(',', '').replace('K', '000').replace('M', '000000')
                ebitda_num = float(ebitda_val)
                # Include if positive or small negative (investing in growth)
                if ebitda_num > -100000:  # Less than $100K loss
                    return True, "EBITDA data available (investing in growth)"
            except:
                pass
        
        # If operating but no good financials, don't include
        if 'operating' in stage or 'established' in stage:
            return False, "Operating but financial data not strong enough to highlight"
        
        return False, "No meaningful financial data to include"
    
    def get_charts_for_slides(self, company_data: Dict) -> Dict[str, Optional[Path]]:
        """
        Generate all relevant charts based on company data.
        
        Args:
            company_data: Company data dictionary
            
        Returns:
            Dict mapping chart types to file paths
        """
        charts = {}
        
        # Revenue chart
        if company_data.get('annual_revenue'):
            try:
                # Try to create historical revenue data
                revenue = company_data.get('annual_revenue', '')
                if revenue and revenue.lower() not in ['n/a', 'not applicable', 'none', '']:
                    # Create simple revenue chart with current year
                    from datetime import datetime
                    current_year = str(datetime.now().year)
                    charts['revenue'] = self.create_revenue_chart({current_year: revenue})
            except Exception as e:
                logger.warning(f"Could not create revenue chart: {e}")
        
        # Growth chart
        if company_data.get('growth_rate'):
            try:
                growth = company_data.get('growth_rate', '')
                if growth and '%' in str(growth):
                    # Parse growth rate and create chart
                    growth_val = float(str(growth).replace('%', '').replace('MoM', '').replace('YoY', '').strip())
                    # Create simple growth chart
                    charts['growth'] = self.create_growth_chart({"Current": growth_val})
            except Exception as e:
                logger.warning(f"Could not create growth chart: {e}")
        
        # Projection chart
        if company_data.get('projected_revenue') and company_data.get('annual_revenue'):
            try:
                from datetime import datetime
                historical = {str(datetime.now().year - 1): company_data.get('annual_revenue')}
                # Parse projected revenue
                projected_text = company_data.get('projected_revenue', '')
                # Simple parsing - could be enhanced
                if '12' in projected_text or '24' in projected_text:
                    charts['projection'] = self.create_projection_chart(
                        historical,
                        {str(datetime.now().year + 1): projected_text}
                    )
            except Exception as e:
                logger.warning(f"Could not create projection chart: {e}")
        
        # Metrics chart
        if company_data.get('key_metrics'):
            try:
                metrics_text = company_data.get('key_metrics', '')
                # Parse metrics (CAC, LTV, Churn, etc.)
                metrics = {}
                for line in metrics_text.split('\n'):
                    if ':' in line:
                        key, val = line.split(':', 1)
                        key = key.strip()
                        val = val.strip()
                        metrics[key] = val
                if metrics:
                    charts['metrics'] = self.create_metrics_chart(metrics)
            except Exception as e:
                logger.warning(f"Could not create metrics chart: {e}")
        
        return charts
    
    def create_growth_chart(self, data: Dict, output_path: Optional[Path] = None) -> Optional[Path]:
        """
        Create a growth rate chart (MoM, YoY growth).
        
        Args:
            data: Dict with growth data (e.g., {"Jan": 10, "Feb": 15, "Mar": 20} for % growth)
            output_path: Optional output path
            
        Returns:
            Path to chart image file
        """
        try:
            import matplotlib.pyplot as plt
            import matplotlib
            matplotlib.use('Agg')
            
            periods = list(data.keys())
            values = [float(str(v).replace('%', '')) for v in data.values()]
            
            fig, ax = plt.subplots(figsize=(10, 6))
            bars = ax.bar(periods, values, color='#10b981', alpha=0.8, edgecolor='#059669', linewidth=2)
            ax.set_xlabel('Period', fontsize=12, fontweight='bold')
            ax.set_ylabel('Growth Rate (%)', fontsize=12, fontweight='bold')
            ax.set_title('Growth Trajectory', fontsize=16, fontweight='bold', pad=20)
            ax.grid(True, alpha=0.3, axis='y')
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            
            # Add value labels on bars
            for bar, val in zip(bars, values):
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{val:.1f}%', ha='center', va='bottom', fontweight='bold', fontsize=10)
            
            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()
            
            if not output_path:
                output_path = self.temp_dir / "growth_chart.png"
            
            plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
            plt.close()
            
            logger.info(f"Created growth chart: {output_path}")
            return output_path
            
        except ImportError:
            logger.warning("matplotlib not installed. Charts will be skipped.")
            return None
        except Exception as e:
            logger.error(f"Error creating growth chart: {e}", exc_info=True)
            return None
    
    def create_projection_chart(self, historical: Dict, projected: Dict, output_path: Optional[Path] = None) -> Optional[Path]:
        """
        Create a revenue projection chart with historical and projected data.
        
        Args:
            historical: Dict with historical revenue (e.g., {"2023": 500000})
            projected: Dict with projected revenue (e.g., {"2024": 2000000, "2025": 5000000})
            output_path: Optional output path
            
        Returns:
            Path to chart image file
        """
        try:
            import matplotlib.pyplot as plt
            import matplotlib
            matplotlib.use('Agg')
            
            # Combine data
            all_periods = sorted(list(set(list(historical.keys()) + list(projected.keys()))))
            historical_values = []
            projected_values = []
            
            for period in all_periods:
                if period in historical:
                    val = float(str(historical[period]).replace('$', '').replace(',', '').replace('K', '000').replace('M', '000000'))
                    historical_values.append(val)
                    projected_values.append(None)
                elif period in projected:
                    val = float(str(projected[period]).replace('$', '').replace(',', '').replace('K', '000').replace('M', '000000'))
                    historical_values.append(None)
                    projected_values.append(val)
            
            fig, ax = plt.subplots(figsize=(10, 6))
            
            # Plot historical data
            hist_periods = [p for p, v in zip(all_periods, historical_values) if v is not None]
            hist_values = [v for v in historical_values if v is not None]
            if hist_periods:
                ax.plot(hist_periods, hist_values, marker='o', linewidth=3, markersize=10, 
                       color='#3b82f6', label='Historical', zorder=3)
                ax.fill_between(hist_periods, hist_values, alpha=0.3, color='#3b82f6')
            
            # Plot projected data
            proj_periods = [p for p, v in zip(all_periods, projected_values) if v is not None]
            proj_values = [v for v in projected_values if v is not None]
            if proj_periods:
                ax.plot(proj_periods, proj_values, marker='s', linewidth=3, markersize=10, 
                       color='#10b981', label='Projected', linestyle='--', zorder=3)
                ax.fill_between(proj_periods, proj_values, alpha=0.2, color='#10b981')
            
            ax.set_xlabel('Year', fontsize=12, fontweight='bold')
            ax.set_ylabel('Revenue ($)', fontsize=12, fontweight='bold')
            ax.set_title('Revenue Projections', fontsize=16, fontweight='bold', pad=20)
            ax.legend(loc='upper left', fontsize=11)
            ax.grid(True, alpha=0.3)
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            
            # Format y-axis as currency
            ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x/1000:.0f}K' if x < 1000000 else f'${x/1000000:.1f}M'))
            
            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()
            
            if not output_path:
                output_path = self.temp_dir / "projection_chart.png"
            
            plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
            plt.close()
            
            logger.info(f"Created projection chart: {output_path}")
            return output_path
            
        except ImportError:
            logger.warning("matplotlib not installed. Charts will be skipped.")
            return None
        except Exception as e:
            logger.error(f"Error creating projection chart: {e}", exc_info=True)
            return None
    
    def get_charts_for_slides(self, company_data: Dict) -> Dict[str, Optional[Path]]:
        """
        Generate all relevant charts based on company data.
        
        Args:
            company_data: Company data dictionary
            
        Returns:
            Dict mapping chart types to file paths
        """
        charts = {}
        
        # Revenue chart
        if company_data.get('annual_revenue'):
            try:
                # Try to create historical revenue data
                revenue = company_data.get('annual_revenue', '')
                if revenue and revenue.lower() not in ['n/a', 'not applicable', 'none', '']:
                    # Create simple revenue chart with current year
                    from datetime import datetime
                    current_year = str(datetime.now().year)
                    charts['revenue'] = self.create_revenue_chart({current_year: revenue})
            except Exception as e:
                logger.warning(f"Could not create revenue chart: {e}")
        
        # Growth chart
        if company_data.get('growth_rate'):
            try:
                growth = company_data.get('growth_rate', '')
                if growth and '%' in str(growth):
                    # Parse growth rate and create chart
                    growth_val = float(str(growth).replace('%', '').replace('MoM', '').replace('YoY', '').strip())
                    # Create simple growth chart
                    charts['growth'] = self.create_growth_chart({"Current": growth_val})
            except Exception as e:
                logger.warning(f"Could not create growth chart: {e}")
        
        # Projection chart
        if company_data.get('projected_revenue') and company_data.get('annual_revenue'):
            try:
                historical = {str(datetime.now().year - 1): company_data.get('annual_revenue')}
                # Parse projected revenue
                projected_text = company_data.get('projected_revenue', '')
                # Simple parsing - could be enhanced
                if '12' in projected_text or '24' in projected_text:
                    charts['projection'] = self.create_projection_chart(
                        historical,
                        {str(datetime.now().year + 1): projected_text}
                    )
            except Exception as e:
                logger.warning(f"Could not create projection chart: {e}")
        
        # Metrics chart
        if company_data.get('key_metrics'):
            try:
                metrics_text = company_data.get('key_metrics', '')
                # Parse metrics (CAC, LTV, Churn, etc.)
                metrics = {}
                for line in metrics_text.split('\n'):
                    if ':' in line:
                        key, val = line.split(':', 1)
                        key = key.strip()
                        val = val.strip()
                        metrics[key] = val
                if metrics:
                    charts['metrics'] = self.create_metrics_chart(metrics)
            except Exception as e:
                logger.warning(f"Could not create metrics chart: {e}")
        
        return charts

