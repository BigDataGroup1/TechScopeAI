"""Generate infographics (process flows, timelines, comparisons)."""

import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import numpy as np

logger = logging.getLogger(__name__)


class InfographicGenerator:
    """Generate infographics for presentations."""
    
    def __init__(self):
        """Initialize infographic generator."""
        self.cache_dir = Path("exports/infographics")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        logger.info("InfographicGenerator initialized")
    
    def generate_timeline(self, events: List[Dict[str, str]], title: str,
                         output_path: Optional[Path] = None) -> Optional[Path]:
        """
        Generate timeline infographic.
        
        Args:
            events: List of events with 'date', 'title', 'description'
            title: Timeline title
            output_path: Optional output path
            
        Returns:
            Path to generated timeline
        """
        try:
            fig, ax = plt.subplots(figsize=(12, 6))
            
            # Draw timeline line
            timeline_y = 0.5
            ax.plot([0.1, 0.9], [timeline_y, timeline_y], 
                   color='#3b82f6', linewidth=3, zorder=1)
            
            # Add events
            num_events = len(events)
            x_positions = np.linspace(0.15, 0.85, num_events)
            
            for i, (event, x_pos) in enumerate(zip(events, x_positions)):
                # Event marker
                ax.scatter(x_pos, timeline_y, s=200, color='#3b82f6', 
                          zorder=3, edgecolors='white', linewidths=2)
                
                # Event box
                event_text = f"{event.get('date', '')}\n{event.get('title', '')}"
                if event.get('description'):
                    event_text += f"\n{event.get('description', '')[:30]}..."
                
                # Position above or below timeline
                y_offset = 0.15 if i % 2 == 0 else -0.15
                
                # Text box
                bbox = FancyBboxPatch(
                    (x_pos - 0.08, timeline_y + y_offset - 0.08),
                    0.16, 0.16,
                    boxstyle="round,pad=0.01",
                    facecolor='white',
                    edgecolor='#3b82f6',
                    linewidth=2,
                    zorder=2
                )
                ax.add_patch(bbox)
                
                ax.text(x_pos, timeline_y + y_offset, event_text,
                       ha='center', va='center', fontsize=9,
                       fontweight='bold', zorder=4)
                
                # Connector line
                ax.plot([x_pos, x_pos], [timeline_y, timeline_y + y_offset],
                       color='#3b82f6', linewidth=1, linestyle='--', zorder=1)
            
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
            ax.axis('off')
            ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
            
            plt.tight_layout()
            
            if not output_path:
                output_path = self.cache_dir / f"timeline_{hash(title)}.png"
            
            plt.savefig(output_path, dpi=150, bbox_inches='tight',
                       facecolor='white', edgecolor='none')
            plt.close()
            
            logger.info(f"Generated timeline: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error generating timeline: {e}")
            return None
    
    def generate_process_flow(self, steps: List[str], title: str,
                            output_path: Optional[Path] = None) -> Optional[Path]:
        """
        Generate process flow diagram.
        
        Args:
            steps: List of process steps
            title: Diagram title
            output_path: Optional output path
            
        Returns:
            Path to generated process flow
        """
        try:
            fig, ax = plt.subplots(figsize=(12, 6))
            
            num_steps = len(steps)
            x_positions = np.linspace(0.1, 0.9, num_steps)
            y_pos = 0.5
            
            for i, (step, x_pos) in enumerate(zip(steps, x_positions)):
                # Step box
                box = FancyBboxPatch(
                    (x_pos - 0.08, y_pos - 0.1),
                    0.16, 0.2,
                    boxstyle="round,pad=0.01",
                    facecolor='#3b82f6',
                    edgecolor='white',
                    linewidth=2,
                    zorder=2
                )
                ax.add_patch(box)
                
                # Step number
                ax.text(x_pos, y_pos + 0.05, str(i + 1),
                       ha='center', va='center', fontsize=14,
                       fontweight='bold', color='white', zorder=3)
                
                # Step text
                ax.text(x_pos, y_pos - 0.05, step[:15] + ('...' if len(step) > 15 else ''),
                       ha='center', va='center', fontsize=9,
                       fontweight='bold', color='white', zorder=3)
                
                # Arrow to next step
                if i < num_steps - 1:
                    next_x = x_positions[i + 1]
                    arrow = FancyArrowPatch(
                        (x_pos + 0.08, y_pos),
                        (next_x - 0.08, y_pos),
                        arrowstyle='->',
                        mutation_scale=20,
                        color='#3b82f6',
                        linewidth=2,
                        zorder=1
                    )
                    ax.add_patch(arrow)
            
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
            ax.axis('off')
            ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
            
            plt.tight_layout()
            
            if not output_path:
                output_path = self.cache_dir / f"process_{hash(title)}.png"
            
            plt.savefig(output_path, dpi=150, bbox_inches='tight',
                       facecolor='white', edgecolor='none')
            plt.close()
            
            logger.info(f"Generated process flow: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error generating process flow: {e}")
            return None
    
    def generate_comparison_matrix(self, items: List[str], features: List[str],
                                  data: List[List[bool]], title: str,
                                  output_path: Optional[Path] = None) -> Optional[Path]:
        """
        Generate comparison matrix (feature comparison).
        
        Args:
            items: List of items to compare
            features: List of features
            data: 2D list of booleans (item has feature)
            title: Chart title
            output_path: Optional output path
            
        Returns:
            Path to generated matrix
        """
        try:
            fig, ax = plt.subplots(figsize=(10, 6))
            
            # Create heatmap
            matrix = np.array(data, dtype=float)
            
            im = ax.imshow(matrix, cmap='RdYlGn', aspect='auto', vmin=0, vmax=1)
            
            # Set ticks
            ax.set_xticks(np.arange(len(features)))
            ax.set_yticks(np.arange(len(items)))
            ax.set_xticklabels(features, rotation=45, ha='right')
            ax.set_yticklabels(items)
            
            # Add text annotations
            for i in range(len(items)):
                for j in range(len(features)):
                    text = "✓" if matrix[i, j] > 0.5 else "✗"
                    color = 'white' if matrix[i, j] > 0.5 else 'black'
                    ax.text(j, i, text, ha='center', va='center',
                           fontsize=14, fontweight='bold', color=color)
            
            ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
            plt.tight_layout()
            
            if not output_path:
                output_path = self.cache_dir / f"matrix_{hash(title)}.png"
            
            plt.savefig(output_path, dpi=150, bbox_inches='tight',
                       facecolor='white', edgecolor='none')
            plt.close()
            
            logger.info(f"Generated comparison matrix: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error generating comparison matrix: {e}")
            return None
    
    def generate_roadmap(self, phases: List[Dict[str, any]], title: str,
                        output_path: Optional[Path] = None) -> Optional[Path]:
        """
        Generate product roadmap.
        
        Args:
            phases: List of phases with 'name', 'timeline', 'features'
            title: Roadmap title
            output_path: Optional output path
            
        Returns:
            Path to generated roadmap
        """
        try:
            fig, ax = plt.subplots(figsize=(14, 6))
            
            num_phases = len(phases)
            bar_height = 0.6
            y_positions = np.linspace(0.2, 0.8, num_phases)
            
            colors = plt.cm.viridis(np.linspace(0, 1, num_phases))
            
            for i, (phase, y_pos, color) in enumerate(zip(phases, y_positions, colors)):
                # Phase bar
                timeline = phase.get('timeline', 'Q1')
                width = 0.6
                
                bar = ax.barh(y_pos, width, height=bar_height/num_phases,
                            color=color, alpha=0.7, edgecolor='white', linewidth=2)
                
                # Phase name
                ax.text(0.05, y_pos, phase.get('name', f'Phase {i+1}'),
                       ha='left', va='center', fontsize=12, fontweight='bold')
                
                # Timeline
                ax.text(0.65, y_pos, timeline,
                       ha='left', va='center', fontsize=10)
                
                # Features (if space allows)
                features = phase.get('features', [])
                if features and len(features) <= 3:
                    features_text = ', '.join(features[:3])
                    ax.text(0.3, y_pos, features_text,
                           ha='left', va='center', fontsize=9, style='italic')
            
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
            ax.axis('off')
            ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
            
            plt.tight_layout()
            
            if not output_path:
                output_path = self.cache_dir / f"roadmap_{hash(title)}.png"
            
            plt.savefig(output_path, dpi=150, bbox_inches='tight',
                       facecolor='white', edgecolor='none')
            plt.close()
            
            logger.info(f"Generated roadmap: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error generating roadmap: {e}")
            return None


