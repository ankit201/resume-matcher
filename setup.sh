#!/bin/bash

# Resume Matcher Setup Script
# Automates environment setup and dependency installation with UV

echo "🚀 Resume Matcher - Setup Script (UV Edition)"
echo "=============================================="
echo ""

# Check Python version
echo "📋 Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Found Python $python_version"

if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.9+ and try again."
    exit 1
fi

# Check for UV
echo ""
echo "📦 Checking for UV package manager..."
if ! command -v uv &> /dev/null; then
    echo "UV not found. Installing UV..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    
    # Add UV to PATH for current session
    export PATH="$HOME/.cargo/bin:$PATH"
    
    if command -v uv &> /dev/null; then
        echo "✅ UV installed successfully ($(uv --version))"
    else
        echo "❌ Failed to install UV. Please install manually from: https://github.com/astral-sh/uv"
        echo "Falling back to traditional pip setup..."
        # Fallback to pip
        if [ ! -d "venv" ]; then
            python3 -m venv venv
        fi
        source venv/bin/activate
        pip install --upgrade pip
        if [ -f "requirements.txt" ]; then
            pip install -r requirements.txt
        else
            pip install -e .
        fi
    fi
else
    echo "✅ UV already installed ($(uv --version))"
fi

# Create virtual environment with UV
echo ""
echo "🔧 Creating virtual environment with UV..."
if [ ! -d ".venv" ]; then
    uv venv
    echo "✅ Virtual environment created at .venv/"
else
    echo "ℹ️  Virtual environment already exists"
fi

# Install dependencies with UV
echo ""
echo "📥 Installing dependencies with UV..."
echo "This may take a few minutes..."
uv pip install -e .

if [ $? -ne 0 ]; then
    echo "❌ Error installing dependencies with UV"
    exit 1
fi
echo "✅ Dependencies installed successfully"

# Pre-download embedding model
echo ""
echo "📚 Pre-downloading embedding model..."
source .venv/bin/activate
python3 -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')" 2>&1 > /dev/null
if [ $? -eq 0 ]; then
    echo "✅ Embedding model cached"
else
    echo "ℹ️  Model will be downloaded on first use"
fi

# Create .env file if it doesn't exist
echo ""
echo "⚙️  Setting up configuration..."
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "✅ Created .env file from .env.example"
    echo "⚠️  IMPORTANT: Edit .env file and add your API keys:"
    echo "   - OPENAI_API_KEY"
    echo "   - GOOGLE_API_KEY"
    echo "   - ANTHROPIC_API_KEY (optional)"
else
    echo "ℹ️  .env file already exists"
fi

# Create necessary directories
echo ""
echo "📁 Creating directories..."
mkdir -p data/resumes
mkdir -p data/job_descriptions
mkdir -p logs
mkdir -p tests
echo "✅ Directories created"

# Check if setup is complete
echo ""
echo "=============================================="
echo "✅ Setup Complete!"
echo ""
echo "📝 Next Steps:"
echo "1. Edit .env file and add your API keys:"
echo "   - OPENAI_API_KEY (required for matching)"
echo "   - GOOGLE_API_KEY (required for PDF parsing)"
echo "   - ANTHROPIC_API_KEY (optional for Claude comparison)"
echo ""
echo "2. Place resume PDFs in data/resumes/"
echo "3. Place job descriptions in data/job_descriptions/"
echo ""
echo "4. Activate the virtual environment:"
echo "   source .venv/bin/activate"
echo ""
echo "5. Run the application:"
echo "   streamlit run app.py"
echo ""
echo "   Or use UV directly (no activation needed):"
echo "   uv run streamlit run app.py"
echo ""
echo "💡 For more information, see README.md"
echo "=============================================="
