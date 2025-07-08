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
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        # Set longer timeout and add debugging
        print(f"🔍 Navigating to: {url}")
        print("⏳ This may take a moment for complex sites...")
        
        try:
            # Increase timeout for complex sites
            await page.goto(url, timeout=120000)  # 2 minutes timeout
            
            print("✅ Page loaded successfully")
            
            # Wait for dynamic content to load
            print("⏳ Waiting for dynamic content...")
            await page.wait_for_load_state("networkidle", timeout=30000)
            await page.wait_for_timeout(5000)  # Additional wait for JavaScript execution
            
            print("✅ Dynamic content loaded")
            
        except Exception as e:
            print(f"❌ Error loading page: {e}")
            print("🔄 Attempting to continue with current page state...")
        
        # Check if page loaded at all
        try:
            page_title = await page.title()
            print(f"📄 Page title: {page_title}")
        except Exception as e:
            print(f"❌ Could not get page title: {e}")
            await browser.close()
            return []

        forms = await page.query_selector_all("form")
        print(f"✅ Found {len(forms)} form(s)")
        
        data = []

        for form in forms:
            print(f"📝 Processing form {len(data) + 1}...")
            
            # Enhanced input extraction
            inputs = await form.query_selector_all("input, textarea, select")
            print(f"  - Found {len(inputs)} input elements")
            
            # Submit triggers (buttons, links, custom elements)
            submit_triggers = await form.query_selector_all("button, input[type=submit], input[type=button], [role='button'], .btn, .button")
            print(f"  - Found {len(submit_triggers)} submit triggers")
            
            # Validation elements
            validation_elements = await form.query_selector_all("[data-validation], [data-validate], .validation, .error, .invalid, [aria-invalid]")
            print(f"  - Found {len(validation_elements)} validation elements")
            
            # Custom widgets (date pickers, sliders, file uploads, etc.)
            custom_widgets = await form.query_selector_all("input[type='date'], input[type='file'], input[type='range'], input[type='color'], .datepicker, .slider, .upload, .widget")
            print(f"  - Found {len(custom_widgets)} custom widgets")
            
            # Dynamic elements (elements that change based on user interaction)
            dynamic_elements = await form.query_selector_all("[data-dynamic], [data-toggle], .dynamic, .collapsible, .expandable, [aria-expanded]")
            print(f"  - Found {len(dynamic_elements)} dynamic elements")

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
                    value = await inp.get_attribute("value")
                    disabled = await inp.get_attribute("disabled")
                    readonly = await inp.get_attribute("readonly")
                    
                    # Get validation attributes
                    aria_invalid = await inp.get_attribute("aria-invalid")
                    data_validation = await inp.get_attribute("data-validation")
                    data_validate = await inp.get_attribute("data-validate")
                    
                    # Get custom attributes
                    data_attrs = {}
                    for attr in ["data-type", "data-format", "data-mask", "data-min", "data-max", "data-step"]:
                        data_attrs[attr] = await inp.get_attribute(attr)
                    
                    input_fields.append({
                        "name": name,
                        "type": input_type,
                        "placeholder": placeholder,
                        "required": required is not None,
                        "max_length": max_length,
                        "pattern": pattern,
                        "id": id_attr,
                        "class": class_attr,
                        "value": value,
                        "disabled": disabled is not None,
                        "readonly": readonly is not None,
                        "validation": {
                            "aria_invalid": aria_invalid,
                            "data_validation": data_validation,
                            "data_validate": data_validate
                        },
                        "custom_attributes": data_attrs
                    })
                except Exception as e:
                    print(f"❌ Error processing input: {e}")
                    continue

            # Enhanced submit triggers
            submit_info = []
            for trigger in submit_triggers:
                try:
                    txt = await trigger.inner_text()
                    trigger_name = await trigger.get_attribute("name")
                    trigger_id = await trigger.get_attribute("id")
                    trigger_type = await trigger.get_attribute("type")
                    trigger_value = await trigger.get_attribute("value")
                    trigger_class = await trigger.get_attribute("class")
                    trigger_role = await trigger.get_attribute("role")
                    trigger_disabled = await trigger.get_attribute("disabled")
                    
                    # Get custom attributes
                    data_attrs = {}
                    for attr in ["data-action", "data-submit", "data-confirm", "data-loading"]:
                        data_attrs[attr] = await trigger.get_attribute(attr)
                    
                    submit_info.append({
                        "text": txt.strip() if txt.strip() else None,
                        "name": trigger_name,
                        "id": trigger_id,
                        "type": trigger_type,
                        "value": trigger_value,
                        "class": trigger_class,
                        "role": trigger_role,
                        "disabled": trigger_disabled is not None,
                        "custom_attributes": data_attrs
                    })
                except Exception as e:
                    print(f"❌ Error processing submit trigger: {e}")
                    continue

            # Validation elements
            validation_info = []
            for val_elem in validation_elements:
                try:
                    val_text = await val_elem.inner_text()
                    val_id = await val_elem.get_attribute("id")
                    val_class = await val_elem.get_attribute("class")
                    val_role = await val_elem.get_attribute("role")
                    val_aria_live = await val_elem.get_attribute("aria-live")
                    
                    validation_info.append({
                        "text": val_text.strip() if val_text.strip() else None,
                        "id": val_id,
                        "class": val_class,
                        "role": val_role,
                        "aria_live": val_aria_live
                    })
                except Exception as e:
                    print(f"❌ Error processing validation element: {e}")
                    continue

            # Custom widgets
            widget_info = []
            for widget in custom_widgets:
                try:
                    widget_type = await widget.get_attribute("type")
                    widget_id = await widget.get_attribute("id")
                    widget_class = await widget.get_attribute("class")
                    widget_name = await widget.get_attribute("name")
                    widget_value = await widget.get_attribute("value")
                    
                    # Get widget-specific attributes
                    widget_attrs = {}
                    if widget_type == "file":
                        widget_attrs["accept"] = await widget.get_attribute("accept")
                        widget_attrs["multiple"] = await widget.get_attribute("multiple")
                    elif widget_type == "range":
                        widget_attrs["min"] = await widget.get_attribute("min")
                        widget_attrs["max"] = await widget.get_attribute("max")
                        widget_attrs["step"] = await widget.get_attribute("step")
                    elif widget_type == "date":
                        widget_attrs["min"] = await widget.get_attribute("min")
                        widget_attrs["max"] = await widget.get_attribute("max")
                    
                    widget_info.append({
                        "type": widget_type,
                        "id": widget_id,
                        "class": widget_class,
                        "name": widget_name,
                        "value": widget_value,
                        "attributes": widget_attrs
                    })
                except Exception as e:
                    print(f"❌ Error processing widget: {e}")
                    continue

            # Dynamic elements
            dynamic_info = []
            for dyn_elem in dynamic_elements:
                try:
                    dyn_text = await dyn_elem.inner_text()
                    dyn_id = await dyn_elem.get_attribute("id")
                    dyn_class = await dyn_elem.get_attribute("class")
                    dyn_role = await dyn_elem.get_attribute("role")
                    dyn_aria_expanded = await dyn_elem.get_attribute("aria-expanded")
                    dyn_data_toggle = await dyn_elem.get_attribute("data-toggle")
                    dyn_data_target = await dyn_elem.get_attribute("data-target")
                    
                    dynamic_info.append({
                        "text": dyn_text.strip() if dyn_text.strip() else None,
                        "id": dyn_id,
                        "class": dyn_class,
                        "role": dyn_role,
                        "aria_expanded": dyn_aria_expanded,
                        "data_toggle": dyn_data_toggle,
                        "data_target": dyn_data_target
                    })
                except Exception as e:
                    print(f"❌ Error processing dynamic element: {e}")
                    continue

            # Form metadata
            try:
                form_action = await form.get_attribute("action")
                form_method = await form.get_attribute("method")
                form_id = await form.get_attribute("id")
                form_class = await form.get_attribute("class")
                form_enctype = await form.get_attribute("enctype")
                form_novalidate = await form.get_attribute("novalidate")

                form_html = await form.inner_html()
                data.append({
                    "url": url,
                    "form_metadata": {
                        "action": form_action,
                        "method": form_method,
                        "id": form_id,
                        "class": form_class,
                        "enctype": form_enctype,
                        "novalidate": form_novalidate is not None
                    },
                    "inputs": input_fields,
                    "submit_triggers": submit_info,
                    "validation_elements": validation_info,
                    "custom_widgets": widget_info,
                    "dynamic_elements": dynamic_info,
                    "html_snippet": form_html[:500]
                })
                print(f"✅ Form {len(data)} processed successfully")
            except Exception as e:
                print(f"❌ Error processing form metadata: {e}")

        await browser.close()
        return data

