"""Chat interface for TechScopeAI using Streamlit."""

import streamlit as st
import json
import logging
import os
from pathlib import Path
from typing import Dict, Optional
import sys

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.agents.pitch_agent import PitchAgent
from src.agents.competitive_agent import CompetitiveAgent
from src.rag.embedder import Embedder
from src.rag.vector_store import VectorStore
from src.rag.retriever import Retriever
from src.data.load_company_data import load_test_company_data, format_company_data_for_pitch, load_company_data
from src.utils.exporters import PitchExporter

logger = logging.getLogger(__name__)

# Configure page
st.set_page_config(
    page_title="TechScopeAI - Pitch Agent",
    page_icon="🚀",
    layout="wide"
)


@st.cache_resource
def load_pitch_agent():
    """Load and cache PitchAgent."""
    try:
        # Check for OpenAI API key
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            return None, "OPENAI_API_KEY not found in environment. Add it to .env file"
        
        # Initialize RAG components
        embedder = Embedder(use_openai=False)  # Use free embeddings
        vector_store = VectorStore(category="pitch", dimension=embedder.get_embedding_dimension())
        retriever = Retriever(vector_store, embedder)
        
        # Initialize agent
        agent = PitchAgent(retriever)
        return agent, None
    except Exception as e:
        return None, str(e)


@st.cache_resource
def load_competitive_agent():
    """Load and cache CompetitiveAgent."""
    try:
        # Check for OpenAI API key
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            return None, "OPENAI_API_KEY not found in environment. Add it to .env file"
        
        # Initialize RAG components for competitive analysis
        embedder = Embedder(use_openai=False)
        vector_store = VectorStore(category="competitive", dimension=embedder.get_embedding_dimension())
        retriever = Retriever(vector_store, embedder)
        
        # Initialize agent
        agent = CompetitiveAgent(retriever)
        return agent, None
    except Exception as e:
        return None, str(e)


def load_company_data_file(company_id: str) -> Optional[Dict]:
    """Load company data from file."""
    company_path = Path(f"src/data/user_companies/{company_id}.json")
    if company_path.exists():
        with open(company_path, 'r') as f:
            return json.load(f)
    return None


def save_company_data(company_id: str, data: Dict):
    """Save company data to file."""
    company_path = Path(f"src/data/user_companies/{company_id}.json")
    company_path.parent.mkdir(parents=True, exist_ok=True)
    with open(company_path, 'w') as f:
        json.dump(data, f, indent=2)


