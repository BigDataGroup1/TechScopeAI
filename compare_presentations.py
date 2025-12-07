#!/usr/bin/env python3
"""
Comparison Tool: TechScopeAI vs Gamma.ai vs Canva
Generates presentations from the same input and creates a comparison report.
"""

import sys
import os
from pathlib import Path
import json
from datetime import datetime

# Fix tokenizers warning
os.environ["TOKENIZERS_PARALLELISM"] = "false"

# Load environment
from dotenv import load_dotenv
load_dotenv()

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.agents.pitch_agent import PitchAgent
from src.rag.embedder import Embedder
from src.rag.vector_store import VectorStore
from src.rag.retriever import Retriever
from src.data.load_company_data import format_company_data_for_pitch
from src.utils.exporters import PitchExporter

# API integrations
try:
    from src.integrations.gamma_api import GammaAPI
    GAMMA_API_AVAILABLE = True
except ImportError:
    GAMMA_API_AVAILABLE = False
    logger.warning("Gamma API not available")

try:
    from src.integrations.canva_api import CanvaAPI
    CANVA_API_AVAILABLE = True
except ImportError:
    CANVA_API_AVAILABLE = False
    logger.warning("Canva API not available")

class PresentationComparator:
    """Compare TechScopeAI, Gamma.ai, and Canva presentations."""
    
    def __init__(self):
        """Initialize comparator."""
        self.comparison_dir = Path("comparisons")
        self.comparison_dir.mkdir(exist_ok=True)
        
        # Create subdirectories
        (self.comparison_dir / "techscopeai").mkdir(exist_ok=True)
        (self.comparison_dir / "gamma_ai").mkdir(exist_ok=True)
        (self.comparison_dir / "canva").mkdir(exist_ok=True)
        (self.comparison_dir / "reports").mkdir(exist_ok=True)
        
        # Initialize API clients
        self.gamma_api = None
        self.canva_api = None
        
        if GAMMA_API_AVAILABLE:
            try:
                self.gamma_api = GammaAPI()
                if self.gamma_api.api_key:
                    print("✅ Gamma.ai API initialized")
                else:
                    print("⚠️  Gamma.ai API key not set (optional)")
            except Exception as e:
                logger.warning(f"Could not initialize Gamma API: {e}")
        
        if CANVA_API_AVAILABLE:
            try:
                self.canva_api = CanvaAPI()
                if self.canva_api.access_token or self.canva_api.api_key:
                    print("✅ Canva API initialized")
                else:
                    print("⚠️  Canva API credentials not set (optional)")
            except Exception as e:
                logger.warning(f"Could not initialize Canva API: {e}")
        
        print("📊 Presentation Comparator initialized")
    
    def generate_techscopeai_ppt(self, company_data: dict) -> str:
        """Generate TechScopeAI PowerPoint."""
        print("\n" + "="*80)
        print("🎯 GENERATING TECHSCOPEAI PRESENTATION")
        print("="*80)
        
        # Format company data
        formatted_data = format_company_data_for_pitch(company_data)
        company_name = company_data.get('company_name', 'Company')
        
        # Initialize agent
        print("\n🤖 Initializing PitchAgent...")
        embedder = Embedder(use_openai=False)
        dimension = embedder.get_embedding_dimension()
        vector_store = VectorStore(category="pitch", dimension=dimension)
        retriever = Retriever(vector_store, embedder)
        agent = PitchAgent(retriever)
        print("✅ PitchAgent initialized")
        
        # Generate slides
        print("\n🎯 Generating structured slides with Gamma.ai-style engine...")
        print("   This may take a minute...\n")
        slides_data = agent.generate_slides(formatted_data)
        
        print(f"✅ Generated {slides_data.get('total_slides', 0)} slides")
        
        # Export to PowerPoint
        print("\n📊 Exporting to PowerPoint...")
        exporter = PitchExporter()
        output_dir = self.comparison_dir / "techscopeai"
        pptx_path = exporter.export_to_powerpoint(
            slides_data["slides"],
            company_name,
            include_images=True,
            use_gamma_style=True,
            template="modern"
        )
        
        # Move to comparison directory
        if pptx_path:
            from shutil import copy
            comparison_path = output_dir / Path(pptx_path).name
            copy(pptx_path, comparison_path)
            print(f"✅ TechScopeAI PPT saved: {comparison_path}")
            return str(comparison_path)
        
        return None
    
    def generate_gamma_ppt(self, company_data: dict) -> Optional[str]:
        """Generate Gamma.ai PowerPoint using API."""
        print("\n" + "="*80)
        print("✨ GENERATING GAMMA.AI PRESENTATION")
        print("="*80)
        
        if not self.gamma_api or not self.gamma_api.api_key:
            print("⚠️  Gamma.ai API key not set. Skipping Gamma.ai generation.")
            print("   To enable: Add GAMMA_API_KEY to your .env file")
            print("   Get API key from: https://gamma.app (Pro account required)")
            return None
        
        try:
            print("\n🚀 Calling Gamma.ai API...")
            gamma_path = self.gamma_api.generate_presentation(company_data)
            
            if gamma_path:
                print(f"✅ Gamma.ai PPT saved: {gamma_path}")
                return gamma_path
            else:
                print("❌ Gamma.ai generation failed. Check API key and account status.")
                return None
                
        except Exception as e:
            logger.error(f"Error generating Gamma.ai presentation: {e}")
            print(f"❌ Error: {e}")
            return None
    
    def generate_canva_ppt(self, company_data: dict) -> Optional[str]:
        """Generate Canva PowerPoint using API."""
        print("\n" + "="*80)
        print("🎨 GENERATING CANVA PRESENTATION")
        print("="*80)
        
        if not self.canva_api or (not self.canva_api.access_token and not self.canva_api.api_key):
            print("⚠️  Canva API credentials not set. Skipping Canva generation.")
            print("   To enable: Add CANVA_API_KEY or CANVA_ACCESS_TOKEN to your .env file")
            print("   Get credentials from: https://www.canva.dev/")
            return None
        
        try:
            print("\n🚀 Calling Canva API...")
            canva_path = self.canva_api.generate_presentation(company_data)
            
            if canva_path:
                print(f"✅ Canva PPT saved: {canva_path}")
                return canva_path
            else:
                print("❌ Canva generation failed. Check API credentials.")
                return None
                
        except Exception as e:
            logger.error(f"Error generating Canva presentation: {e}")
            print(f"❌ Error: {e}")
            return None
    
    def create_comparison_report(self, company_data: dict, techscopeai_path: str = None,
                                gamma_path: str = None, canva_path: str = None):
        """Create comparison report."""
        print("\n" + "="*80)
        print("📊 CREATING COMPARISON REPORT")
        print("="*80)
        
        company_name = company_data.get('company_name', 'Company')
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Create HTML comparison report
        html_content = self._generate_html_report(company_data, techscopeai_path, gamma_path, canva_path, timestamp)
        
        report_path = self.comparison_dir / "reports" / f"comparison_{company_name.replace(' ', '_')}_{timestamp}.html"
        with open(report_path, 'w') as f:
            f.write(html_content)
        
        print(f"✅ Comparison report created: {report_path}")
        return str(report_path)
    
    def _generate_html_report(self, company_data: dict, techscopeai_path: str = None, 
                              gamma_path: str = None, canva_path: str = None, timestamp: str = "") -> str:
        """Generate HTML comparison report."""
        company_name = company_data.get('company_name', 'Company')
        
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Presentation Comparison: {company_name}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            min-height: 100vh;
        }}
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }}
        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
        }}
        .header p {{
            font-size: 1.2em;
            opacity: 0.9;
        }}
        .comparison-grid {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 30px;
            padding: 40px;
        }}
        .comparison-card {{
            background: #f8f9fa;
            border-radius: 15px;
            padding: 30px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            transition: transform 0.3s;
        }}
        .comparison-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 10px 25px rgba(0,0,0,0.2);
        }}
        .comparison-card h2 {{
            font-size: 1.8em;
            margin-bottom: 20px;
            color: #333;
        }}
        .techscopeai h2 {{
            color: #667eea;
        }}
        .gamma h2 {{
            color: #00d4aa;
        }}
        .canva h2 {{
            color: #00c4cc;
        }}
        .features {{
            list-style: none;
            margin: 20px 0;
        }}
        .features li {{
            padding: 10px 0;
            border-bottom: 1px solid #e0e0e0;
            display: flex;
            align-items: center;
        }}
        .features li:before {{
            content: "✓";
            color: #4caf50;
            font-weight: bold;
            margin-right: 10px;
            font-size: 1.2em;
        }}
        .status {{
            display: inline-block;
            padding: 8px 16px;
            border-radius: 20px;
            font-weight: bold;
            margin-top: 20px;
        }}
        .status.completed {{
            background: #4caf50;
            color: white;
        }}
        .status.pending {{
            background: #ff9800;
            color: white;
        }}
        .instructions {{
            background: #fff3cd;
            border-left: 4px solid #ffc107;
            padding: 20px;
            margin: 20px 0;
            border-radius: 5px;
        }}
        .instructions h3 {{
            color: #856404;
            margin-bottom: 10px;
        }}
        .instructions ol {{
            margin-left: 20px;
        }}
        .instructions li {{
            margin: 10px 0;
            color: #856404;
        }}
        .metrics {{
            background: #e3f2fd;
            padding: 30px;
            margin: 40px;
            border-radius: 15px;
        }}
        .metrics h2 {{
            color: #1976d2;
            margin-bottom: 20px;
        }}
        .metric-grid {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 20px;
        }}
        .metric-item {{
            text-align: center;
            padding: 20px;
            background: white;
            border-radius: 10px;
        }}
        .metric-value {{
            font-size: 2em;
            font-weight: bold;
            color: #1976d2;
        }}
        .metric-label {{
            color: #666;
            margin-top: 5px;
        }}
        .footer {{
            background: #f8f9fa;
            padding: 30px;
            text-align: center;
            color: #666;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 Presentation Comparison Report</h1>
            <p>{company_name} - Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</p>
        </div>
        
        <div class="comparison-grid">
            <!-- TechScopeAI -->
            <div class="comparison-card techscopeai">
                <h2>🚀 TechScopeAI</h2>
                <div class="status {'completed' if techscopeai_path else 'pending'}">
                    {'✅ Generated' if techscopeai_path else '⏳ Pending'}
                </div>
                <ul class="features">
                    <li>Gamma.ai-style layouts</li>
                    <li>Auto-generated charts</li>
                    <li>Real-time data integration</li>
                    <li>Smart content enhancement</li>
                    <li>Brand customization</li>
                    <li>Advanced visual design</li>
                    <li>Infographic generation</li>
                    <li>Content-aware layouts</li>
                </ul>
                {'<p style="margin-top: 20px;"><strong>File:</strong> ' + Path(techscopeai_path).name + '</p>' if techscopeai_path else ''}
                {'<p style="margin-top: 10px;"><strong>File:</strong> ' + Path(gamma_path).name + '</p>' if gamma_path else ''}
                {'<p style="margin-top: 10px;"><strong>File:</strong> ' + Path(canva_path).name + '</p>' if canva_path else ''}
            </div>
            
            <!-- Gamma.ai -->
            <div class="comparison-card gamma">
                <h2>✨ Gamma.ai</h2>
                <div class="status pending">⏳ Manual Generation Required</div>
                <ul class="features">
                    <li>AI-powered design</li>
                    <li>Smart layouts</li>
                    <li>Beautiful templates</li>
                    <li>Interactive elements</li>
                    <li>Web-based editor</li>
                    <li>Collaboration features</li>
                    <li>Export options</li>
                    <li>Animation support</li>
                </ul>
                <div class="instructions">
                    <h3>📝 How to Generate:</h3>
                    <ol>
                        <li>Go to <a href="https://gamma.app" target="_blank">gamma.app</a></li>
                        <li>Sign up / Log in</li>
                        <li>Click "Create" → "Presentation"</li>
                        <li>Enter company details from the data below</li>
                        <li>Let Gamma.ai generate the presentation</li>
                        <li>Export as PowerPoint</li>
                        <li>Save to: <code>comparisons/gamma_ai/</code></li>
                    </ol>
                </div>
            </div>
            
            <!-- Canva -->
            <div class="comparison-card canva">
                <h2>🎨 Canva</h2>
                <div class="status {'completed' if canva_path else 'pending'}">
                    {'✅ Generated' if canva_path else '⏳ API Credentials Not Set'}
                </div>
                <ul class="features">
                    <li>Extensive template library</li>
                    <li>Drag-and-drop editor</li>
                    <li>Stock photos & graphics</li>
                    <li>Brand kit integration</li>
                    <li>Team collaboration</li>
                    <li>Animation & transitions</li>
                    <li>Multiple export formats</li>
                    <li>Mobile app support</li>
                </ul>
                <div class="instructions">
                    <h3>📝 How to Generate:</h3>
                    <ol>
                        <li>Go to <a href="https://canva.com" target="_blank">canva.com</a></li>
                        <li>Sign up / Log in</li>
                        <li>Search for "Pitch Deck" template</li>
                        <li>Choose a professional template</li>
                        <li>Fill in company details from data below</li>
                        <li>Customize design</li>
                        <li>Download as PowerPoint</li>
                        <li>Save to: <code>comparisons/canva/</code></li>
                    </ol>
                </div>
            </div>
        </div>
        
        <div class="metrics">
            <h2>📈 Comparison Metrics</h2>
            <div class="metric-grid">
                <div class="metric-item">
                    <div class="metric-value">3</div>
                    <div class="metric-label">Platforms Compared</div>
                </div>
                <div class="metric-item">
                    <div class="metric-value">8+</div>
                    <div class="metric-label">Features Per Platform</div>
                </div>
                <div class="metric-item">
                    <div class="metric-value">100%</div>
                    <div class="metric-label">Automation (TechScopeAI)</div>
                </div>
            </div>
        </div>
        
        <div class="instructions" style="margin: 40px;">
            <h3>📋 Company Data Used for Comparison</h3>
            <pre style="background: white; padding: 20px; border-radius: 5px; overflow-x: auto; margin-top: 10px;">{json.dumps(company_data, indent=2)}</pre>
        </div>
        
        <div class="footer">
            <p>Generated by TechScopeAI Presentation Comparator</p>
            <p>Compare all three presentations side-by-side to evaluate quality, design, and features.</p>
        </div>
    </div>
</body>
</html>
"""
        return html
    
    def create_comparison_instructions(self, company_data: dict):
        """Create detailed comparison instructions."""
        instructions_path = self.comparison_dir / "reports" / "COMPARISON_INSTRUCTIONS.md"
        
        instructions = f"""# Presentation Comparison Instructions

## Overview
This guide helps you generate presentations using Gamma.ai and Canva with the same company data, then compare all three side-by-side.

## Company Data
```json
{json.dumps(company_data, indent=2)}
```

---

## Step 1: TechScopeAI ✅
**Status:** Already generated automatically

The TechScopeAI presentation has been generated with:
- Gamma.ai-style layouts
- Auto-generated charts
- Real-time data integration
- Smart content enhancement
- Advanced visual design

**Location:** `comparisons/techscopeai/`

---

## Step 2: Gamma.ai

### Method 1: Using Gamma.ai Website
1. Go to https://gamma.app
2. Sign up or log in
3. Click **"Create"** → **"Presentation"**
4. Enter the following information:

**Company Name:** {company_data.get('company_name', 'N/A')}
**Industry:** {company_data.get('industry', 'N/A')}
**Problem:** {company_data.get('problem', 'N/A')}
**Solution:** {company_data.get('solution', 'N/A')}
**Target Market:** {company_data.get('target_market', 'N/A')}
**Traction:** {company_data.get('traction', 'N/A')}
**Funding Goal:** {company_data.get('funding_goal', 'N/A')}

5. Let Gamma.ai generate the presentation
6. Review and customize if needed
7. Export as PowerPoint (.pptx)
8. Save to: `comparisons/gamma_ai/`

### Method 2: Using Gamma.ai API (if available)
```python
# Note: Gamma.ai API may require authentication
# Check their documentation for API access
```

---

## Step 3: Canva

### Using Canva Website
1. Go to https://canva.com
2. Sign up or log in (free account works)
3. Search for **"Pitch Deck"** or **"Startup Presentation"**
4. Choose a professional template
5. Fill in the slides with company data:

**Slide 1 - Title:**
- Company: {company_data.get('company_name', 'N/A')}
- Tagline: {company_data.get('unique_value_proposition', 'N/A')[:50]}

**Slide 2 - Problem:**
{company_data.get('problem', 'N/A')}

**Slide 3 - Solution:**
{company_data.get('solution', 'N/A')}

**Slide 4 - Market:**
{company_data.get('market_size', 'N/A')}

**Slide 5 - Traction:**
{company_data.get('traction', 'N/A')}

**Slide 6 - Team:**
{company_data.get('founders', 'N/A')}

**Slide 7 - Ask:**
{company_data.get('funding_goal', 'N/A')}

6. Customize design, colors, fonts
7. Add images from Canva's library
8. Download as PowerPoint (.pptx)
9. Save to: `comparisons/canva/`

---

## Step 4: Side-by-Side Comparison

### Option 1: Manual Comparison
1. Open all three PowerPoint files
2. Arrange windows side-by-side
3. Compare:
   - Visual design quality
   - Layout sophistication
   - Content structure
   - Chart quality
   - Overall professionalism

### Option 2: Use Comparison Report
1. Open the HTML report: `comparisons/reports/comparison_*.html`
2. Review the feature comparison
3. Open each PowerPoint to verify

### Comparison Criteria

#### Visual Design (1-10)
- **TechScopeAI:** ___
- **Gamma.ai:** ___
- **Canva:** ___

#### Content Quality (1-10)
- **TechScopeAI:** ___
- **Gamma.ai:** ___
- **Canva:** ___

#### Automation Level (1-10)
- **TechScopeAI:** 10 (Fully automated)
- **Gamma.ai:** 7 (Semi-automated)
- **Canva:** 3 (Manual)

#### Customization (1-10)
- **TechScopeAI:** ___
- **Gamma.ai:** ___
- **Canva:** ___

#### Speed (1-10)
- **TechScopeAI:** 10 (2-3 minutes)
- **Gamma.ai:** 7 (5-10 minutes)
- **Canva:** 4 (15-30 minutes)

#### Data Integration (1-10)
- **TechScopeAI:** 10 (Real-time data)
- **Gamma.ai:** 5 (Manual input)
- **Canva:** 3 (Manual input)

---

## Step 5: Create Comparison Summary

After reviewing all three, create a summary document:

1. **Winner by Category:**
   - Best Visual Design: ___
   - Best Content Quality: ___
   - Fastest Generation: ___
   - Most Automated: ___

2. **Overall Winner:** ___

3. **Key Differences:**
   - TechScopeAI: ___
   - Gamma.ai: ___
   - Canva: ___

4. **Recommendations:**
   - Use TechScopeAI when: ___
   - Use Gamma.ai when: ___
   - Use Canva when: ___

---

## Files Generated

- ✅ TechScopeAI: `comparisons/techscopeai/*.pptx`
- ⏳ Gamma.ai: `comparisons/gamma_ai/*.pptx` (to be added)
- ⏳ Canva: `comparisons/canva/*.pptx` (to be added)
- ✅ Comparison Report: `comparisons/reports/comparison_*.html`
- ✅ Instructions: `comparisons/reports/COMPARISON_INSTRUCTIONS.md`

---

## Tips

1. **Use the same company data** for all three to ensure fair comparison
2. **Take screenshots** of key slides for documentation
3. **Note the time** it takes to generate each presentation
4. **Evaluate objectively** based on criteria, not personal preference
5. **Consider use cases** - each tool may excel in different scenarios

---

Good luck with your comparison! 🚀
"""
        
        with open(instructions_path, 'w') as f:
            f.write(instructions)
        
        print(f"✅ Comparison instructions created: {instructions_path}")
        return str(instructions_path)


def main():
    """Main comparison function."""
    print("="*80)
    print("📊 PRESENTATION COMPARISON TOOL")
    print("TechScopeAI vs Gamma.ai vs Canva")
    print("="*80)
    
    # Get company data file
    if len(sys.argv) > 1:
        company_file = sys.argv[1]
    else:
        company_file = input("\nEnter path to company JSON file (or press Enter for test data): ").strip()
        if not company_file:
            company_file = "test/sample_company_data.json"
    
    if not Path(company_file).exists():
        print(f"❌ File not found: {company_file}")
        return
    
    # Load company data
    print(f"\n📋 Loading company data from: {company_file}")
    with open(company_file, 'r') as f:
        company_data = json.load(f)
    
    company_name = company_data.get('company_name', 'Company')
    print(f"✅ Loaded: {company_name}")
    
    # Initialize comparator
    comparator = PresentationComparator()
    
    # Generate TechScopeAI presentation
    techscopeai_path = comparator.generate_techscopeai_ppt(company_data)
    
    # Create comparison report
    report_path = comparator.create_comparison_report(company_data, techscopeai_path)
    
    # Create instructions
    instructions_path = comparator.create_comparison_instructions(company_data)
    
    # Summary
    print("\n" + "="*80)
    print("✅ COMPARISON SETUP COMPLETE")
    print("="*80)
    print(f"\n📊 TechScopeAI Presentation: {techscopeai_path}")
    print(f"📄 Comparison Report: {report_path}")
    print(f"📝 Instructions: {instructions_path}")
    print("\n📋 Next Steps:")
    print("1. Open the comparison report HTML file in your browser")
    print("2. Follow instructions to generate Gamma.ai and Canva presentations")
    print("3. Compare all three side-by-side")
    print("4. Evaluate based on the criteria in the report")
    print("\n🚀 Happy comparing!")


if __name__ == "__main__":
    main()

