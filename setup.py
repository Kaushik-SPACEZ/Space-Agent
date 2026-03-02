"""
Setup script for Earth Observation Agent
Helps with initial setup and configuration
"""
import os
import sys
from pathlib import Path


def create_env_file():
    """Create .env file from template"""
    env_example = Path(".env.example")
    env_file = Path(".env")
    
    if env_file.exists():
        print("✅ .env file already exists")
        return
    
    if not env_example.exists():
        print("❌ .env.example not found")
        return
    
    # Copy template
    with open(env_example, 'r') as f:
        content = f.read()
    
    with open(env_file, 'w') as f:
        f.write(content)
    
    print("✅ Created .env file from template")
    print("⚠️  Please edit .env and add your OpenAI API key")


def check_python_version():
    """Check Python version"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 10):
        print(f"❌ Python 3.10+ required, you have {version.major}.{version.minor}")
        return False
    print(f"✅ Python version: {version.major}.{version.minor}.{version.micro}")
    return True


def check_directories():
    """Ensure required directories exist"""
    directories = ['data', 'agents', 'pipelines', 'services', 'models']
    
    for directory in directories:
        path = Path(directory)
        if not path.exists():
            print(f"❌ Directory missing: {directory}")
            return False
        print(f"✅ Directory exists: {directory}")
    
    return True


def check_data_files():
    """Check if data files exist"""
    data_files = ['data/flood_data.csv', 'data/vegetation_data.csv']
    
    for file in data_files:
        path = Path(file)
        if not path.exists():
            print(f"❌ Data file missing: {file}")
            return False
        print(f"✅ Data file exists: {file}")
    
    return True


def check_dependencies():
    """Check if dependencies are installed"""
    try:
        import fastapi
        import uvicorn
        import pydantic
        import pandas
        import openai
        print("✅ All required packages are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing package: {str(e)}")
        print("Run: pip install -r requirements.txt")
        return False


def main():
    """Main setup function"""
    print("="*80)
    print("EARTH OBSERVATION AGENT - SETUP")
    print("="*80)
    print()
    
    # Check Python version
    if not check_python_version():
        return
    
    print()
    
    # Check directories
    if not check_directories():
        print("\n❌ Setup incomplete: Missing directories")
        return
    
    print()
    
    # Check data files
    if not check_data_files():
        print("\n❌ Setup incomplete: Missing data files")
        return
    
    print()
    
    # Create .env file
    create_env_file()
    
    print()
    
    # Check dependencies
    if not check_dependencies():
        print("\n❌ Setup incomplete: Missing dependencies")
        print("Run: pip install -r requirements.txt")
        return
    
    print()
    print("="*80)
    print("✅ SETUP COMPLETE!")
    print("="*80)
    print()
    print("Next steps:")
    print("1. Edit .env file and add your OpenAI API key")
    print("2. Run: python main.py")
    print("3. Visit: http://localhost:8000/docs")
    print()
    print("To test the API:")
    print("  python test_queries.py")
    print()


if __name__ == "__main__":
    main()