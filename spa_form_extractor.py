#!/usr/bin/env python3
"""
SPA Form Extractor
Specialized form extractor for Single Page Applications (SPAs)
Handles dynamically generated forms and React components
"""

import asyncio
import json
import time
from playwright.async_api import async_playwright
from rich.console import Console
from rich.table import Table

console = Console()

async def extract_spa_forms(url):
    """Extract forms from Single Page Applications"""
    async with async_playwright() as p:
        # Use a more realistic browser configuration
        browser = await p.chromium.launch(
            headless=True,
            args=[
                '--no-sandbox',
                '--disable-blink-features=AutomationControlled',
                '--disable-dev-shm-usage',
                '--disable-web-security',
                '--disable-features=VizDisplayCompositor'
            ]
        )
        
        # Create context with realistic user agent
        context = await browser.new_context(
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            viewport={'width': 1920, 'height': 1080},
            locale='en-US',
            timezone_id='America/New_York'
        )
        
        page = await context.new_page()
        
        # Set up stealth mode
        await page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined,
            });
        """)
        
        console.print(f"[yellow]Navigating to SPA: {url}[/yellow]")
        
        try:
            # Load the page with longer timeout
            await page.goto(url, timeout=120000, wait_until="domcontentloaded")
            console.print("[green]Initial page load complete[/green]")
            
            # Wait for React/Angular to load
            await page.wait_for_timeout(3000)
            
            # Wait for dynamic content
            try:
                await page.wait_for_load_state("networkidle", timeout=30000)
                console.print("[green]Network idle achieved[/green]")
            except:
                console.print("[yellow]Network may still be active, continuing...[/yellow]")
            
            # Additional wait for JavaScript frameworks
            await page.wait_for_timeout(5000)
            
            # Check for React/Angular/Vue indicators
            framework_indicators = await page.evaluate("""
                () => {
                    const indicators = {
                        react: !!document.querySelector('[data-reactroot], [data-reactid]'),
                        angular: !!document.querySelector('[ng-version], [ng-app]'),
                        vue: !!document.querySelector('[data-v-]'),
                        spa: !!document.querySelector('[data-testid], [data-cy]')
                    };
                    return indicators;
                }
            """)
            
            console.print(f"[blue]Framework detected: {framework_indicators}[/blue]")
            
            # Try multiple strategies to find forms
            forms_data = []
            
            # Strategy 1: Traditional form elements
            console.print("[yellow]Strategy 1: Looking for traditional form elements[/yellow]")
            traditional_forms = await page.query_selector_all("form")
            console.print(f"Found {len(traditional_forms)} traditional forms")
            
            # Strategy 2: Form-like elements (divs with form behavior)
            console.print("[yellow]Strategy 2: Looking for form-like elements[/yellow]")
            form_like_elements = await page.query_selector_all("""
                div[role='form'],
                div[data-testid*='form'],
                div[class*='form'],
                div[id*='form'],
                section[role='form'],
                section[data-testid*='form']
            """)
            console.print(f"Found {len(form_like_elements)} form-like elements")
            
            # Strategy 3: Input containers
            console.print("[yellow]Strategy 3: Looking for input containers[/yellow]")
            input_containers = await page.query_selector_all("""
                div:has(input),
                div:has(select),
                div:has(textarea),
                section:has(input),
                section:has(select),
                section:has(textarea)
            """)
            console.print(f"Found {len(input_containers)} input containers")
            
            # Strategy 4: Button groups (potential form triggers)
            console.print("[yellow]Strategy 4: Looking for button groups[/yellow]")
            button_groups = await page.query_selector_all("""
                div:has(button),
                div:has(input[type='submit']),
                div:has(input[type='button']),
                section:has(button),
                section:has(input[type='submit']),
                section:has(input[type='button'])
            """)
            console.print(f"Found {len(button_groups)} button groups")
            
            # Strategy 5: Modal/Dialog forms
            console.print("[yellow]Strategy 5: Looking for modal/dialog forms[/yellow]")
            modal_forms = await page.query_selector_all("""
                [role='dialog']:has(input),
                [role='dialog']:has(select),
                [role='dialog']:has(textarea),
                .modal:has(input),
                .modal:has(select),
                .modal:has(textarea),
                .dialog:has(input),
                .dialog:has(select),
                .dialog:has(textarea)
            """)
            console.print(f"Found {len(modal_forms)} modal/dialog forms")
            
            # Process traditional forms
            for i, form in enumerate(traditional_forms):
                console.print(f"[yellow]Processing traditional form {i+1}[/yellow]")
                form_data = await extract_form_data(page, form, f"traditional_form_{i+1}")
                forms_data.append(form_data)
            
            # Process form-like elements
            for i, element in enumerate(form_like_elements):
                console.print(f"[yellow]Processing form-like element {i+1}[/yellow]")
                form_data = await extract_form_data(page, element, f"form_like_{i+1}")
                forms_data.append(form_data)
            
            # Process input containers
            for i, container in enumerate(input_containers[:5]):  # Limit to first 5
                console.print(f"[yellow]Processing input container {i+1}[/yellow]")
                form_data = await extract_form_data(page, container, f"input_container_{i+1}")
                forms_data.append(form_data)
            
            # Process modal forms
            for i, modal in enumerate(modal_forms):
                console.print(f"[yellow]Processing modal form {i+1}[/yellow]")
                form_data = await extract_form_data(page, modal, f"modal_form_{i+1}")
                forms_data.append(form_data)
            
            # Try to trigger dynamic form loading
            console.print("[yellow]Attempting to trigger dynamic form loading...[/yellow]")
            
            # Click common triggers that might reveal forms (fixed selectors)
            triggers = await page.query_selector_all("""
                button,
                input[type='submit'],
                input[type='button'],
                a[href*='contact'],
                a[href*='sign'],
                a[href*='register'],
                a[href*='login']
            """)
            
            console.print(f"Found {len(triggers)} potential form triggers")
            
            # Filter triggers by text content
            form_triggers = []
            for trigger in triggers[:10]:  # Check first 10 triggers
                try:
                    text = await trigger.inner_text()
                    if text and any(keyword in text.lower() for keyword in ['add', 'create', 'new', 'submit', 'contact', 'sign', 'register', 'login', 'email', 'message']):
                        form_triggers.append(trigger)
                except:
                    continue
            
            console.print(f"Found {len(form_triggers)} form-related triggers")
            
            # Try clicking a few triggers to see if forms appear
            for i, trigger in enumerate(form_triggers[:3]):  # Limit to first 3
                try:
                    console.print(f"[yellow]Clicking trigger {i+1}[/yellow]")
                    await trigger.click()
                    await page.wait_for_timeout(2000)
                    
                    # Check for new forms after click
                    new_forms = await page.query_selector_all("form, div[role='form'], .modal:has(input)")
                    if new_forms:
                        console.print(f"[green]Found {len(new_forms)} new forms after trigger click[/green]")
                        for j, new_form in enumerate(new_forms):
                            form_data = await extract_form_data(page, new_form, f"dynamic_form_{i+1}_{j+1}")
                            forms_data.append(form_data)
                    
                    # Go back if we navigated away
                    if page.url != url:
                        await page.goto(url)
                        await page.wait_for_timeout(2000)
                        
                except Exception as e:
                    console.print(f"[red]Error clicking trigger {i+1}: {e}[/red]")
                    continue
            
            await browser.close()
            return forms_data
            
        except Exception as e:
            console.print(f"[red]Error extracting SPA forms: {e}[/red]")
            await browser.close()
            return []

async def extract_form_data(page, element, form_id):
    """Extract comprehensive form data from an element"""
    try:
        # Get basic element info
        tag_name = await element.evaluate("el => el.tagName.toLowerCase()")
        element_id = await element.get_attribute("id")
        element_class = await element.get_attribute("class")
        element_role = await element.get_attribute("role")
        
        # Get all inputs within this element
        inputs = await element.query_selector_all("input, textarea, select")
        input_data = []
        
        for inp in inputs:
            try:
                input_info = {
                    "name": await inp.get_attribute("name"),
                    "type": await inp.get_attribute("type"),
                    "id": await inp.get_attribute("id"),
                    "class": await inp.get_attribute("class"),
                    "placeholder": await inp.get_attribute("placeholder"),
                    "required": await inp.get_attribute("required") is not None,
                    "value": await inp.get_attribute("value"),
                    "disabled": await inp.get_attribute("disabled") is not None,
                    "readonly": await inp.get_attribute("readonly") is not None,
                    "maxlength": await inp.get_attribute("maxlength"),
                    "pattern": await inp.get_attribute("pattern"),
                    "aria_label": await inp.get_attribute("aria-label"),
                    "data_testid": await inp.get_attribute("data-testid"),
                    "data_cy": await inp.get_attribute("data-cy")
                }
                input_data.append(input_info)
            except Exception as e:
                console.print(f"[red]Error processing input: {e}[/red]")
                continue
        
        # Get all buttons within this element
        buttons = await element.query_selector_all("button, input[type='submit'], input[type='button']")
        button_data = []
        
        for btn in buttons:
            try:
                button_text = await btn.inner_text()
                button_info = {
                    "text": button_text.strip() if button_text.strip() else None,
                    "type": await btn.get_attribute("type"),
                    "id": await btn.get_attribute("id"),
                    "class": await btn.get_attribute("class"),
                    "disabled": await btn.get_attribute("disabled") is not None,
                    "data_testid": await btn.get_attribute("data-testid"),
                    "data_cy": await btn.get_attribute("data-cy")
                }
                button_data.append(button_info)
            except Exception as e:
                console.print(f"[red]Error processing button: {e}[/red]")
                continue
        
        # Get element HTML for analysis
        html_snippet = await element.inner_html()
        
        return {
            "form_id": form_id,
            "element_type": tag_name,
            "element_id": element_id,
            "element_class": element_class,
            "element_role": element_role,
            "inputs": input_data,
            "buttons": button_data,
            "input_count": len(input_data),
            "button_count": len(button_data),
            "html_snippet": html_snippet[:500]
        }
        
    except Exception as e:
        console.print(f"[red]Error extracting form data: {e}[/red]")
        return {
            "form_id": form_id,
            "error": str(e),
            "inputs": [],
            "buttons": [],
            "input_count": 0,
            "button_count": 0
        }

def display_spa_form_data(forms_data):
    """Display SPA form data in a comprehensive table"""
    
    if not forms_data:
        console.print("[red]No forms found in the SPA[/red]")
        return
    
    console.print(f"\n[bold green]Found {len(forms_data)} potential form elements[/bold green]")
    
    for i, form in enumerate(forms_data):
        console.print(f"\n[bold blue]Form {i+1}: {form['form_id']}[/bold blue]")
        console.print(f"Element Type: {form.get('element_type', 'N/A')}")
        console.print(f"Element ID: {form.get('element_id', 'N/A')}")
        console.print(f"Element Class: {form.get('element_class', 'N/A')}")
        console.print(f"Element Role: {form.get('element_role', 'N/A')}")
        console.print(f"Inputs: {form.get('input_count', 0)}")
        console.print(f"Buttons: {form.get('button_count', 0)}")
        
        if form.get('inputs'):
            console.print(f"\n[yellow]Inputs:[/yellow]")
            input_table = Table(show_header=True, header_style="bold magenta")
            input_table.add_column("Name")
            input_table.add_column("Type")
            input_table.add_column("ID")
            input_table.add_column("Required")
            input_table.add_column("Test ID")
            
            for inp in form['inputs']:
                input_table.add_row(
                    inp.get('name', 'N/A'),
                    inp.get('type', 'N/A'),
                    inp.get('id', 'N/A'),
                    "Yes" if inp.get('required') else "No",
                    inp.get('data_testid', 'N/A')
                )
            console.print(input_table)
        
        if form.get('buttons'):
            console.print(f"\n[yellow]Buttons:[/yellow]")
            button_table = Table(show_header=True, header_style="bold magenta")
            button_table.add_column("Text")
            button_table.add_column("Type")
            button_table.add_column("ID")
            button_table.add_column("Test ID")
            
            for btn in form['buttons']:
                button_table.add_row(
                    btn.get('text', 'N/A'),
                    btn.get('type', 'N/A'),
                    btn.get('id', 'N/A'),
                    btn.get('data_testid', 'N/A')
                )
            console.print(button_table)

async def main():
    """Main function to test SPA form extraction"""
    console.print("[bold green]SPA Form Extractor[/bold green]")
    console.print("Specialized extractor for Single Page Applications")
    
    # Test with the problematic URL
    url = "https://shop.deere.com/us/diagrams?dealer-id=036816&story=st969494&catalog_no=11945"
    
    console.print(f"\n[bold]Testing SPA: {url}[/bold]")
    
    try:
        forms_data = await extract_spa_forms(url)
        
        if not forms_data:
            console.print("[red]No forms found in the SPA[/red]")
            console.print("[yellow]This might be because:[/yellow]")
            console.print("1. The site uses a different form pattern")
            console.print("2. Forms are loaded via AJAX after user interaction")
            console.print("3. The site has strong bot protection")
            console.print("4. Forms are in iframes or shadow DOM")
        else:
            display_spa_form_data(forms_data)
            
            # Save the data
            with open("spa_form_data.json", "w") as f:
                json.dump(forms_data, f, indent=2)
            console.print(f"\n[green]Form data saved to: spa_form_data.json[/green]")
        
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")

if __name__ == "__main__":
    asyncio.run(main()) 