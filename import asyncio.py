import asyncio
import os
import openai
import pandas as pd
from rich.console import Console
from rich.table import Table
from playwright.async_api import async_playwright

openai.api_key = os.getenv("OPENAI_API_KEY")
console = Console()

async def extract_forms_from_url(url):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(url, timeout=60000)

        forms = await page.query_selector_all("form")
        data = []

        for form in forms:
            inputs = await form.query_selector_all("input, textarea")
            buttons = await form.query_selector_all("button, input[type=submit]")

            input_fields = []
            for inp in inputs:
                name = await inp.get_attribute("name")
                input_type = await inp.get_attribute("type")
                placeholder = await inp.get_attribute("placeholder")
                input_fields.append({
                    "name": name,
                    "type": input_type,
                    "placeholder": placeholder
                })

            button_texts = []
            for btn in buttons:
                txt = await btn.inner_text()
                if txt.strip():
                    button_texts.append(txt.strip())

            form_html = await form.inner_html()
            data.append({
                "url": url,
                "inputs": input_fields,
                "buttons": button_texts,
                "html_snippet": form_html[:500]
            })

        await browser.close()
        return data

def classify_functionality(form_data):
    prompt = f"""The following is a form found on a website:\n
Inputs: {form_data['inputs']}\n
Buttons: {form_data['buttons']}\n
HTML Snippet (partial): {form_data['html_snippet'][:300]}\n
Describe what functionality this form likely implements (e.g., login, search, contact form)."""
    
    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=0.3,
        max_tokens=150
    )
    return response.choices[0].message["content"].strip()

def display_results(results):
    table = Table(title="Discovered Website Functionalities")

    table.add_column("URL", style="cyan", no_wrap=True)
    table.add_column("Functionality", style="green")
    table.add_column("Inputs", style="white")
    table.add_column("Buttons", style="magenta")

    for res in results:
        table.add_row(
            res["url"],
            res["functionality"],
            ", ".join(i["name"] or "?" for i in res["inputs"]),
            ", ".join(res["buttons"])
        )
    console.print(table)

async def main(url):
    print(f"🔍 Crawling {url}...")
    forms = await extract_forms_from_url(url)
    print(f"🧠 Classifying functionality using GPT...")

    results = []
    for form in forms:
        func = classify_functionality(form)
        form["functionality"] = func
        results.append(form)

    # Display table
    display_results(results)

    # Save to CSV
    df = pd.DataFrame(results)
    df.to_csv("functionality_report.csv", index=False)
    print("📄 Report saved as functionality_report.csv")

# Replace with the site you want to analyze
if __name__ == "__main__":
    url_to_test = "https://example.com"  # Replace this
    asyncio.run(main(url_to_test))
import asyncio
import os
import openai
import pandas as pd
from rich.console import Console
from rich.table import Table
from playwright.async_api import async_playwright

openai.api_key = os.getenv("OPENAI_API_KEY")
console = Console()

async def extract_forms_from_url(url):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(url, timeout=60000)

        forms = await page.query_selector_all("form")
        data = []

        for form in forms:
            inputs = await form.query_selector_all("input, textarea")
            buttons = await form.query_selector_all("button, input[type=submit]")

            input_fields = []
            for inp in inputs:
                name = await inp.get_attribute("name")
                input_type = await inp.get_attribute("type")
                placeholder = await inp.get_attribute("placeholder")
                input_fields.append({
                    "name": name,
                    "type": input_type,
                    "placeholder": placeholder
                })

            button_texts = []
            for btn in buttons:
                txt = await btn.inner_text()
                if txt.strip():
                    button_texts.append(txt.strip())

            form_html = await form.inner_html()
            data.append({
                "url": url,
                "inputs": input_fields,
                "buttons": button_texts,
                "html_snippet": form_html[:500]
            })

        await browser.close()
        return data

def classify_functionality(form_data):
    prompt = f"""The following is a form found on a website:\n
Inputs: {form_data['inputs']}\n
Buttons: {form_data['buttons']}\n
HTML Snippet (partial): {form_data['html_snippet'][:300]}\n
Describe what functionality this form likely implements (e.g., login, search, contact form)."""
    
    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=0.3,
        max_tokens=150
    )
    return response.choices[0].message["content"].strip()

def display_results(results):
    table = Table(title="Discovered Website Functionalities")

    table.add_column("URL", style="cyan", no_wrap=True)
    table.add_column("Functionality", style="green")
    table.add_column("Inputs", style="white")
    table.add_column("Buttons", style="magenta")

    for res in results:
        table.add_row(
            res["url"],
            res["functionality"],
            ", ".join(i["name"] or "?" for i in res["inputs"]),
            ", ".join(res["buttons"])
        )
    console.print(table)

async def main(url):
    print(f"🔍 Crawling {url}...")
    forms = await extract_forms_from_url(url)
    print(f"🧠 Classifying functionality using GPT...")

    results = []
    for form in forms:
        func = classify_functionality(form)
        form["functionality"] = func
        results.append(form)

    # Display table
    display_results(results)

    # Save to CSV
    df = pd.DataFrame(results)
    df.to_csv("functionality_report.csv", index=False)
    print("📄 Report saved as functionality_report.csv")

# Replace with the site you want to analyze
if __name__ == "__main__":
    url_to_test = "https://example.com"  # Replace this
    asyncio.run(main(url_to_test))
