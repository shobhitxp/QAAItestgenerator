import asyncio
import os
from openai import OpenAI
import pandas as pd
from rich.console import Console
from rich.table import Table
from playwright.async_api import async_playwright
import argparse

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
console = Console()

async def extract_forms_from_url(url):
    async with async_playwright() as p:
        # Launch browser with enhanced settings
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        # Set viewport and user agent
        await page.set_viewport_size({"width": 1920, "height": 1080})
        await page.set_extra_http_headers({
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
        })
        
        console.print(f"🌐 Navigating to {url}...")
        
        # Enhanced page loading with multiple wait strategies
        await page.goto(url, timeout=60000, wait_until="networkidle")
        await page.wait_for_load_state("networkidle")
        
        # Wait for dynamic content
        console.print("⏳ Waiting for dynamic content to load...")
        await asyncio.sleep(5)
        
        # Try multiple strategies to find forms
        forms = []
        
        # Strategy 1: Standard forms
        standard_forms = await page.query_selector_all("form")
        forms.extend(standard_forms)
        
        # Strategy 2: Form-like containers
        dynamic_forms = await page.query_selector_all("div[role='form'], div[class*='form']")
        forms.extend(dynamic_forms)
        
        # Strategy 3: Any container with inputs
        input_containers = await page.query_selector_all("div:has(input), section:has(input)")
        forms.extend(input_containers)
        
        # Remove duplicates
        unique_forms = []
        seen = set()
        
        for form in forms:
            try:
                html = await form.inner_html()
                if html not in seen:
                    seen.add(html)
                    unique_forms.append(form)
            except:
                continue
        
        console.print(f"✅ Found {len(unique_forms)} potential form elements")
        
        data = []
        for i, form in enumerate(unique_forms):
            try:
                inputs = await form.query_selector_all("input, textarea, select")
                buttons = await form.query_selector_all("button, input[type=submit], input[type=button]")
                
                input_fields = []
                for inp in inputs:
                    name = await inp.get_attribute("name")
                    input_type = await inp.get_attribute("type")
                    placeholder = await inp.get_attribute("placeholder")
                    required = await inp.get_attribute("required")
                    
                    input_fields.append({
                        "name": name,
                        "type": input_type,
                        "placeholder": placeholder,
                        "required": required is not None
                    })

                button_info = []
                for btn in buttons:
                    txt = await btn.inner_text()
                    btn_name = await btn.get_attribute("name")
                    btn_value = await btn.get_attribute("value")
                    
                    if txt.strip():
                        button_info.append(txt.strip())
                    elif btn_value:
                        button_info.append(f"{btn_value} (value)")
                    elif btn_name:
                        button_info.append(f"{btn_name} (name)")
                    else:
                        button_info.append("Button")

                form_html = await form.inner_html()
                data.append({
                    "url": url,
                    "form_index": i + 1,
                    "inputs": input_fields,
                    "buttons": button_info,
                    "html_snippet": form_html[:500]
                })
                
            except Exception as e:
                console.print(f"[red]Error analyzing form {i+1}: {e}[/red]")
                continue

        await browser.close()
        return data

def classify_functionality(form_data):
    prompt = f"""Analyze this form and describe its functionality:

    URL: {form_data['url']}
    Form Index: {form_data.get('form_index', 'N/A')}
    Inputs: {form_data['inputs']}
    Buttons: {form_data['buttons']}
    HTML Snippet: {form_data['html_snippet'][:300]}

    Describe what this form likely does (e.g., search, login, contact, etc.)"""
    
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=0.3,
        max_tokens=150
    )
    return response.choices[0].message.content.strip()

def display_results(results):
    table = Table(title="Discovered Website Functionalities (JavaScript Enhanced)")

    table.add_column("URL", style="cyan", no_wrap=True)
    table.add_column("Form Index", style="blue")
    table.add_column("Functionality", style="green")
    table.add_column("Inputs", style="white")
    table.add_column("Buttons", style="magenta")

    for res in results:
        table.add_row(
            res["url"],
            str(res.get("form_index", "N/A")),
            res["functionality"],
            ", ".join(i["name"] or "?" for i in res["inputs"]),
            ", ".join(res["buttons"])
        )
    console.print(table)

async def main(url):
    print(f"🔍 Crawling {url} with JavaScript support...")
    forms = await extract_forms_from_url(url)
    
    if not forms:
        print("❌ No forms found on this website!")
        print("💡 This might be due to:")
        print("   - Forms loaded via AJAX after page load")
        print("   - Authentication required")
        print("   - Forms in iframes")
        print("   - Custom form implementations")
        return
    
    print(f"✅ Found {len(forms)} form(s)")
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
    df.to_csv("js_enhanced_functionality_report.csv", index=False)
    print("📄 Report saved as js_enhanced_functionality_report.csv")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Crawl JavaScript-heavy websites and classify forms.")
    parser.add_argument("url", type=str, help="URL of the website to analyze")
    args = parser.parse_args()
    asyncio.run(main(args.url)) 