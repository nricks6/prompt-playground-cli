import os
import yaml
import click
import tiktoken
import csv
import openai
from datetime import datetime

from dotenv import load_dotenv
load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

def count_tokens(model, prompt):
    encoding = tiktoken.encoding_for_model(model)
    return len(encoding.encode(prompt))

PROMPT_DIR = "prompts"
HISTORY_DIR = ".prompt-history"

os.makedirs(PROMPT_DIR, exist_ok=True)
os.makedirs(HISTORY_DIR, exist_ok=True)

@click.group()
def cli():
    """Prompt Playground CLI"""
    pass

@cli.command()
@click.argument("prompt_file")
@click.option("--input", required=True, help="Input string to inject into prompt.")
def run(prompt_file, input):
    """Run a prompt from a YAML file with provided input."""
    from openai import OpenAI
    client = OpenAI()

    with open(os.path.join(PROMPT_DIR, prompt_file), 'r') as f:
        config = yaml.safe_load(f)

    prompt_template = config["prompt"]
    prompt_text = prompt_template.replace("{input}", input)
    model = config.get("model", "gpt-3.5-turbo")
    temperature = config.get("temperature", 0.7)

    # Count tokens
    encoding = tiktoken.encoding_for_model(model)
    prompt_tokens = len(encoding.encode(prompt_text))

    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt_text}],
        temperature=temperature
    )

    output = response.choices[0].message.content
    completion_tokens = response.usage.completion_tokens
    total_tokens = response.usage.total_tokens
    cost = total_tokens * 0.000002  # GPT-3.5 Turbo

    print("\nResponse:\n", output)
    print(f"\nToken usage: {total_tokens} tokens (Prompt: {prompt_tokens}, Completion: {completion_tokens})")
    print(f"Estimated cost: ${cost:.6f}")

    # Save to history
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    log_file = os.path.join(HISTORY_DIR, f"{prompt_file}-{timestamp}.txt")
    with open(log_file, 'w') as log:
        log.write(f"Input: {input}\n\nPrompt:\n{prompt_text}\n\nResponse:\n{output}\n")
        log.write(f"\nToken usage: {total_tokens} (Prompt: {prompt_tokens}, Completion: {completion_tokens})\n")
        log.write(f"Estimated cost: ${cost:.6f}\n")

@cli.command()
@click.argument("name")
def new(name):
    """Scaffold a new prompt YAML file."""
    template = {
        "name": name,
        "provider": "openai",
        "model": "gpt-3.5-turbo",
        "temperature": 0.7,
        "prompt": "Enter your prompt here with {input}",
        "few_shot_examples": []
    }
    path = os.path.join(PROMPT_DIR, f"{name}.yaml")
    with open(path, "w") as f:
        yaml.dump(template, f)
    print(f"Created new prompt at {path}")

@cli.command()
def list():
    """List all prompt files."""
    files = os.listdir(PROMPT_DIR)
    for f in files:
        print(f)

@cli.command()
@click.option("--input", help="Input text to run through all prompts.")
@click.option("--input-file", help="YAML file with 'input' field.")
@click.argument("prompt_files", nargs=-1)
def compare(input, input_file, prompt_files):
    """Compare multiple prompts with the same input."""
    from openai import OpenAI
    client = OpenAI()

    if input_file:
        with open(input_file, 'r') as f:
            input = yaml.safe_load(f)["input"]

    if not input:
        print("Error: You must provide either --input or --input-file")
        return

    results = []
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    log_file = os.path.join(HISTORY_DIR, f"compare-{timestamp}.txt")
    csv_file = os.path.join(HISTORY_DIR, f"compare-{timestamp}.csv")

    with open(log_file, 'w') as log, open(csv_file, 'w', newline='', encoding='utf-8') as csv_out:
        csv_writer = csv.writer(csv_out)
        csv_writer.writerow(["Prompt File", "Prompt Tokens", "Completion Tokens", "Total Tokens", "Estimated Cost", "Response"])

        log.write(f"Input: {input}\n\n")

        for pf in prompt_files:
            with open(os.path.join(PROMPT_DIR, pf), 'r') as f:
                config = yaml.safe_load(f)

            prompt_template = config["prompt"]
            prompt_text = prompt_template.replace("{input}", input)
            model = config.get("model", "gpt-3.5-turbo")
            temperature = config.get("temperature", 0.7)

            prompt_tokens = count_tokens(model, prompt_text)

            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt_text}],
                temperature=temperature
            )

            output = response.choices[0].message.content
            usage = response.usage
            completion_tokens = usage.completion_tokens
            total_tokens = usage.total_tokens
            cost = total_tokens * 0.000002

            results.append((pf, output, total_tokens, cost, prompt_tokens, completion_tokens))

            # Log to text
            log.write(f"Prompt: {pf}\n")
            log.write(f"Prompt Text:\n{prompt_text}\n")
            log.write(f"Response:\n{output}\n")
            log.write(f"Tokens: {total_tokens} (Prompt: {prompt_tokens}, Completion: {completion_tokens})\n")
            log.write(f"Estimated cost: ${cost:.6f}\n")
            log.write("\n" + "-" * 40 + "\n\n")

            # Log to CSV
            csv_writer.writerow([pf, prompt_tokens, completion_tokens, total_tokens, f"{cost:.6f}", output])

    print(f"\nInput:\n{input}\n\n---\nResults:\n")
    for pf, out, tokens, cost, pt, ct in results:
        print(f"Prompt: {pf}\nResponse: {out}\nTokens: {tokens} (Prompt: {pt}, Completion: {ct})\nEstimated cost: ${cost:.6f}\n{'-' * 40}")

if __name__ == "__main__":
    cli()
    cli()