def generate_test_cases(form_data):
    prompt = f"""Based on the following comprehensive form data, generate comprehensive functional test cases in JSON format. 
    Include test cases for valid inputs, invalid inputs, edge cases, accessibility testing, and dynamic behavior.

    Form Data:
    URL: {form_data['url']}
    Form Metadata: {form_data.get('form_metadata', {})}
    Inputs: {form_data['inputs']}
    Submit Triggers: {form_data.get('submit_triggers', [])}
    Validation Elements: {form_data.get('validation_elements', [])}
    Custom Widgets: {form_data.get('custom_widgets', [])}
    Dynamic Elements: {form_data.get('dynamic_elements', [])}
    HTML Snippet: {form_data['html_snippet'][:300]}

    Generate test cases in this JSON structure:
    {{
        "form_type": "description of form type",
        "test_cases": [
            {{
                "test_id": "TC001",
                "test_name": "Descriptive test name",
                "test_type": "positive|negative|edge_case|accessibility|dynamic|validation",
                "priority": "high|medium|low",
                "preconditions": "What needs to be set up",
                "test_steps": ["Step 1", "Step 2", "Step 3"],
                "test_data": {{"field_name": "value"}},
                "expected_result": "What should happen",
                "validation_points": ["Point 1", "Point 2"],
                "dynamic_behavior": "Description of dynamic changes",
                "widget_interaction": "How custom widgets should behave"
            }}
        ]
    }}

    Focus on:
    1. Input validation (required fields, data types, formats, patterns)
    2. Submit trigger functionality (buttons, custom triggers, loading states)
    3. Validation elements (error messages, aria-live regions, validation states)
    4. Custom widgets (date pickers, file uploads, sliders, color pickers)
    5. Dynamic elements (collapsible sections, expandable content, toggles)
    6. Form submission behavior and error handling
    7. Accessibility (screen readers, keyboard navigation, ARIA attributes)
    8. Edge cases (empty inputs, special characters, max lengths, disabled states)
    9. Cross-browser compatibility for custom widgets
    10. Mobile responsiveness for dynamic elements
    
    Consider these specific scenarios:
    - File upload validation (file types, sizes, multiple files)
    - Date/time picker interactions and validation
    - Range slider interactions and value changes
    - Color picker functionality and validation
    - Dynamic form sections that show/hide based on user input
    - Real-time validation feedback
    - Loading states during form submission
    - Error message display and accessibility
    
    Return ONLY valid JSON, no additional text.
    """
    
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=0.3,
        max_tokens=2500
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
            "validation_points": " | ".join(test_case.get("validation_points", [])),
            "dynamic_behavior": test_case.get("dynamic_behavior", ""),
            "widget_interaction": test_case.get("widget_interaction", "")
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
    forms = await extract_forms_from_url(url)
    
    if not forms:
        print("❌ No forms found on this website!")
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
    parser = argparse.ArgumentParser(description="Generate test cases for forms on a website.")
    parser.add_argument("url", type=str, help="URL of the website to analyze")
    args = parser.parse_args()
    asyncio.run(main(args.url)) 