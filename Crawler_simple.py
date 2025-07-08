import asyncio
import os
import pandas as pd
from rich.console import Console
from rich.table import Table
from playwright.async_api import async_playwright
import argparse

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

def display_results(results):
    table = Table(title="Discovered Forms on Website")

    table.add_column("URL", style="cyan", no_wrap=True)
    table.add_column("Input Fields", style="white")
    table.add_column("Input Types", style="yellow")
    table.add_column("Buttons", style="magenta")
    table.add_column("Placeholders", style="green")

    for res in results:
        input_names = ", ".join(i["name"] or "unnamed" for i in res["inputs"])
        input_types = ", ".join(i["type"] or "text" for i in res["inputs"])
        placeholders = ", ".join(i["placeholder"] or "none" for i in res["inputs"])
        
        table.add_row(
            res["url"],
            input_names,
            input_types,
            ", ".join(res["buttons"]),
            placeholders
        )
    console.print(table)

async def main(url):
    print(f"🔍 Crawling {url}...")
    forms = await extract_forms_from_url(url)
    
    if not forms:
        print("❌ No forms found on this website!")
        return
    
    print(f"✅ Found {len(forms)} form(s)")

    # Display table
    display_results(forms)

    # Save to CSV
    df = pd.DataFrame(forms)
    df.to_csv("forms_report.csv", index=False)
    print("📄 Report saved as forms_report.csv")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Crawl a website and extract form information.")
    parser.add_argument("url", type=str, help="URL of the website to analyze")
    args = parser.parse_args()
    asyncio.run(main(args.url)) 