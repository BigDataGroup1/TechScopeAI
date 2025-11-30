#!/bin/bash
# Setup script for Pitch Agent

echo "🚀 Setting up TechScopeAI Pitch Agent..."
echo ""

# Check if virtual environment is activated
if [ -z "$VIRTUAL_ENV" ]; then
    echo "⚠️  Virtual environment not activated. Activating..."
    source venv/bin/activate
fi

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Check for .env file
if [ ! -f .env ]; then
    echo "⚠️  .env file not found. Creating template..."
    echo "OPENAI_API_KEY=your_key_here" > .env
    echo "✅ Created .env file. Please add your OpenAI API key!"
fi

# Process pitch data
echo ""
echo "📊 Processing pitch data..."
python scripts/processing/process_pitch_data.py

# Build RAG index
echo ""
echo "🔍 Building RAG index..."
python scripts/processing/build_rag_index.py --category pitch

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Add your OpenAI API key to .env file"
echo "2. Run: python main.py --mode web"
echo ""

