"""Auto-generate charts for PowerPoint slides from data."""

import logging
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from io import BytesIO
import numpy as np

logger = logging.getLogger(__name__)


class ChartGenerator:
    """Generate charts automatically from slide content."""
    
    def __init__(self):
        """Initialize chart generator."""
        self.chart_cache_dir = Path("exports/charts")
        self.chart_cache_dir.mkdir(parents=True, exist_ok=True)
        logger.info("ChartGenerator initialized")
    
    def extract_numbers_from_text(self, text: str) -> List[Dict]:
        """
        Extract numbers and their context from text.
        
        Args:
            text: Text to analyze
            
        Returns:
            List of dictionaries with number, value, and context
        """
        # Pattern to match numbers with context (e.g., "$10M", "45%", "1000 users")
        patterns = [
            (r'\$(\d+(?:\.\d+)?)\s*([KMkm]|million|billion)?', 'currency'),
            (r'(\d+(?:\.\d+)?)\s*%', 'percentage'),
            (r'(\d+(?:\.\d+)?)\s*(users|customers|revenue|MRR|ARR)', 'metric'),
            (r'(\d+(?:\.\d+)?)\s*([KMkm])', 'abbreviated'),
            (r'(\d+(?:\.\d+)?)', 'number')
        ]
        
        numbers = []
        for pattern, num_type in patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                value_str = match.group(1)
                try:
                    value = float(value_str)
                    # Get context (words around the number)
                    start = max(0, match.start() - 20)
                    end = min(len(text), match.end() + 20)
                    context = text[start:end].strip()
                    
                    numbers.append({
                        "value": value,
                        "type": num_type,
                        "context": context,
                        "full_match": match.group(0)
                    })
                except ValueError:
                    continue
        
        return numbers
    
    def detect_chart_type(self, slide_title: str, slide_content: str, 
                         key_points: List[str]) -> Optional[str]:
        """
        Detect what type of chart would be appropriate.
        
        Args:
            slide_title: Slide title
            slide_content: Slide content
            key_points: Key points list
            
        Returns:
            Chart type: 'pie', 'bar', 'line', 'comparison', or None
        """
        text = f"{slide_title} {slide_content} {' '.join(key_points)}".lower()
        
        # Market size indicators
        if any(word in text for word in ['tam', 'sam', 'som', 'market size', 'market opportunity']):
            return 'pie'
        
        # Growth/traction indicators
        if any(word in text for word in ['growth', 'traction', 'revenue', 'users', 'over time', 'timeline']):
            return 'line'
        
        # Comparison indicators
        if any(word in text for word in ['vs', 'versus', 'compare', 'competitor', 'competition']):
            return 'bar'
        
        # Financial indicators
        if any(word in text for word in ['financial', 'revenue', 'cost', 'profit', 'budget']):
            return 'bar'
        
        # Multiple metrics
        numbers = self.extract_numbers_from_text(text)
        if len(numbers) >= 3:
            return 'bar'  # Default to bar chart for multiple metrics
        
        return None
    
    def generate_pie_chart(self, data: Dict[str, float], title: str, 
                          output_path: Optional[Path] = None) -> Optional[Path]:
        """
        Generate a pie chart.
        
        Args:
            data: Dictionary with labels and values
            title: Chart title
            output_path: Optional output path
            
        Returns:
            Path to saved chart image
        """
        try:
            fig, ax = plt.subplots(figsize=(8, 6))
            
            labels = list(data.keys())
            values = list(data.values())
            colors = plt.cm.Set3(np.linspace(0, 1, len(labels)))
            
            wedges, texts, autotexts = ax.pie(
                values,
                labels=labels,
                autopct='%1.1f%%',
                colors=colors,
                startangle=90,
                textprops={'fontsize': 10, 'fontweight': 'bold'}
            )
            
            ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
            
            plt.tight_layout()
            
            if not output_path:
                output_path = self.chart_cache_dir / f"pie_{hash(title)}.png"
            
            plt.savefig(output_path, dpi=150, bbox_inches='tight', 
                       facecolor='white', edgecolor='none')
            plt.close()
            
            logger.info(f"Generated pie chart: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error generating pie chart: {e}")
            return None
    
    def generate_bar_chart(self, data: Dict[str, float], title: str,
                           xlabel: str = "", ylabel: str = "",
                           output_path: Optional[Path] = None) -> Optional[Path]:
        """
        Generate a bar chart.
        
        Args:
            data: Dictionary with labels and values
            title: Chart title
            xlabel: X-axis label
            ylabel: Y-axis label
            output_path: Optional output path
            
        Returns:
            Path to saved chart image
        """
        try:
            fig, ax = plt.subplots(figsize=(10, 6))
            
            labels = list(data.keys())
            values = list(data.values())
            colors = plt.cm.viridis(np.linspace(0, 1, len(labels)))
            
            bars = ax.bar(labels, values, color=colors, edgecolor='white', linewidth=1.5)
            
            # Add value labels on bars
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{height:.1f}',
                       ha='center', va='bottom', fontweight='bold')
            
            ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
            if xlabel:
                ax.set_xlabel(xlabel, fontsize=11)
            if ylabel:
                ax.set_ylabel(ylabel, fontsize=11)
            
            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()
            
            if not output_path:
                output_path = self.chart_cache_dir / f"bar_{hash(title)}.png"
            
            plt.savefig(output_path, dpi=150, bbox_inches='tight',
                       facecolor='white', edgecolor='none')
            plt.close()
            
            logger.info(f"Generated bar chart: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error generating bar chart: {e}")
            return None
    
    def generate_line_chart(self, data: Dict[str, float], title: str,
                           xlabel: str = "", ylabel: str = "",
                           output_path: Optional[Path] = None) -> Optional[Path]:
        """
        Generate a line chart.
        
        Args:
            data: Dictionary with labels (x) and values (y)
            title: Chart title
            xlabel: X-axis label
            ylabel: Y-axis label
            output_path: Optional output path
            
        Returns:
            Path to saved chart image
        """
        try:
            fig, ax = plt.subplots(figsize=(10, 6))
            
            labels = list(data.keys())
            values = list(data.values())
            
            ax.plot(labels, values, marker='o', linewidth=2.5, markersize=8,
                   color='#3b82f6', markerfacecolor='#1e40af', markeredgecolor='white',
                   markeredgewidth=2)
            
            # Fill under line
            ax.fill_between(labels, values, alpha=0.3, color='#3b82f6')
            
            ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
            if xlabel:
                ax.set_xlabel(xlabel, fontsize=11)
            if ylabel:
                ax.set_ylabel(ylabel, fontsize=11)
            
            plt.xticks(rotation=45, ha='right')
            plt.grid(True, alpha=0.3, linestyle='--')
            plt.tight_layout()
            
            if not output_path:
                output_path = self.chart_cache_dir / f"line_{hash(title)}.png"
            
            plt.savefig(output_path, dpi=150, bbox_inches='tight',
                       facecolor='white', edgecolor='none')
            plt.close()
            
            logger.info(f"Generated line chart: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error generating line chart: {e}")
            return None
    
    def generate_gauge_chart(self, value: float, max_value: float, title: str,
                            output_path: Optional[Path] = None) -> Optional[Path]:
        """
        Generate a gauge/speedometer chart for metrics.
        
        Args:
            value: Current value
            max_value: Maximum value
            title: Chart title
            output_path: Optional output path
            
        Returns:
            Path to saved chart image
        """
        try:
            fig, ax = plt.subplots(figsize=(8, 6), subplot_kw=dict(projection='polar'))
            
            # Calculate percentage
            percentage = (value / max_value) * 100
            
            # Create gauge
            theta = np.linspace(0, np.pi, 100)
            r = np.ones_like(theta)
            
            # Background (gray)
            ax.fill_between(theta, 0, r, alpha=0.3, color='gray')
            
            # Fill (colored based on percentage)
            fill_theta = np.linspace(0, np.pi * (percentage / 100), int(percentage))
            fill_r = np.ones_like(fill_theta)
            color = 'green' if percentage > 70 else 'orange' if percentage > 40 else 'red'
            ax.fill_between(fill_theta, 0, fill_r, alpha=0.7, color=color)
            
            # Add value text
            ax.text(0, 0.5, f'{percentage:.0f}%', ha='center', va='center',
                   fontsize=24, fontweight='bold')
            ax.text(0, 0.3, f'{value:.1f}/{max_value:.1f}', ha='center', va='center',
                   fontsize=14)
            
            ax.set_ylim(0, 1)
            ax.set_xticks([])
            ax.set_yticks([])
            ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
            
            plt.tight_layout()
            
            if not output_path:
                output_path = self.chart_cache_dir / f"gauge_{hash(title)}.png"
            
            plt.savefig(output_path, dpi=150, bbox_inches='tight',
                       facecolor='white', edgecolor='none')
            plt.close()
            
            logger.info(f"Generated gauge chart: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error generating gauge chart: {e}")
            return None
    
    def generate_funnel_chart(self, data: Dict[str, float], title: str,
                            output_path: Optional[Path] = None) -> Optional[Path]:
        """
        Generate a funnel chart for conversion flows.
        
        Args:
            data: Dictionary with stage names and values
            title: Chart title
            output_path: Optional output path
            
        Returns:
            Path to saved chart image
        """
        try:
            fig, ax = plt.subplots(figsize=(8, 10))
            
            stages = list(data.keys())
            values = list(data.values())
            max_value = max(values)
            
            # Create funnel
            y_positions = []
            widths = []
            for i, val in enumerate(values):
                width = (val / max_value) * 0.8
                widths.append(width)
                y_positions.append(i * 1.2)
            
            # Draw funnel segments
            for i, (stage, val, width, y_pos) in enumerate(zip(stages, values, widths, y_positions)):
                # Funnel shape (trapezoid)
                x_center = 0.5
                x_left = x_center - width/2
                x_right = x_center + width/2
                
                # Next level width (for trapezoid)
                if i < len(widths) - 1:
                    next_width = widths[i + 1]
                    next_x_left = x_center - next_width/2
                    next_x_right = x_center + next_width/2
                else:
                    next_x_left = x_left
                    next_x_right = x_right
                
                # Draw trapezoid
                ax.fill([x_left, x_right, next_x_right, next_x_left],
                       [y_pos, y_pos, y_pos + 1.0, y_pos + 1.0],
                       alpha=0.7, color=plt.cm.viridis(i / len(stages)))
                
                # Add label
                ax.text(x_center, y_pos + 0.5, f"{stage}\n{val:.0f}",
                       ha='center', va='center', fontsize=12, fontweight='bold')
            
            ax.set_xlim(0, 1)
            ax.set_ylim(-0.5, len(stages) * 1.2)
            ax.axis('off')
            ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
            
            plt.tight_layout()
            
            if not output_path:
                output_path = self.chart_cache_dir / f"funnel_{hash(title)}.png"
            
            plt.savefig(output_path, dpi=150, bbox_inches='tight',
                       facecolor='white', edgecolor='none')
            plt.close()
            
            logger.info(f"Generated funnel chart: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error generating funnel chart: {e}")
            return None
    
    def generate_waterfall_chart(self, data: Dict[str, float], title: str,
                                output_path: Optional[Path] = None) -> Optional[Path]:
        """
        Generate a waterfall chart for financials.
        
        Args:
            data: Dictionary with labels and values
            title: Chart title
            output_path: Optional output path
            
        Returns:
            Path to saved chart image
        """
        try:
            fig, ax = plt.subplots(figsize=(10, 6))
            
            labels = list(data.keys())
            values = list(data.values())
            
            # Calculate cumulative positions
            cumulative = 0
            positions = []
            for val in values:
                positions.append(cumulative)
                cumulative += val
            
            # Draw bars
            colors = ['green' if v > 0 else 'red' for v in values]
            bars = ax.bar(labels, values, bottom=positions, color=colors, alpha=0.7)
            
            # Add value labels
            for i, (bar, val) in enumerate(zip(bars, values)):
                height = bar.get_height()
                y_pos = positions[i] + height/2
                ax.text(bar.get_x() + bar.get_width()/2., y_pos,
                       f'{val:+.1f}',
                       ha='center', va='center', fontweight='bold')
            
            ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
            ax.set_ylabel('Value', fontsize=11)
            plt.xticks(rotation=45, ha='right')
            plt.grid(True, alpha=0.3, axis='y')
            plt.tight_layout()
            
            if not output_path:
                output_path = self.chart_cache_dir / f"waterfall_{hash(title)}.png"
            
            plt.savefig(output_path, dpi=150, bbox_inches='tight',
                       facecolor='white', edgecolor='none')
            plt.close()
            
            logger.info(f"Generated waterfall chart: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error generating waterfall chart: {e}")
            return None
    
    def auto_generate_chart_for_slide(self, slide_title: str, slide_content: str,
                                     key_points: List[str]) -> Optional[Path]:
        """
        Automatically generate appropriate chart for a slide.
        
        Args:
            slide_title: Slide title
            slide_content: Slide content
            key_points: Key points list
            
        Returns:
            Path to generated chart or None
        """
        # Detect chart type
        chart_type = self.detect_chart_type(slide_title, slide_content, key_points)
        
        if not chart_type:
            return None
        
        # Extract data
        numbers = self.extract_numbers_from_text(f"{slide_content} {' '.join(key_points)}")
        
        if len(numbers) < 2:
            return None
        
        # Prepare data based on chart type
        if chart_type == 'pie':
            # For pie chart, use first few numbers as segments
            data = {}
            for i, num in enumerate(numbers[:5]):  # Max 5 segments
                label = num.get('context', f'Item {i+1}')[:20]  # Truncate long labels
                data[label] = num['value']
            
            return self.generate_pie_chart(data, slide_title)
        
        elif chart_type == 'bar':
            # For bar chart, use numbers as bars
            data = {}
            for i, num in enumerate(numbers[:8]):  # Max 8 bars
                label = num.get('context', f'Metric {i+1}')[:15]
                data[label] = num['value']
            
            return self.generate_bar_chart(data, slide_title)
        
        elif chart_type == 'line':
            # For line chart, assume time series
            data = {}
            for i, num in enumerate(numbers[:10]):  # Max 10 points
                label = f"Period {i+1}"
                data[label] = num['value']
            
            return self.generate_line_chart(data, slide_title, ylabel="Value")
        
        return None

