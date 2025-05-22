A developer-friendly command-line tool for managing, testing, and comparing prompt templates with OpenAI's GPT models—designed to make prompt engineering reproducible, versionable, and fast.

# 🚀 Features

- Run prompt templates with dynamic input
- Compare multiple prompt versions side-by-side
- Track token usage and estimate API cost
- Log results to .txt and .csv files
- Scaffold new prompts using a consistent YAML format

# 🛠️ Installation

## Clone the repo
git clone https://github.com/your-username/prompt-playground-cli.git
cd prompt-playground-cli

## Set up virtual environment
python -m venv venv
source venv/Scripts/activate  # On Windows

## Install dependencies
pip install -r requirements.txt

## Install CLI in editable mode
pip install -e .

# 🧪 Usage Examples

## Create a new prompt scaffold

prompt-cli new summarize-v1

Example prompt file (YAML)

name: summarize-v1
model: gpt-3.5-turbo
temperature: 0.7
prompt: |
  Summarize this in one sentence:
  {input}

## Run a prompt

prompt-cli run summarize-v1.yaml --input "AI is transforming healthcare."

## Compare multiple prompts

prompt-cli compare --input "Summarize AI trends in 2024." summarize-v1.yaml summarize-v2.yaml

Saves .txt and .csv logs to .prompt-history/

## List available prompts

prompt-cli list

# 🔐 Environment Variables

Create a .env file in your project root:

OPENAI_API_KEY=your-openai-api-key

Or set it in your terminal session:

$env:OPENAI_API_KEY="your-openai-api-key"  # Windows PowerShell

# 📁 File Structure

prompt-playground-cli/
├── prompt_cli/             # CLI source code
├── prompts/                # Prompt YAML templates
├── .prompt-history/        # Output logs and comparison results
├── requirements.txt
├── setup.cfg
├── README.md
└── .gitignore

# 📄 License

MIT License