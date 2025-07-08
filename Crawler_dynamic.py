import asyncio
import os
from openai import OpenAI
import pandas as pd
from rich.console import Console
from rich.table import Table
from playwright.async_api import async_playwright
import argparse
import json
from datetime import datetime
import re

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
console = Console()

def create_directory_structure(base_url):
    """Create organized directory structure for test cases"""
    # Clean URL for directory name
    domain = re.sub(r'https?://', '', base_url)
    domain = re.sub(r'[^\w\-_.]', '_', domain)
    
    # Create main test directory
    test_dir = f"test_cases/{domain}"
    os.makedirs(test_dir, exist_ok=True)
    
    # Create subdirectories
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

async def extract_forms_from_url(url):
    async with async_playwright() as p:
        # Launch browser with JavaScript enabled
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        # Set viewport and user agent for better compatibility
        await page.set_viewport_size({"width": 1920, "height": 1080})
        await page.set_extra_http_headers({
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        })
        
        console.print(f"🌐 Navigating to {url}...")
        await page.goto(url, timeout=60000, wait_until="networkidle")
        
        # Wait for page to fully load
        console.print("⏳ Waiting for page to fully load...")
        await page.wait_for_load_state("networkidle")
        
        # Additional wait for dynamic content
        await asyncio.sleep(3)
        
        # Try to find forms with different strategies
        forms = []
        
        # Strategy 1: Standard form elements
        console.print("🔍 Looking for standard form elements...")
        standard_forms = await page.query_selector_all("form")
        forms.extend(standard_forms)
        
        # Strategy 2: Look for form-like containers (divs with form-like attributes)
        console.print("🔍 Looking for dynamic form containers...")
        dynamic_forms = await page.query_selector_all("div[role='form'], div[class*='form'], div[id*='form']")
        forms.extend(dynamic_forms)
        
        # Strategy 3: Look for any container with input elements
        console.print("🔍 Looking for input containers...")
        input_containers = await page.query_selector_all("div:has(input), section:has(input), main:has(input)")
        forms.extend(input_containers)
        
        # Strategy 4: Look for search forms specifically
        console.print("🔍 Looking for search forms...")
        search_forms = await page.query_selector_all("form[action*='search'], form[class*='search'], div[class*='search']:has(input)")
        forms.extend(search_forms)
        
        # Remove duplicates
        unique_forms = []
        seen_selectors = set()
        
        for form in forms:
            try:
                selector = await form.evaluate("el => el.outerHTML")
                if selector not in seen_selectors:
                    seen_selectors.add(selector)
                    unique_forms.append(form)
            except:
                continue
        
        console.print(f"✅ Found {len(unique_forms)} potential form elements")
        
        data = []
        
        for i, form in enumerate(unique_forms):
            console.print(f"📝 Analyzing form {i+1}/{len(unique_forms)}...")
            
            try:
                # Get all input elements within this form
                inputs = await form.query_selector_all("input, textarea, select")
                buttons = await form.query_selector_all("button, input[type=submit], input[type=button]")
                
                # Also look for clickable elements that might act as buttons
                clickable_elements = await form.query_selector_all("a[role='button'], div[role='button'], span[role='button']")
                buttons.extend(clickable_elements)

                input_fields = []
                for inp in inputs:
                    try:
                        name = await inp.get_attribute("name")
                        input_type = await inp.get_attribute("type")
                        placeholder = await inp.get_attribute("placeholder")
                        required = await inp.get_attribute("required")
                        max_length = await inp.get_attribute("maxlength")
                        pattern = await inp.get_attribute("pattern")
                        id_attr = await inp.get_attribute("id")
                        class_attr = await inp.get_attribute("class")
                        
                        input_fields.append({
                            "name": name,
                            "type": input_type,
                            "placeholder": placeholder,
                            "required": required is not None,
                            "max_length": max_length,
                            "pattern": pattern,
                            "id": id_attr,
                            "class": class_attr
                        })
                    except Exception as e:
                        console.print(f"[yellow]Warning: Could not extract input field: {e}[/yellow]")
                        continue

                button_info = []
                for btn in buttons:
                    try:
                        txt = await btn.inner_text()
                        btn_name = await btn.get_attribute("name")
                        btn_id = await btn.get_attribute("id")
                        btn_type = await btn.get_attribute("type")
                        btn_value = await btn.get_attribute("value")
                        btn_class = await btn.get_attribute("class")
                        
                        if txt.strip():
                            button_info.append(txt.strip())
                        elif btn_value:
                            button_info.append(f"{btn_value} (value)")
                        elif btn_name:
                            button_info.append(f"{btn_name} (name)")
                        elif btn_id:
                            button_info.append(f"{btn_id} (id)")
                        elif btn_class and "btn" in btn_class:
                            button_info.append(f"Button ({btn_class})")
                        else:
                            button_info.append(f"Button ({btn_type or 'unknown'})")
                    except Exception as e:
                        console.print(f"[yellow]Warning: Could not extract button: {e}[/yellow]")
                        continue

                # Get form HTML for analysis
                form_html = await form.inner_html()
                
                # Get form attributes
                form_action = await form.get_attribute("action")
                form_method = await form.get_attribute("method")
                form_id = await form.get_attribute("id")
                form_class = await form.get_attribute("class")
                
                data.append({
                    "url": url,
                    "form_index": i + 1,
                    "inputs": input_fields,
                    "buttons": button_info,
                    "html_snippet": form_html[:500],
                    "form_action": form_action,
                    "form_method": form_method,
                    "form_id": form_id,
                    "form_class": form_class
                })
                
            except Exception as e:
                console.print(f"[red]Error analyzing form {i+1}: {e}[/red]")
                continue

        await browser.close()
        return data

