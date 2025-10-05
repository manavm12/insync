#!/bin/bash
# InSync Web Application Environment Setup Script

echo "🤟 InSync Web Application Setup"
echo "================================"

# Check if .env file exists
if [ -f ".env" ]; then
    echo "📄 Found .env file, loading environment variables..."
    source .env
else
    echo "📝 No .env file found. Creating one..."
    echo "# InSync Environment Variables" > .env
    echo "# Get your OpenAI API key from: https://platform.openai.com/api-keys" >> .env
    echo "# Get your ElevenLabs API key from: https://elevenlabs.io/app/settings/api-keys" >> .env
    echo "" >> .env
    echo "OPENAI_API_KEY=your_openai_api_key_here" >> .env
    echo "XI_API_KEY=your_elevenlabs_api_key_here" >> .env
    echo "XI_VOICE_ID=your_voice_id_here" >> .env
    echo "" >> .env
    echo "✅ Created .env file. Please edit it with your actual API keys."
    echo "📝 Then run: source .env && python3 start_web_app.py"
    exit 0
fi

# Check if required variables are set
if [ -z "$OPENAI_API_KEY" ] || [ "$OPENAI_API_KEY" = "your_openai_api_key_here" ]; then
    echo "❌ OPENAI_API_KEY not set or still has placeholder value"
    echo "🔧 Please edit .env file and set your actual OpenAI API key"
    exit 1
fi

echo "✅ Environment variables loaded successfully"
echo "🚀 Starting InSync Web Application..."

# Start the web application
python3 start_web_app.py
