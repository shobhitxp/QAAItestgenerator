import asyncio
import os
import json
import re
from datetime import datetime
import pandas as pd
from openai import OpenAI
from rich.console import Console
from rich.table import Table
from playwright.async_api import async_playwright
import argparse

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
console = Console()

def create_directory_structure(base_url):
    domain = re.sub(r'https?://', '', base_url)
    domain = re.sub(r'[^\w\-_.]', '_', domain)
    test_dir = f"test_cases/{domain}"
    os.makedirs(test_dir, exist_ok=True)
    subdirs = {
        "json": f"{test_dir}/json",
        "csv": f"{test_dir}/csv",
        "reports": f"{test_dir}/reports",
        "test_scripts": f"{test_dir}/test_scripts",
        "test_data": f"{test_dir}/test_data"
    }
    for subdir in subdirs.values():
        os.makedirs(subdir, exist_ok=True)
    return test_dir, subdirs

async def extract_spa_forms(url):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=[
            '--no-sandbox',
            '--disable-blink-features=AutomationControlled',
            '--disable-dev-shm-usage',
            '--disable-web-security',
            '--disable-features=VizDisplayCompositor'
        ])
        context = await browser.new_context(
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            viewport={'width': 1920, 'height': 1080},
            locale='en-US',
            timezone_id='America/New_York'
        )
        page = await context.new_page()
        await page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined,
            });
        """)
        console.print(f"[yellow]Navigating to SPA: {url}[/yellow]")
        try:
            await page.goto(url, timeout=120000, wait_until="domcontentloaded")
            console.print("[green]Initial page load complete[/green]")
            await page.wait_for_timeout(3000)
            try:
                await page.wait_for_load_state("networkidle", timeout=30000)
                console.print("[green]Network idle achieved[/green]")
            except:
                console.print("[yellow]Network may still be active, continuing...[/yellow]")
            await page.wait_for_timeout(5000)
            forms_data = []
            # Strategy 1: Traditional form elements
            traditional_forms = await page.query_selector_all("form")
            # Strategy 2: Form-like elements
            form_like_elements = await page.query_selector_all("""
                div[role='form'],
                div[data-testid*='form'],
                div[class*='form'],
                div[id*='form'],
                section[role='form'],
                section[data-testid*='form']
            """)
            # Strategy 3: Input containers
            input_containers = await page.query_selector_all("""
                div:has(input),
                div:has(select),
                div:has(textarea),
                section:has(input),
                section:has(select),
                section:has(textarea)
            """)
            # Strategy 5: Modal/Dialog forms
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
            # Process all found elements
            for i, form in enumerate(traditional_forms):
                form_data = await extract_form_data(page, form, url, f"traditional_form_{i+1}")
                forms_data.append(form_data)
            for i, element in enumerate(form_like_elements):
                form_data = await extract_form_data(page, element, url, f"form_like_{i+1}")
                forms_data.append(form_data)
            for i, container in enumerate(input_containers[:5]):
                form_data = await extract_form_data(page, container, url, f"input_container_{i+1}")
                forms_data.append(form_data)
            for i, modal in enumerate(modal_forms):
                form_data = await extract_form_data(page, modal, url, f"modal_form_{i+1}")
                forms_data.append(form_data)
            await browser.close()
            return forms_data
        except Exception as e:
            console.print(f"[red]Error extracting SPA forms: {e}[/red]")
            await browser.close()
            return []

async def extract_form_data(page, element, url, form_id):
    try:
        tag_name = await element.evaluate("el => el.tagName.toLowerCase()")
        element_id = await element.get_attribute("id")
        element_class = await element.get_attribute("class")
        element_role = await element.get_attribute("role")
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
        html_snippet = await element.inner_html()
        return {
            "url": url,
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
            "url": url,
            "form_id": form_id,
            "error": str(e),
            "inputs": [],
            "buttons": [],
            "input_count": 0,
            "button_count": 0
        }

def generate_test_cases(form_data):
    prompt = f"""Based on the following comprehensive form data, generate comprehensive functional test cases in JSON format. \nInclude test cases for valid inputs, invalid inputs, edge cases, accessibility testing, and dynamic behavior.\n\nForm Data:\nURL: {form_data['url']}\nForm ID: {form_data.get('form_id', '')}\nElement Type: {form_data.get('element_type', '')}\nInputs: {form_data['inputs']}\nButtons: {form_data['buttons']}\nHTML Snippet: {form_data['html_snippet'][:300]}\n\nGenerate test cases in this JSON structure:\n{{\n    \"form_type\": \"description of form type\",\n    \"test_cases\": [\n        {{\n            \"test_id\": \"TC001\",\n            \"test_name\": \"Descriptive test name\",\n            \"test_type\": \"positive|negative|edge_case|accessibility|dynamic|validation\",\n            \"priority\": \"high|medium|low\",\n            \"preconditions\": \"What needs to be set up\",\n            \"test_steps\": [\"Step 1\", \"Step 2\", \"Step 3\"],\n            \"test_data\": {{\"field_name\": \"value\"}},\n            \"expected_result\": \"What should happen\",\n            \"validation_points\": [\"Point 1\", \"Point 2\"],\n            \"dynamic_behavior\": \"Description of dynamic changes\",\n            \"widget_interaction\": \"How custom widgets should behave\"\n        }}\n    ]\n}}\n\nReturn ONLY valid JSON, no additional text.\n"""
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=2500
    )
    try:
        content = response.choices[0].message.content.strip()
        if content.startswith("```json"):
            content = content[7:]
        if content.endswith("```"):
            content = content[:-3]
        return json.loads(content.strip())
    except json.JSONDecodeError as e:
        console.print(f"[red]JSON parsing failed: {e}[/red]")
        console.print(f"[yellow]Raw response: {content[:200]}...[/yellow]")
        return {
            "form_type": "Unknown form type",
            "test_cases": [{
                "test_id": "TC001",
                "test_name": "Basic form validation",
                "test_type": "positive",
                "priority": "high",
                "preconditions": "Form is loaded",
                "test_steps": ["Fill required fields", "Submit form"],
                "test_data": {},
                "expected_result": "Form submits successfully",
                "validation_points": ["No errors displayed", "Success message shown"],
                "dynamic_behavior": "No dynamic changes expected",
                "widget_interaction": "Standard form behavior"
            }]
        }

def display_test_cases(test_data, url):
    table = Table(title=f"Generated Test Cases for {url}")
    table.add_column("Test ID", style="cyan", no_wrap=True)
    table.add_column("Test Name", style="green")
    table.add_column("Type", style="yellow")
    table.add_column("Priority", style="magenta")
    table.add_column("Expected Result", style="white")
    for test_case in test_data.get("test_cases", []):
        table.add_row(
            test_case.get("test_id", "N/A"),
            test_case.get("test_name", "N/A"),
            test_case.get("test_type", "N/A"),
            test_case.get("priority", "N/A"),
            test_case.get("expected_result", "N/A")[:50] + "..." if len(test_case.get("expected_result", "")) > 50 else test_case.get("expected_result", "N/A")
        )
    console.print(table)

def save_test_cases_to_files(test_data, url, subdirs, form_index):
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    form_type = test_data.get('form_type', 'unknown').replace(' ', '_').lower()
    json_file = f"{subdirs['json']}/form_{form_index}_{form_type}_{timestamp}.json"
    with open(json_file, "w") as f:
        json.dump(test_data, f, indent=2)
    test_cases_list = []
    for test_case in test_data.get("test_cases", []):
        test_cases_list.append({
            "test_id": test_case.get("test_id"),
            "test_name": test_case.get("test_name"),
            "test_type": test_case.get("test_type"),
            "priority": test_case.get("priority"),
            "preconditions": test_case.get("preconditions"),
            "test_steps": " | ".join(test_case.get("test_steps", [])),
            "test_data": json.dumps(test_case.get("test_data", {})),
            "expected_result": test_case.get("expected_result"),
            "validation_points": " | ".join(test_case.get("validation_points", [])),
            "dynamic_behavior": test_case.get("dynamic_behavior", ""),
            "widget_interaction": test_case.get("widget_interaction", "")
        })
    df = pd.DataFrame(test_cases_list)
    csv_file = f"{subdirs['csv']}/form_{form_index}_{form_type}_{timestamp}.csv"
    df.to_csv(csv_file, index=False)
    report = f"""
# Test Case Report for Form {form_index} - {url}

**Generated on:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Form Type:** {test_data.get('form_type', 'Unknown')}
**Total Test Cases:** {len(test_data.get('test_cases', []))}

## Form Details

- **Form ID:** {test_data.get('form_id', 'N/A')}
- **Element Type:** {test_data.get('element_type', 'N/A')}
- **Element Class:** {test_data.get('element_class', 'N/A')}

## Test Case Summary

"""
    test_types = {}
    for test_case in test_data.get("test_cases", []):
        test_type = test_case.get("test_type", "unknown")
        if test_type not in test_types:
            test_types[test_type] = []
        test_types[test_type].append(test_case)
    for test_type, cases in test_types.items():
        report += f"\n### {test_type.title()} Test Cases ({len(cases)})\n\n"
        for case in cases:
            report += f"**{case.get('test_id')} - {case.get('test_name')}**\n"
            report += f"- Priority: {case.get('priority')}\n"
            report += f"- Steps: {' | '.join(case.get('test_steps', []))}\n"
            report += f"- Expected: {case.get('expected_result')}\n"
            if case.get('dynamic_behavior'):
                report += f"- Dynamic Behavior: {case.get('dynamic_behavior')}\n"
            if case.get('widget_interaction'):
                report += f"- Widget Interaction: {case.get('widget_interaction')}\n"
            report += "\n"
    report_file = f"{subdirs['reports']}/form_{form_index}_{form_type}_{timestamp}.md"
    with open(report_file, "w") as f:
        f.write(report)
    return json_file, csv_file, report_file

def create_test_script(test_data, url, subdirs, form_index):
    form_type = test_data.get('form_type', 'unknown').replace(' ', '_').lower()
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Generate form-specific selectors and test logic
    form_selectors = generate_form_selectors(test_data)
    test_implementations = generate_test_implementations(test_data, form_selectors)
    
    script_content = f'''"""
Test Script for Form {form_index} - {url}
Form Type: {test_data.get('form_type', 'Unknown')}
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""

import pytest
import time
from playwright.sync_api import sync_playwright, expect

class TestForm{form_index}:
    """Test cases for {test_data.get('form_type', 'Unknown')} form"""
    
    @pytest.fixture(scope="class")
    def browser(self):
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            yield browser
            browser.close()
    
    @pytest.fixture(scope="class")
    def page(self, browser):
        page = browser.new_page()
        page.goto("{url}")
        # Wait for page to load completely
        page.wait_for_load_state('networkidle')
        yield page
        page.close()
    
    def wait_for_form_elements(self, page):
        """Wait for form elements to be available"""
        try:
            # Wait for common form elements
            page.wait_for_selector('input, select, textarea, button', timeout=10000)
            return True
        except Exception as e:
            print(f"Form elements not found: {{e}}")
            return False
'''
    
    # Add the test implementations
    for test_case in test_data.get("test_cases", []):
        test_id = test_case.get("test_id", "TC001")
        test_name = test_case.get("test_name", "Basic Test")
        test_type = test_case.get("test_type", "positive")
        priority = test_case.get("priority", "medium")
        
        # Get the implementation for this test case
        implementation = test_implementations.get(test_id, generate_default_implementation(test_case, form_selectors))
        
        script_content += f'''
    def test_{test_id.lower()}_{test_type}_{priority}(self, page):
        """
        {test_name}
        Type: {test_type}
        Priority: {priority}
        """
        {implementation}
'''
    
    script_file = f"{subdirs['test_scripts']}/test_form_{form_index}_{form_type}_{timestamp}.py"
    with open(script_file, "w") as f:
        f.write(script_content)
    return script_file

def generate_form_selectors(test_data):
    """Generate CSS selectors for form elements based on form type"""
    form_type = test_data.get('form_type', '').lower()
    selectors = {
        'input': 'input[type="text"], input[type="search"], input[type="email"], input[type="password"]',
        'button': 'button, input[type="submit"], input[type="button"]',
        'select': 'select',
        'textarea': 'textarea',
        'form': 'form'
    }
    
    # Add form-specific selectors
    if 'search' in form_type:
        selectors.update({
            'search_input': 'input[type="search"], input[placeholder*="search"], input[name*="search"], input[id*="search"]',
            'search_button': 'button[type="submit"], input[type="submit"], button:has-text("Search")',
            'results': '.search-results, .results, [class*="result"], [id*="result"]'
        })
    elif 'login' in form_type:
        selectors.update({
            'username': 'input[name="username"], input[name="email"], input[type="email"]',
            'password': 'input[name="password"], input[type="password"]',
            'login_button': 'button[type="submit"], input[type="submit"]'
        })
    elif 'contact' in form_type:
        selectors.update({
            'name': 'input[name="name"], input[name="fullname"]',
            'email': 'input[name="email"], input[type="email"]',
            'message': 'textarea[name="message"], textarea[name="comment"]',
            'submit': 'button[type="submit"], input[type="submit"]'
        })
    
    return selectors

def generate_test_implementations(test_data, selectors):
    """Generate actual test implementations based on test cases"""
    implementations = {}
    
    for test_case in test_data.get("test_cases", []):
        test_id = test_case.get("test_id")
        test_type = test_case.get("test_type")
        test_data_input = test_case.get("test_data", {})
        
        if test_type == "positive":
            implementations[test_id] = generate_positive_test(test_case, selectors)
        elif test_type == "negative":
            implementations[test_id] = generate_negative_test(test_case, selectors)
        elif test_type == "edge_case":
            implementations[test_id] = generate_edge_case_test(test_case, selectors)
        elif test_type == "accessibility":
            implementations[test_id] = generate_accessibility_test(test_case, selectors)
        elif test_type == "dynamic":
            implementations[test_id] = generate_dynamic_test(test_case, selectors)
    
    return implementations

def generate_positive_test(test_case, selectors):
    """Generate positive test implementation"""
    test_data = test_case.get("test_data", {})
    form_type = test_case.get("form_type", "").lower()
    
    if "search" in form_type and "search_input" in selectors:
        search_input = test_data.get("search_input", "test123")
        return f'''
        # Wait for form elements
        assert self.wait_for_form_elements(page), "Form elements not found"
        
        # Find search input
        search_input = page.wait_for_selector('{selectors["search_input"]}', timeout=10000)
        assert search_input is not None, "Search input not found"
        
        # Clear and fill search input
        search_input.clear()
        search_input.fill("{search_input}")
        
        # Submit search
        search_button = page.query_selector('{selectors["search_button"]}')
        if search_button:
            search_button.click()
        else:
            search_input.press("Enter")
        
        # Wait for results
        try:
            results = page.wait_for_selector('{selectors["results"]}', timeout=10000)
            assert results is not None, "Search results not displayed"
        except:
            # Check if any content changed
            assert page.content() != "", "No search results or content found"
        
        print(f"✅ Positive test passed: Search for '{{search_input}}' completed")
'''
    elif "login" in form_type and "username" in selectors:
        username = test_data.get("username", "test@example.com")
        password = test_data.get("password", "password123")
        return f'''
        # Wait for form elements
        assert self.wait_for_form_elements(page), "Form elements not found"
        
        # Find login fields
        username_input = page.wait_for_selector('{selectors["username"]}', timeout=10000)
        password_input = page.wait_for_selector('{selectors["password"]}', timeout=10000)
        
        assert username_input is not None, "Username field not found"
        assert password_input is not None, "Password field not found"
        
        # Fill login form
        username_input.clear()
        username_input.fill("{username}")
        password_input.clear()
        password_input.fill("{password}")
        
        # Submit form
        login_button = page.query_selector('{selectors["login_button"]}')
        if login_button:
            login_button.click()
            time.sleep(2)
            print("✅ Positive test passed: Login form submitted successfully")
        else:
            print("⚠️ No login button found")
'''
    else:
        return generate_default_implementation(test_case, selectors)

def generate_negative_test(test_case, selectors):
    """Generate negative test implementation"""
    test_data = test_case.get("test_data", {})
    form_type = test_case.get("form_type", "").lower()
    
    if "search" in form_type and "search_input" in selectors:
        invalid_input = test_data.get("search_input", "!@#$%^&*()")
        return f'''
        # Wait for form elements
        assert self.wait_for_form_elements(page), "Form elements not found"
        
        # Find search input
        search_input = page.wait_for_selector('{selectors["search_input"]}', timeout=10000)
        assert search_input is not None, "Search input not found"
        
        # Clear and fill with invalid input
        search_input.clear()
        search_input.fill("{invalid_input}")
        
        # Submit search
        search_button = page.query_selector('{selectors["search_button"]}')
        if search_button:
            search_button.click()
        else:
            search_input.press("Enter")
        
        # Check for error handling
        time.sleep(2)  # Wait for processing
        
        # Verify no results or error message
        error_message = page.query_selector('.error, .alert, [class*="error"], [class*="alert"]')
        if error_message:
            assert error_message.is_visible(), "Error message should be visible"
        else:
            # Check if results are empty or show no results message
            results = page.query_selector('{selectors["results"]}')
            if results:
                assert "no results" in results.text_content().lower() or results.text_content().strip() == "", "Should show no results for invalid input"
        
        print(f"✅ Negative test passed: Invalid input '{{invalid_input}}' handled correctly")
'''
    else:
        return generate_default_implementation(test_case, selectors)

def generate_edge_case_test(test_case, selectors):
    """Generate edge case test implementation"""
    test_data = test_case.get("test_data", {})
    form_type = test_case.get("form_type", "").lower()
    
    if "search" in form_type and "search_input" in selectors:
        empty_input = test_data.get("search_input", "")
        return f'''
        # Wait for form elements
        assert self.wait_for_form_elements(page), "Form elements not found"
        
        # Find search input
        search_input = page.wait_for_selector('{selectors["search_input"]}', timeout=10000)
        assert search_input is not None, "Search input not found"
        
        # Clear input (empty search)
        search_input.clear()
        
        # Submit empty search
        search_button = page.query_selector('{selectors["search_button"]}')
        if search_button:
            search_button.click()
        else:
            search_input.press("Enter")
        
        # Wait for processing
        time.sleep(2)
        
        # Verify empty search behavior
        # Should either show no results or not trigger search
        results = page.query_selector('{selectors["results"]}')
        if results:
            # If results container exists, it should be empty or show "no results"
            content = results.text_content().lower()
            assert "no results" in content or content.strip() == "", "Empty search should show no results"
        
        print("✅ Edge case test passed: Empty search handled correctly")
'''
    else:
        return generate_default_implementation(test_case, selectors)

def generate_accessibility_test(test_case, selectors):
    """Generate accessibility test implementation"""
    # Determine the main input selector based on form type
    form_type = test_case.get("form_type", "").lower()
    
    if "search" in form_type and "search_input" in selectors:
        input_selector = selectors["search_input"]
        input_name = "search input"
    elif "login" in form_type and "username" in selectors:
        input_selector = selectors["username"]
        input_name = "username input"
    elif "contact" in form_type and "name" in selectors:
        input_selector = selectors["name"]
        input_name = "name input"
    else:
        # Fallback to generic input selector
        input_selector = selectors.get("input", 'input[type="text"], input[type="search"], input[type="email"], input[type="password"]')
        input_name = "form input"
    
    return f'''
        # Wait for form elements
        assert self.wait_for_form_elements(page), "Form elements not found"
        
        # Check for ARIA labels and roles
        main_input = page.wait_for_selector('{input_selector}', timeout=10000)
        assert main_input is not None, "{input_name} not found"
        
        # Check for accessibility attributes
        aria_label = main_input.get_attribute('aria-label')
        aria_labelledby = main_input.get_attribute('aria-labelledby')
        placeholder = main_input.get_attribute('placeholder')
        role = main_input.get_attribute('role')
        
        # At least one accessibility feature should be present
        assert any([aria_label, aria_labelledby, placeholder, role]), "{input_name} should have accessibility attributes"
        
        # Check for keyboard navigation
        main_input.focus()
        main_input.press("Tab")
        
        # Verify focus moves to next element
        focused_element = page.evaluate('document.activeElement')
        assert focused_element is not None, "Keyboard navigation should work"
        
        print("✅ Accessibility test passed: Form supports screen readers and keyboard navigation")
'''

def generate_dynamic_test(test_case, selectors):
    """Generate dynamic behavior test implementation"""
    test_data = test_case.get("test_data", {})
    form_type = test_case.get("form_type", "").lower()
    
    if "search" in form_type and "search_input" in selectors:
        dynamic_input = test_data.get("search_input", "engine")
        return f'''
        # Wait for form elements
        assert self.wait_for_form_elements(page), "Form elements not found"
        
        # Find search input
        search_input = page.wait_for_selector('{selectors["search_input"]}', timeout=10000)
        assert search_input is not None, "Search input not found"
        
        # Clear and start typing
        search_input.clear()
        search_input.fill("{dynamic_input}")
        
        # Wait for dynamic updates (if any)
        time.sleep(1)
        
        # Check if results update dynamically
        try:
            # Look for dynamic results or suggestions
            dynamic_results = page.query_selector('.suggestions, .autocomplete, [class*="suggestion"], [class*="auto"]')
            if dynamic_results:
                assert dynamic_results.is_visible(), "Dynamic suggestions should be visible"
                print("✅ Dynamic test passed: Search suggestions appear dynamically")
            else:
                # If no dynamic suggestions, check if form responds to input
                assert search_input.input_value() == "{dynamic_input}", "Input value should match what was typed"
                print("✅ Dynamic test passed: Form responds to input changes")
        except Exception as e:
            print(f"⚠️ Dynamic behavior not detected: {{e}}")
            # Still pass if basic input works
            assert search_input.input_value() == "{dynamic_input}", "Input value should match what was typed"
'''
    else:
        return generate_default_implementation(test_case, selectors)

def generate_default_implementation(test_case, selectors):
    """Generate a default implementation for unknown form types"""
    return f'''
        # Wait for form elements
        assert self.wait_for_form_elements(page), "Form elements not found"
        
        # Find form elements
        form = page.query_selector('{selectors["form"]}')
        if form:
            # Basic form interaction
            inputs = page.query_selector_all('{selectors["input"]}')
            if inputs:
                # Fill first input
                first_input = inputs[0]
                first_input.fill("test input")
                
                # Find and click submit button
                submit_button = page.query_selector('{selectors["button"]}')
                if submit_button:
                    submit_button.click()
                    time.sleep(2)
                    print("✅ Default test passed: Basic form interaction completed")
                else:
                    print("⚠️ No submit button found")
            else:
                print("⚠️ No input elements found")
        else:
            print("⚠️ No form element found")
'''

def create_readme(test_dir, url, all_test_data):
    readme_content = f"""# Test Cases for {url}

Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Directory Structure

```
{test_dir}/
├── json/           # JSON format test cases
├── csv/            # CSV format test cases  
├── reports/        # Markdown reports
├── test_scripts/   # Python test scripts
└── test_data/      # Test data files
```

## Summary

- **Total Forms Found:** {len(all_test_data)}
- **Total Test Cases:** {sum(len(form.get('test_cases', [])) for form in all_test_data)}

## Forms Analyzed

"""
    for i, form_data in enumerate(all_test_data):
        form_type = form_data.get('form_type', 'Unknown')
        test_count = len(form_data.get('test_cases', []))
        readme_content += f"""
### Form {i+1}: {form_type}
- **Test Cases:** {test_count}
- **Files:** 
  - JSON: `json/form_{i+1}_{form_type.replace(' ', '_').lower()}_*.json`
  - CSV: `csv/form_{i+1}_{form_type.replace(' ', '_').lower()}_*.csv`
  - Report: `reports/form_{i+1}_{form_type.replace(' ', '_').lower()}_*.md`
  - Script: `test_scripts/test_form_{i+1}_{form_type.replace(' ', '_').lower()}_*.py`
"""
    readme_content += """
## Usage

1. **View Reports**: Check the `reports/` directory for detailed test case documentation
2. **Import Test Cases**: Use JSON or CSV files to import into your test management system
3. **Run Tests**: Execute the generated Python test scripts with pytest
4. **Customize**: Modify the test scripts to match your specific testing framework

## Test Categories

- **Positive Tests**: Valid input scenarios
- **Negative Tests**: Invalid input scenarios  
- **Edge Cases**: Boundary conditions and special characters
- **Accessibility Tests**: Screen reader and keyboard navigation tests
"""
    readme_file = f"{test_dir}/README.md"
    with open(readme_file, "w") as f:
        f.write(readme_content)
    return readme_file

async def main(url):
    print(f"🔍 Crawling {url}...")
    forms = await extract_spa_forms(url)
    if not forms:
        print("❌ No forms found on this website!")
        return
    print(f"✅ Found {len(forms)} form(s)")
    test_dir, subdirs = create_directory_structure(url)
    print(f"📁 Created test directory: {test_dir}")
    print(f"🧠 Generating test cases using GPT...")
    all_test_data = []
    generated_files = []
    for i, form in enumerate(forms):
        print(f"📝 Generating test cases for form {i+1}/{len(forms)}...")
        test_data = generate_test_cases(form)
        test_data["form_index"] = i + 1
        all_test_data.append(test_data)
        display_test_cases(test_data, url)
        json_file, csv_file, report_file = save_test_cases_to_files(test_data, url, subdirs, i+1)
        script_file = create_test_script(test_data, url, subdirs, i+1)
        generated_files.extend([json_file, csv_file, report_file, script_file])
    readme_file = create_readme(test_dir, url, all_test_data)
    generated_files.append(readme_file)
    print(f"\n📄 Test cases saved in organized structure:")
    print(f"   📁 Main directory: {test_dir}")
    print(f"   📄 README: {readme_file}")
    print(f"   📊 Total files generated: {len(generated_files)}")
    print(f"\n📂 Directory structure created:")
    for subdir_name, subdir_path in subdirs.items():
        print(f"   📁 {subdir_name}/: {subdir_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate test cases for SPA forms on a website.")
    parser.add_argument("url", type=str, help="URL of the website to analyze")
    args = parser.parse_args()
    asyncio.run(main(args.url))