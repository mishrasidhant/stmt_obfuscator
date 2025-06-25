#!/bin/bash
# Setup development environment for the PDF Bank Statement Obfuscator

set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Setting up development environment for PDF Bank Statement Obfuscator...${NC}"

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Python 3 is not installed. Please install Python 3.10 or higher.${NC}"
    exit 1
fi

# Check Python version
PYTHON_VERSION=$(python3 --version | cut -d ' ' -f 2)
PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d '.' -f 1)
PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d '.' -f 2)

if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 10 ]); then
    echo -e "${RED}Python 3.10 or higher is required. Found Python $PYTHON_VERSION.${NC}"
    exit 1
fi

echo -e "${GREEN}Using Python $PYTHON_VERSION${NC}"

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo -e "${YELLOW}Creating virtual environment...${NC}"
    python3 -m venv .venv
    echo -e "${GREEN}Virtual environment created.${NC}"
else
    echo -e "${GREEN}Virtual environment already exists.${NC}"
fi

# Activate virtual environment
echo -e "${YELLOW}Activating virtual environment...${NC}"
source .venv/bin/activate

# Install Poetry if not installed
if ! command -v poetry &> /dev/null; then
    echo -e "${YELLOW}Installing Poetry...${NC}"
    pip install poetry
    echo -e "${GREEN}Poetry installed.${NC}"
else
    echo -e "${GREEN}Poetry already installed.${NC}"
fi

# Install dependencies
echo -e "${YELLOW}Installing dependencies...${NC}"
poetry install
echo -e "${GREEN}Dependencies installed.${NC}"

# Install pre-commit hooks
echo -e "${YELLOW}Installing pre-commit hooks...${NC}"
pre-commit install
echo -e "${GREEN}Pre-commit hooks installed.${NC}"

# Create data directories
echo -e "${YELLOW}Creating data directories...${NC}"
mkdir -p tests/data
echo -e "${GREEN}Data directories created.${NC}"

echo -e "${GREEN}Development environment setup complete!${NC}"
echo -e "${YELLOW}To activate the virtual environment, run:${NC}"
echo -e "    source .venv/bin/activate"
echo -e "${YELLOW}To run tests, run:${NC}"
echo -e "    pytest"
echo -e "${YELLOW}To run the application, run:${NC}"
echo -e "    python -m stmt_obfuscator.main"