def generate_test_cases(form_data):
    prompt = f"""Based on the following form data, generate comprehensive functional test cases in JSON format. 
    Include test cases for valid inputs, invalid inputs, edge cases, and accessibility testing.

    Form Data:
    URL: {form_data['url']}
    Form Index: {form_data.get('form_index', 'N/A')}
    Form Action: {form_data.get('form_action', 'N/A')}
    Form Method: {form_data.get('form_method', 'N/A')}
    Form ID: {form_data.get('form_id', 'N/A')}
    Form Class: {form_data.get('form_class', 'N/A')}
    Inputs: {form_data['inputs']}
    Buttons: {form_data['buttons']}
    HTML Snippet: {form_data['html_snippet'][:300]}

    Generate test cases in this JSON structure:
    {{
        "form_type": "description of form type",
        "test_cases": [
            {{
                "test_id": "TC001",
                "test_name": "Descriptive test name",
                "test_type": "positive|negative|edge_case|accessibility",
                "priority": "high|medium|low",
                "preconditions": "What needs to be set up",
                "test_steps": ["Step 1", "Step 2", "Step 3"],
                "test_data": {{"field_name": "value"}},
                "expected_result": "What should happen",
                "validation_points": ["Point 1", "Point 2"]
            }}
        ]
    }}

    Focus on:
    1. Input validation (required fields, data types, formats)
    2. Button functionality
    3. Form submission behavior
    4. Error handling
    5. Accessibility (screen readers, keyboard navigation)
    6. Edge cases (empty inputs, special characters, max lengths)
    7. Dynamic form behavior (if applicable)
    
    Return ONLY valid JSON, no additional text.
    """
    
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=0.3,
        max_tokens=2000
    )
    
    try:
        # Try to extract JSON from response
        content = response.choices[0].message.content.strip()
        # Remove any markdown formatting if present
        if content.startswith("```json"):
            content = content[7:]
        if content.endswith("```"):
            content = content[:-3]
        
        return json.loads(content.strip())
    except json.JSONDecodeError as e:
        console.print(f"[red]JSON parsing failed: {e}[/red]")
        console.print(f"[yellow]Raw response: {content[:200]}...[/yellow]")
        # Fallback if JSON parsing fails
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
                "validation_points": ["No errors displayed", "Success message shown"]
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
    
    # Save as JSON
    json_file = f"{subdirs['json']}/form_{form_index}_{form_type}_{timestamp}.json"
    with open(json_file, "w") as f:
        json.dump(test_data, f, indent=2)
    
    # Save as CSV
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
            "validation_points": " | ".join(test_case.get("validation_points", []))
        })
    
    df = pd.DataFrame(test_cases_list)
    csv_file = f"{subdirs['csv']}/form_{form_index}_{form_type}_{timestamp}.csv"
    df.to_csv(csv_file, index=False)
    
    # Generate test report
    report = f"""
# Test Case Report for Form {form_index} - {url}

**Generated on:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Form Type:** {test_data.get('form_type', 'Unknown')}
**Total Test Cases:** {len(test_data.get('test_cases', []))}

## Form Details

- **Form Action:** {test_data.get('form_action', 'N/A')}
- **Form Method:** {test_data.get('form_method', 'N/A')}
- **Form ID:** {test_data.get('form_id', 'N/A')}
- **Form Class:** {test_data.get('form_class', 'N/A')}

## Test Case Summary

"""
    
    # Group by test type
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
            report += f"- Expected: {case.get('expected_result')}\n\n"
    
    report_file = f"{subdirs['reports']}/form_{form_index}_{form_type}_{timestamp}.md"
    with open(report_file, "w") as f:
        f.write(report)
    
    return json_file, csv_file, report_file