def main():
    """Main chat interface."""
    st.title("🚀 TechScopeAI - Pitch Agent")
    st.markdown("**Your AI-powered pitch deck advisor**")
    
    # Initialize session state
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'company_data' not in st.session_state:
        st.session_state.company_data = None
    if 'company_id' not in st.session_state:
        st.session_state.company_id = None
    if 'slides' not in st.session_state:
        st.session_state.slides = None
    if 'current_slide' not in st.session_state:
        st.session_state.current_slide = 0
    if 'elevator_pitch' not in st.session_state:
        st.session_state.elevator_pitch = None
    
    # Load agent
    agent, error = load_pitch_agent()
    
    if error:
        st.error(f"❌ Error loading agent: {error}")
        st.info("💡 Make sure you've:")
        st.info("1. Processed the pitch data (run: python scripts/processing/process_pitch_data.py)")
        st.info("2. Built the RAG index (run: python scripts/processing/build_rag_index.py)")
        st.info("3. Set OPENAI_API_KEY in .env file")
        return
    
    # Sidebar for company details
    with st.sidebar:
        st.header("📋 Company Details")
        
        # Company ID input
        company_id = st.text_input("Company ID", value=st.session_state.company_id or "default")
        st.session_state.company_id = company_id
        
        # Load test data option
        if st.button("📋 Load Test Company Data"):
            test_data = load_test_company_data()
            if test_data:
                formatted = format_company_data_for_pitch(test_data)
                st.session_state.company_data = formatted
                st.success(f"✅ Loaded test data for: {formatted.get('company_name', 'Unknown')}")
            else:
                st.error("Test company data not found!")
        
        # Load existing company data
        if st.button("📂 Load Saved Company Data"):
            data = load_company_data_file(company_id)
            if data:
                formatted = format_company_data_for_pitch(data)
                st.session_state.company_data = formatted
                st.success("✅ Company data loaded!")
            else:
                st.warning("No company data found. Fill in the form below or load test data.")
        
        # Company details form
        st.subheader("Enter Company Details")
        
        company_name = st.text_input("Company Name", value=st.session_state.company_data.get('company_name', '') if st.session_state.company_data else '')
        industry = st.text_input("Industry", value=st.session_state.company_data.get('industry', '') if st.session_state.company_data else '')
        problem = st.text_area("Problem", value=st.session_state.company_data.get('problem', '') if st.session_state.company_data else '', height=100)
        solution = st.text_area("Solution", value=st.session_state.company_data.get('solution', '') if st.session_state.company_data else '', height=100)
        market = st.text_input("Target Market", value=st.session_state.company_data.get('target_market', '') if st.session_state.company_data else '')
        stage = st.selectbox("Current Stage", ["Pre-Seed", "Seed", "Series A", "Series B", "Series C+"], 
                           index=0 if not st.session_state.company_data else 
                           ["Pre-Seed", "Seed", "Series A", "Series B", "Series C+"].index(st.session_state.company_data.get('current_stage', 'Pre-Seed')) if st.session_state.company_data.get('current_stage') in ["Pre-Seed", "Seed", "Series A", "Series B", "Series C+"] else 0)
        traction = st.text_area("Traction", value=st.session_state.company_data.get('traction', '') if st.session_state.company_data else '', height=80)
        funding_goal = st.text_input("Funding Goal", value=st.session_state.company_data.get('funding_goal', '') if st.session_state.company_data else '')
        
        if st.button("💾 Save Company Data"):
            company_data = {
                'company_name': company_name,
                'industry': industry,
                'problem': problem,
                'solution': solution,
                'target_market': market,
                'current_stage': stage,
                'traction': traction,
                'funding_goal': funding_goal
            }
            save_company_data(company_id, company_data)
            st.session_state.company_data = company_data
            st.success("✅ Company data saved!")
    
    # Main chat area
    st.header("💬 Chat with Pitch Agent")
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if "sources" in message and message["sources"]:
                with st.expander("📚 Sources"):
                    for source in message["sources"][:3]:  # Show top 3 sources
                        st.text(f"• {source.get('source', 'Unknown')} (similarity: {source.get('similarity', 0):.2f})")
    
    # Chat input
    if prompt := st.chat_input("Ask about pitch decks, generate a pitch, or evaluate your pitch..."):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Generate response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    # Determine mode based on prompt
                    prompt_lower = prompt.lower()
                    
                    if "evaluate" in prompt_lower or "review" in prompt_lower or "improve" in prompt_lower:
                        # Extract pitch text (assume it's after "evaluate:" or similar)
                        pitch_text = prompt
                        if ":" in prompt:
                            pitch_text = prompt.split(":", 1)[1].strip()
                        
                        response = agent.evaluate_pitch(
                            pitch_text=pitch_text,
                            company_context=st.session_state.company_data
                        )
                    elif "outline" in prompt_lower or "generate from outline" in prompt_lower:
                        # Extract outline (simplified - in real app, use structured input)
                        outline = {
                            "sections": ["Problem", "Solution", "Market", "Traction", "Team", "Ask"],
                            "notes": prompt
                        }
                        response = agent.generate_from_outline(
                            outline=outline,
                            company_context=st.session_state.company_data
                        )
                    elif "generate" in prompt_lower and st.session_state.company_data:
                        # Generate from company details
                        response = agent.generate_from_details(st.session_state.company_data)
                    else:
                        # General query
                        response = agent.process_query(
                            query=prompt,
                            context=st.session_state.company_data
                        )
                    
                    # Display response
                    st.markdown(response['response'])
                    
                    # Show sources
                    if response.get('sources'):
                        with st.expander("📚 Sources & Citations"):
                            for source in response['sources'][:5]:
                                st.text(f"• {source.get('source', 'Unknown')} (similarity: {source.get('similarity', 0):.2f})")
                    
                    # Add to messages
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": response['response'],
                        "sources": response.get('sources', [])
                    })
                    
                except Exception as e:
                    error_msg = f"❌ Error: {str(e)}"
                    st.error(error_msg)
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": error_msg
                    })
    
    # Slides Preview Section
    if st.session_state.slides and len(st.session_state.slides.get('slides', [])) > 0:
        st.markdown("---")
        st.subheader("📊 Pitch Deck Slides")
        
        slides_list = st.session_state.slides['slides']
        total_slides = len(slides_list)
        
        # Slide navigation
        col_nav1, col_nav2, col_nav3, col_nav4 = st.columns([1, 2, 1, 2])
        with col_nav1:
            if st.button("◀ Previous", disabled=st.session_state.current_slide == 0):
                st.session_state.current_slide = max(0, st.session_state.current_slide - 1)
                st.rerun()
        with col_nav2:
            st.write(f"**Slide {st.session_state.current_slide + 1} of {total_slides}**")
        with col_nav3:
            if st.button("Next ▶", disabled=st.session_state.current_slide >= total_slides - 1):
                st.session_state.current_slide = min(total_slides - 1, st.session_state.current_slide + 1)
                st.rerun()
        with col_nav4:
            # Export buttons
            exporter = PitchExporter()
            col_exp1, col_exp2, col_exp3 = st.columns(3)
            with col_exp1:
                if st.button("📄 Export PDF"):
                    filepath = exporter.export_to_pdf(slides_list, st.session_state.slides.get('company_name', 'Company'))
                    if filepath:
                        with open(filepath, 'rb') as f:
                            st.download_button("⬇ Download PDF", f, file_name=Path(filepath).name, mime="application/pdf")
            with col_exp2:
                if st.button("📊 Export PPTX (with images)"):
                    filepath = exporter.export_to_powerpoint(
                        slides_list, 
                        st.session_state.slides.get('company_name', 'Company'),
                        include_images=True
                    )
                    if filepath:
                        with open(filepath, 'rb') as f:
                            st.download_button("⬇ Download PPTX", f, file_name=Path(filepath).name, mime="application/vnd.openxmlformats-officedocument.presentationml.presentation")
            with col_exp3:
                if st.button("📝 Export MD"):
                    filepath = exporter.export_to_markdown(slides_list, st.session_state.slides.get('company_name', 'Company'))
                    if filepath:
                        with open(filepath, 'rb') as f:
                            st.download_button("⬇ Download MD", f, file_name=Path(filepath).name, mime="text/markdown")
        
        # Display current slide
        if 0 <= st.session_state.current_slide < total_slides:
            slide = slides_list[st.session_state.current_slide]
            st.markdown("---")
            with st.container():
                # Create two columns: content on left, image on right
                col_content, col_image = st.columns([2, 1])
                
                with col_content:
                    st.markdown(f"### 📊 Slide {slide.get('slide_number', '?')}: {slide.get('title', 'Untitled')}")
                    
                    # Main content
                    if slide.get('content'):
                        st.markdown("**Content:**")
                        st.markdown(slide.get('content', ''))
                    
                    if slide.get('key_points'):
                        st.markdown("**Key Points:**")
                        for point in slide['key_points']:
                            st.markdown(f"- {point}")
                
                with col_image:
                    # Display image if available
                    image_path = slide.get('image_path')
                    if image_path and Path(image_path).exists():
                        try:
                            from PIL import Image
                            img = Image.open(image_path)
                            st.image(img, caption=slide.get('title', 'Slide Image'), use_container_width=True)
                        except Exception as e:
                            st.warning(f"Could not display image: {e}")
                    else:
                        st.info("🖼️ No image available for this slide")
                
                # Speech section (in expander - not in PPT)
                if slide.get('speech'):
                    with st.expander("💬 Speech Script (Not in PPT - for reference only)"):
                        st.info(slide.get('speech', ''))
                
                # Talking points section (in expander - not in PPT)
                if slide.get('talking_points'):
                    with st.expander("🎯 Talking Points (Not in PPT - for reference only)"):
                        for point in slide.get('talking_points', []):
                            st.markdown(f"→ **{point}**")
        
        # Slide thumbnails
        st.markdown("---")
        st.subheader("📑 All Slides")
        cols = st.columns(min(5, total_slides))
        for idx, slide in enumerate(slides_list):
            col_idx = idx % 5
            with cols[col_idx]:
                if st.button(f"Slide {idx + 1}\n{slide.get('title', '')[:20]}...", key=f"slide_btn_{idx}"):
                    st.session_state.current_slide = idx
                    st.rerun()
    
    # Elevator Pitch Section (independent of slides)
    if st.session_state.get('elevator_pitch'):
        st.markdown("---")
        st.subheader("🎤 Elevator Pitch")
        
        pitch_data = st.session_state.elevator_pitch
        col_pitch1, col_pitch2 = st.columns([3, 1])
        
        with col_pitch1:
            st.markdown(f"**Duration:** {pitch_data.get('duration_seconds', 60)} seconds")
            st.markdown(f"**Words:** ~{pitch_data.get('estimated_words', 0)} words")
            
            # Display pitch in a nice box
            st.markdown("### Your Elevator Pitch:")
            st.info(pitch_data.get('elevator_pitch', ''))
            
            # Also show in code block for easy copying
            st.markdown("### Copy Text:")
            st.code(pitch_data.get('elevator_pitch', ''), language=None)
        
        with col_pitch2:
            # Copy button info
            st.markdown("### Export")
            pitch_text = pitch_data.get('elevator_pitch', '')
            st.download_button(
                "💾 Download as TXT",
                pitch_text,
                file_name=f"{pitch_data.get('company_name', 'Company')}_ElevatorPitch.txt",
                mime="text/plain"
            )
            st.caption("💡 Tip: Click the code block above and copy to clipboard")
    
    # Quick actions
    st.markdown("---")
    st.subheader("⚡ Quick Actions")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("📝 Generate Pitch"):
            if st.session_state.company_data:
                with st.spinner("Generating pitch..."):
                    response = agent.generate_from_details(st.session_state.company_data)
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": response['response'],
                        "sources": response.get('sources', [])
                    })
                    st.rerun()
            else:
                st.warning("Please enter company details first!")
    
    with col2:
        if st.button("🎯 Generate Slides"):
            if st.session_state.company_data:
                with st.spinner("Generating slides and creating professional PowerPoint..."):
                    slides_data = agent.generate_slides(st.session_state.company_data)
                    st.session_state.slides = slides_data
                    st.session_state.current_slide = 0
                    
                    success_msg = f"✅ Generated {slides_data.get('total_slides', 0)} slides!"
                    if slides_data.get('pptx_path'):
                        success_msg += f"\n📊 Professional PowerPoint created!"
                        st.success(success_msg)
                        # Auto-download option
                        pptx_path = Path(slides_data['pptx_path'])
                        if pptx_path.exists():
                            with open(pptx_path, 'rb') as f:
                                st.download_button(
                                    "⬇ Download PowerPoint",
                                    f,
                                    file_name=pptx_path.name,
                                    mime="application/vnd.openxmlformats-officedocument.presentationml.presentation"
                                )
                    else:
                        st.success(success_msg)
                    st.rerun()
            else:
                st.warning("Please enter company details first!")
    
    with col3:
        if st.button("🎤 Generate Elevator Pitch"):
            if st.session_state.company_data:
                with st.spinner("Crafting your elevator pitch..."):
                    try:
                        # Generate 60-second elevator pitch
                        pitch_result = agent.generate_elevator_pitch(
                            st.session_state.company_data,
                            duration_seconds=60
                        )
                        if pitch_result and pitch_result.get('elevator_pitch'):
                            st.session_state.elevator_pitch = pitch_result
                            st.success("✅ Elevator pitch generated!")
                            st.rerun()
                        else:
                            st.error("❌ Failed to generate elevator pitch. Please try again.")
                            logger.error(f"Elevator pitch generation returned empty result: {pitch_result}")
                    except Exception as e:
                        error_msg = f"Error generating elevator pitch: {str(e)}"
                        st.error(error_msg)
                        logger.error(f"Elevator pitch generation error: {e}", exc_info=True)
            else:
                st.warning("Please enter company details first!")
    
    with col4:
        if st.button("📊 Evaluate Pitch"):
            st.info("Paste your pitch in chat: 'evaluate: [your pitch]'")
    
    with col4:
        if st.button("🔍 Analyze Competitors"):
            comp_agent, comp_error = load_competitive_agent()
            if comp_error:
                st.error(f"Error: {comp_error}")
            elif st.session_state.company_data:
                with st.spinner("Analyzing competitors..."):
                    response = comp_agent.analyze_competitors(st.session_state.company_data)
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": f"## Competitive Analysis\n\n{response['response']}",
                        "sources": response.get('sources', [])
                    })
                    st.rerun()
            else:
                st.warning("Please enter company details first!")
    
    # Additional actions
    col5, col6 = st.columns(2)
    with col5:
        if st.button("💡 Pitch Tips"):
            response = agent.process_query("What are common pitch deck mistakes and best practices?")
            st.session_state.messages.append({
                "role": "assistant",
                "content": response['response'],
                "sources": response.get('sources', [])
            })
            st.rerun()
    
    with col6:
        if st.button("📈 Enhanced Scoring"):
            if st.session_state.messages:
                # Get last pitch from messages
                last_pitch = None
                for msg in reversed(st.session_state.messages):
                    if msg.get("role") == "assistant" and len(msg.get("content", "")) > 100:
                        last_pitch = msg.get("content", "")
                        break
                
                if last_pitch:
                    with st.spinner("Scoring pitch..."):
                        response = agent.evaluate_pitch_with_scores(
                            last_pitch,
                            st.session_state.company_data
                        )
                        eval_data = response.get('evaluation', {})
                        
                        # Display scores
                        st.subheader("📊 Pitch Scores")
                        overall = eval_data.get('overall_score', 0)
                        st.metric("Overall Score", f"{overall}/10")
                        
                        section_scores = eval_data.get('section_scores', {})
                        for section, score_data in section_scores.items():
                            if isinstance(score_data, dict):
                                score = score_data.get('score', 0)
                                st.progress(score / 10)
                                st.caption(f"{section.title()}: {score}/10 - {score_data.get('feedback', '')}")
                        
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": f"## Enhanced Scoring\n\n{json.dumps(eval_data, indent=2)}",
                            "sources": response.get('sources', [])
                        })
                        st.rerun()
                else:
                    st.info("Generate a pitch first to score it!")


if __name__ == "__main__":
    main()

