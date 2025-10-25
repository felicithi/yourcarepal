#!/bin/bash

# YourCarePal Deployment Script
echo "🩺 YourCarePal Deployment Script"
echo "================================="

# Check if we're in the right directory
if [ ! -f "app.py" ]; then
    echo "❌ Error: app.py not found. Please run this script from the project root."
    exit 1
fi

# Function to deploy to different platforms
deploy_streamlit_cloud() {
    echo "🚀 Deploying to Streamlit Cloud..."
    echo "1. Push your code to GitHub:"
    echo "   git add ."
    echo "   git commit -m 'Deploy YourCarePal'"
    echo "   git push origin main"
    echo ""
    echo "2. Go to https://share.streamlit.io"
    echo "3. Connect your GitHub repository"
    echo "4. Set main file path: app.py"
    echo "5. Add environment variable: OPENAI_API_KEY (optional)"
    echo "6. Click Deploy!"
}

deploy_heroku() {
    echo "🚀 Deploying to Heroku..."
    if ! command -v heroku &> /dev/null; then
        echo "❌ Heroku CLI not found. Please install it first:"
        echo "   brew install heroku/brew/heroku"
        exit 1
    fi
    
    echo "Creating Heroku app..."
    heroku create yourcarepal-$(date +%s)
    
    echo "Setting environment variables..."
    read -p "Enter your OpenAI API key (or press Enter to skip): " api_key
    if [ ! -z "$api_key" ]; then
        heroku config:set OPENAI_API_KEY="$api_key"
    fi
    
    echo "Deploying..."
    git push heroku main
    
    echo "✅ Deployment complete!"
    heroku open
}

deploy_docker() {
    echo "🐳 Building Docker image..."
    docker build -t yourcarepal .
    
    echo "🚀 Running container..."
    docker run -d -p 8501:8501 --name yourcarepal-app yourcarepal
    
    echo "✅ Docker deployment complete!"
    echo "🌐 Access your app at: http://localhost:8501"
}

deploy_local() {
    echo "🏠 Running locally..."
    echo "Installing dependencies..."
    pip3 install -r requirements.txt
    
    echo "Starting application..."
    streamlit run app.py
}

# Main menu
echo "Choose deployment option:"
echo "1) Streamlit Cloud (Free, Recommended)"
echo "2) Heroku"
echo "3) Docker"
echo "4) Local Development"
echo "5) Show all commands"

read -p "Enter your choice (1-5): " choice

case $choice in
    1)
        deploy_streamlit_cloud
        ;;
    2)
        deploy_heroku
        ;;
    3)
        deploy_docker
        ;;
    4)
        deploy_local
        ;;
    5)
        echo ""
        echo "📋 All Deployment Commands:"
        echo "========================="
        echo ""
        echo "🌐 Streamlit Cloud:"
        echo "   git add . && git commit -m 'Deploy' && git push"
        echo "   Then go to https://share.streamlit.io"
        echo ""
        echo "🚀 Heroku:"
        echo "   heroku create yourcarepal-app"
        echo "   heroku config:set OPENAI_API_KEY=your_key"
        echo "   git push heroku main"
        echo ""
        echo "🐳 Docker:"
        echo "   docker build -t yourcarepal ."
        echo "   docker run -p 8501:8501 yourcarepal"
        echo ""
        echo "🏠 Local:"
        echo "   pip3 install -r requirements.txt"
        echo "   streamlit run app.py"
        ;;
    *)
        echo "❌ Invalid choice. Please run the script again."
        exit 1
        ;;
esac

echo ""
echo "🎉 Deployment setup complete!"
echo "📖 For detailed instructions, see DEPLOYMENT.md"
