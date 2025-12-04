"""Main entry point for TechScopeAI."""

import argparse
import logging
import sys
import os
from pathlib import Path

# Fix tokenizers parallelism warning
os.environ["TOKENIZERS_PARALLELISM"] = "false"

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.agents.pitch_agent import PitchAgent
from src.rag.embedder import Embedder
from src.rag.vector_store import VectorStore
from src.rag.retriever import Retriever
from src.data.load_company_data import load_test_company_data, format_company_data_for_pitch, load_company_data

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def initialize_agent():
    """Initialize PitchAgent with RAG system."""
    logger.info("Initializing PitchAgent...")
    
    # Initialize RAG components
    embedder = Embedder(use_openai=False)  # Use free embeddings
    dimension = embedder.get_embedding_dimension()
    
    vector_store = VectorStore(category="pitch", dimension=dimension)
    retriever = Retriever(vector_store, embedder)
    
    # Initialize agent
    agent = PitchAgent(retriever)
    
    logger.info("✅ PitchAgent initialized")
    return agent


def cli_mode():
    """Run in CLI mode."""
    parser = argparse.ArgumentParser(description="TechScopeAI Pitch Agent CLI")
    parser.add_argument("--mode", choices=["generate", "evaluate", "query"], 
                       default="query", help="Agent mode")
    parser.add_argument("--query", help="Query text")
    parser.add_argument("--company", help="Path to company JSON file or company_id")
    parser.add_argument("--use-test-data", action="store_true", 
                       help="Use test company data from test/sample_company_data.json")
    parser.add_argument("--outline", help="Path to outline JSON file")
    parser.add_argument("--pitch", help="Pitch text to evaluate")
    
    args = parser.parse_args()
    
    # Check OpenAI API key
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ ERROR: OPENAI_API_KEY not found in environment!")
        print("   Please add it to your .env file:")
        print("   OPENAI_API_KEY=sk-your-key-here")
        return
    
    agent = initialize_agent()
    
    if args.mode == "generate":
        company_data = None
        
        # Try to load company data
        if args.use_test_data:
            print("📋 Using test company data...")
            company_data = load_test_company_data()
            if company_data:
                # Format for pitch generation
                company_data = format_company_data_for_pitch(company_data)
                print(f"✅ Loaded test data for: {company_data.get('company_name', 'Unknown')}")
        elif args.company:
            # Check if it's a file path or company_id
            company_path = Path(args.company)
            if company_path.exists():
                # It's a file path
                import json
                with open(company_path, 'r') as f:
                    company_data = json.load(f)
                print(f"✅ Loaded company data from: {args.company}")
            else:
                # It's a company_id, try to load from user_companies
                company_data = load_company_data(args.company)
                if company_data:
                    company_data = format_company_data_for_pitch(company_data)
                    print(f"✅ Loaded company data for ID: {args.company}")
                else:
                    print(f"❌ Company data not found: {args.company}")
                    return
        
        if company_data:
            print("\n🚀 Generating pitch deck...")
            response = agent.generate_from_details(company_data)
        elif args.outline:
            import json
            with open(args.outline, 'r') as f:
                outline = json.load(f)
            print("\n🚀 Generating pitch deck from outline...")
            response = agent.generate_from_outline(outline)
        else:
            print("❌ Error: Need --company, --use-test-data, or --outline for generate mode")
            print("\nExample usage:")
            print("  python main.py --mode cli --mode generate --use-test-data")
            print("  python main.py --mode cli --mode generate --company test/sample_company_data.json")
            return
        
        print("\n" + "="*80)
        print("GENERATED PITCH DECK")
        print("="*80)
        print(response['response'])
        print("\n" + "="*80)
        print("SOURCES:")
        for source in response.get('sources', []):
            print(f"  • {source.get('source', 'Unknown')}")
    
    elif args.mode == "evaluate":
        if not args.pitch:
            print("Error: Need --pitch for evaluate mode")
            return
        
        company_data = None
        if args.company:
            import json
            with open(args.company, 'r') as f:
                company_data = json.load(f)
        
        response = agent.evaluate_pitch(args.pitch, company_context=company_data)
        
        print("\n" + "="*80)
        print("PITCH EVALUATION")
        print("="*80)
        print(response['response'])
        print("\n" + "="*80)
        print("SOURCES:")
        for source in response.get('sources', []):
            print(f"  • {source.get('source', 'Unknown')}")
    
    else:  # query mode
        if not args.query:
            print("❌ Error: Need --query for query mode")
            print("\nExample usage:")
            print("  python main.py --mode cli --query 'What are common pitch mistakes?'")
            print("  python main.py --mode cli --query 'How to structure a pitch deck?' --use-test-data")
            return
        
        company_data = None
        if args.use_test_data:
            company_data = load_test_company_data()
            if company_data:
                company_data = format_company_data_for_pitch(company_data)
        elif args.company:
            company_path = Path(args.company)
            if company_path.exists():
                import json
                with open(company_path, 'r') as f:
                    company_data = json.load(f)
            else:
                company_data = load_company_data(args.company)
                if company_data:
                    company_data = format_company_data_for_pitch(company_data)
        
        print(f"\n💬 Processing query: {args.query}")
        response = agent.process_query(args.query, context=company_data)
        
        print("\n" + "="*80)
        print("RESPONSE")
        print("="*80)
        print(response['response'])
        print("\n" + "="*80)
        print("SOURCES:")
        for source in response.get('sources', []):
            print(f"  • {source.get('source', 'Unknown')}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="TechScopeAI")
    parser.add_argument("--mode", choices=["cli", "web", "demo"], default="web",
                       help="Run mode: cli, web, or demo (default: web)")
    
    args = parser.parse_args()
    
    if args.mode == "cli":
        cli_mode()
    elif args.mode == "demo":
        # Demo mode - generate pitch from test data
        print("🚀 TechScopeAI - Demo Mode")
        print("="*80)
        
        # Check OpenAI API key
        if not os.getenv("OPENAI_API_KEY"):
            print("❌ ERROR: OPENAI_API_KEY not found in environment!")
            print("   Please add it to your .env file:")
            print("   OPENAI_API_KEY=sk-your-key-here")
            return
        
        # Load test data
        print("\n📋 Loading test company data...")
        test_data = load_test_company_data()
        if not test_data:
            print("❌ Test company data not found!")
            return
        
        formatted_data = format_company_data_for_pitch(test_data)
        print(f"✅ Loaded: {formatted_data.get('company_name', 'Unknown')}")
        print(f"   Industry: {formatted_data.get('industry', 'N/A')}")
        print(f"   Stage: {formatted_data.get('current_stage', 'N/A')}")
        
        # Initialize agent
        print("\n🤖 Initializing PitchAgent...")
        agent = initialize_agent()
        
        # Ask user what to generate
        print("\n📊 What would you like to generate?")
        print("  1. Full Pitch Deck (text)")
        print("  2. Structured Slides")
        choice = input("   Enter choice (1 or 2, default=1): ").strip() or "1"
        
        if choice == "2":
            # Generate slides
            print("\n🎯 Generating structured slides...")
            print("   This may take a minute...\n")
            slides_data = agent.generate_slides(formatted_data)
            
            print("\n" + "="*80)
            print(f"GENERATED PITCH DECK SLIDES ({slides_data.get('total_slides', 0)} slides)")
            print("="*80)
            
            for slide in slides_data.get('slides', []):
                print(f"\n📊 Slide {slide.get('slide_number', '?')}: {slide.get('title', 'Untitled')}")
                print("-" * 60)
                print(slide.get('content', ''))
                if slide.get('key_points'):
                    print("\nKey Points:")
                    for point in slide['key_points']:
                        print(f"  • {point}")
            
            print("\n" + "="*80)
            print("SOURCES:")
            for i, source in enumerate(slides_data.get('sources', [])[:5], 1):
                print(f"  {i}. {source.get('source', 'Unknown')} (similarity: {source.get('similarity', 0):.2f})")
            print("="*80)
        else:
            # Generate full pitch
            print("\n🚀 Generating pitch deck...")
            print("   This may take a minute...\n")
            response = agent.generate_from_details(formatted_data)
            
            print("\n" + "="*80)
            print("GENERATED PITCH DECK")
            print("="*80)
            print(response['response'])
            print("\n" + "="*80)
            print("SOURCES:")
            for i, source in enumerate(response.get('sources', [])[:5], 1):
                print(f"  {i}. {source.get('source', 'Unknown')} (similarity: {source.get('similarity', 0):.2f})")
            print("="*80)
    else:
        # Web mode - launch Streamlit
        import subprocess
        
        # Check OpenAI API key
        if not os.getenv("OPENAI_API_KEY"):
            print("⚠️  WARNING: OPENAI_API_KEY not found in environment!")
            print("   The web interface will show an error.")
            print("   Please add it to your .env file:")
            print("   OPENAI_API_KEY=sk-your-key-here")
            print("\n   Continuing anyway...\n")
        
        streamlit_app = Path(__file__).parent / "src" / "api" / "chat_interface.py"
        
        if not streamlit_app.exists():
            logger.error(f"Streamlit app not found: {streamlit_app}")
            return
        
        logger.info("Launching Streamlit web interface...")
        os.chdir(Path(__file__).parent)
        subprocess.run(["streamlit", "run", str(streamlit_app)])


if __name__ == "__main__":
    main()