def create_test_script(test_data, url, subdirs, form_index):
    """Generate a basic test script template"""
    form_type = test_data.get('form_type', 'unknown').replace(' ', '_').lower()
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    script_content = f'''"""
Test Script for Form {form_index} - {url}
Form Type: {test_data.get('form_type', 'Unknown')}
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""

import pytest
from playwright.sync_api import sync_playwright
import time

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
        page.set_viewport_size({{"width": 1920, "height": 1080}})
        page.goto("{url}")
        # Wait for page to load completely
        page.wait_for_load_state("networkidle")
        time.sleep(3)  # Additional wait for dynamic content
        yield page
        page.close()

'''
    
    # Add test methods for each test case
    for test_case in test_data.get("test_cases", []):
        test_id = test_case.get("test_id", "TC001")
        test_name = test_case.get("test_name", "Basic Test")
        test_type = test_case.get("test_type", "positive")
        priority = test_case.get("priority", "medium")
        
        script_content += f'''
    def test_{test_id.lower()}_{test_type}_{priority}(self, page):
        """
        {test_name}
        Type: {test_type}
        Priority: {priority}
        """
        # TODO: Implement test steps
        # {chr(10).join(f"# {step}" for step in test_case.get('test_steps', []))}
        
        # Expected: {test_case.get('expected_result', 'N/A')}
        pass
'''
    
    script_file = f"{subdirs['test_scripts']}/test_form_{form_index}_{form_type}_{timestamp}.py"
    with open(script_file, "w") as f:
        f.write(script_content)
    
    return script_file

def create_readme(test_dir, url, all_test_data):
    """Create a README file for the test directory"""
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
- **Form Action:** {form_data.get('form_action', 'N/A')}
- **Form Method:** {form_data.get('form_method', 'N/A')}
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

## Dynamic Content Handling

This test suite is designed to handle JavaScript-heavy websites and dynamic form loading.
The generated test scripts include:
- Proper page load waiting
- Dynamic content detection
- JavaScript execution support
"""
    
    readme_file = f"{test_dir}/README.md"
    with open(readme_file, "w") as f:
        f.write(readme_content)
    
    return readme_file

async def main(url):
    print(f"🔍 Crawling {url} with enhanced JavaScript support...")
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
    
    # Create directory structure
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
        
        # Display test cases for this form
        display_test_cases(test_data, url)
        
        # Save files
        json_file, csv_file, report_file = save_test_cases_to_files(test_data, url, subdirs, i+1)
        script_file = create_test_script(test_data, url, subdirs, i+1)
        
        generated_files.extend([json_file, csv_file, report_file, script_file])
    
    # Create README
    readme_file = create_readme(test_dir, url, all_test_data)
    generated_files.append(readme_file)
    
    print(f"\n📄 Test cases saved in organized structure:")
    print(f"   📁 Main directory: {test_dir}")
    print(f"   📄 README: {readme_file}")
    print(f"   📊 Total files generated: {len(generated_files)}")
    
    # Show directory structure
    print(f"\n📂 Directory structure created:")
    for subdir_name, subdir_path in subdirs.items():
        print(f"   📁 {subdir_name}/: {subdir_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate test cases for forms on JavaScript-heavy websites.")
    parser.add_argument("url", type=str, help="URL of the website to analyze")
    args = parser.parse_args()
    asyncio.run(main(args.url)) 