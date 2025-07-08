#!/usr/bin/env python3
"""
Enhanced Form Extractor Demo
Demonstrates the enhanced form extraction capabilities including:
- Inputs with validation attributes
- Submit triggers (buttons, custom elements)
- Validation elements
- Custom widgets (date pickers, file uploads, sliders)
- Dynamic elements (collapsible sections, toggles)
"""

import asyncio
import json
from playwright.async_api import async_playwright
from rich.console import Console
from rich.table import Table

console = Console()

async def extract_enhanced_forms(url):
    """Enhanced form extraction with comprehensive element detection"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        # Set longer timeout and add debugging
        console.print(f"[yellow]Navigating to: {url}[/yellow]")
        console.print("[yellow]This may take a moment for complex sites...[/yellow]")
        
        try:
            # Increase timeout for complex sites
            await page.goto(url, timeout=120000)  # 2 minutes timeout
            
            console.print("[green]Page loaded successfully[/green]")
            
            # Wait for dynamic content to load
            console.print("[yellow]Waiting for dynamic content...[/yellow]")
            await page.wait_for_load_state("networkidle", timeout=30000)
            await page.wait_for_timeout(5000)  # Additional wait for JavaScript execution
            
            console.print("[green]Dynamic content loaded[/green]")
            
        except Exception as e:
            console.print(f"[red]Error loading page: {e}[/red]")
            console.print("[yellow]Attempting to continue with current page state...[/yellow]")
        
        # Check if page loaded at all
        try:
            page_title = await page.title()
            console.print(f"[green]Page title: {page_title}[/green]")
        except Exception as e:
            console.print(f"[red]Could not get page title: {e}[/red]")
            await browser.close()
            return []

        forms = await page.query_selector_all("form")
        console.print(f"[green]Found {len(forms)} form(s)[/green]")
        
        data = []

        for form in forms:
            console.print(f"[yellow]Processing form {len(data) + 1}...[/yellow]")
            
            # Enhanced input extraction
            inputs = await form.query_selector_all("input, textarea, select")
            console.print(f"  - Found {len(inputs)} input elements")
            
            # Submit triggers (buttons, links, custom elements)
            submit_triggers = await form.query_selector_all("button, input[type=submit], input[type=button], [role='button'], .btn, .button")
            console.print(f"  - Found {len(submit_triggers)} submit triggers")
            
            # Validation elements
            validation_elements = await form.query_selector_all("[data-validation], [data-validate], .validation, .error, .invalid, [aria-invalid]")
            console.print(f"  - Found {len(validation_elements)} validation elements")
            
            # Custom widgets (date pickers, sliders, file uploads, etc.)
            custom_widgets = await form.query_selector_all("input[type='date'], input[type='file'], input[type='range'], input[type='color'], .datepicker, .slider, .upload, .widget")
            console.print(f"  - Found {len(custom_widgets)} custom widgets")
            
            # Dynamic elements (elements that change based on user interaction)
            dynamic_elements = await form.query_selector_all("[data-dynamic], [data-toggle], .dynamic, .collapsible, .expandable, [aria-expanded]")
            console.print(f"  - Found {len(dynamic_elements)} dynamic elements")

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
                    console.print(f"[red]Error processing input: {e}[/red]")
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
                    console.print(f"[red]Error processing submit trigger: {e}[/red]")
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
                    console.print(f"[red]Error processing validation element: {e}[/red]")
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
                    console.print(f"[red]Error processing widget: {e}[/red]")
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
                    console.print(f"[red]Error processing dynamic element: {e}[/red]")
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
                console.print(f"[green]Form {len(data)} processed successfully[/green]")
            except Exception as e:
                console.print(f"[red]Error processing form metadata: {e}[/red]")

        await browser.close()
        return data

def display_enhanced_form_data(form_data):
    """Display enhanced form data in a comprehensive table"""
    
    for i, form in enumerate(form_data):
        console.print(f"\n[bold blue]Form {i+1}[/bold blue]")
        
        # Form metadata
        metadata = form.get('form_metadata', {})
        console.print(f"[yellow]Form Metadata:[/yellow]")
        console.print(f"  Action: {metadata.get('action', 'N/A')}")
        console.print(f"  Method: {metadata.get('method', 'N/A')}")
        console.print(f"  ID: {metadata.get('id', 'N/A')}")
        console.print(f"  Class: {metadata.get('class', 'N/A')}")
        
        # Inputs
        inputs = form.get('inputs', [])
        if inputs:
            console.print(f"\n[yellow]Inputs ({len(inputs)}):[/yellow]")
            input_table = Table(show_header=True, header_style="bold magenta")
            input_table.add_column("Name")
            input_table.add_column("Type")
            input_table.add_column("Required")
            input_table.add_column("Validation")
            input_table.add_column("Custom Attrs")
            
            for inp in inputs:
                validation_info = inp.get('validation', {})
                validation_str = f"aria-invalid: {validation_info.get('aria_invalid')}, data-validation: {validation_info.get('data_validation')}"
                custom_attrs = inp.get('custom_attributes', {})
                custom_str = ", ".join([f"{k}: {v}" for k, v in custom_attrs.items() if v])
                
                input_table.add_row(
                    inp.get('name', 'N/A'),
                    inp.get('type', 'N/A'),
                    "Yes" if inp.get('required') else "No",
                    validation_str[:50] + "..." if len(validation_str) > 50 else validation_str,
                    custom_str[:50] + "..." if len(custom_str) > 50 else custom_str
                )
            console.print(input_table)
        
        # Submit triggers
        submit_triggers = form.get('submit_triggers', [])
        if submit_triggers:
            console.print(f"\n[yellow]Submit Triggers ({len(submit_triggers)}):[/yellow]")
            submit_table = Table(show_header=True, header_style="bold magenta")
            submit_table.add_column("Text")
            submit_table.add_column("Type")
            submit_table.add_column("ID")
            submit_table.add_column("Disabled")
            submit_table.add_column("Custom Attrs")
            
            for trigger in submit_triggers:
                custom_attrs = trigger.get('custom_attributes', {})
                custom_str = ", ".join([f"{k}: {v}" for k, v in custom_attrs.items() if v])
                
                submit_table.add_row(
                    trigger.get('text', 'N/A'),
                    trigger.get('type', 'N/A'),
                    trigger.get('id', 'N/A'),
                    "Yes" if trigger.get('disabled') else "No",
                    custom_str[:50] + "..." if len(custom_str) > 50 else custom_str
                )
            console.print(submit_table)
        
        # Custom widgets
        widgets = form.get('custom_widgets', [])
        if widgets:
            console.print(f"\n[yellow]Custom Widgets ({len(widgets)}):[/yellow]")
            widget_table = Table(show_header=True, header_style="bold magenta")
            widget_table.add_column("Type")
            widget_table.add_column("Name")
            widget_table.add_column("ID")
            widget_table.add_column("Attributes")
            
            for widget in widgets:
                attrs = widget.get('attributes', {})
                attrs_str = ", ".join([f"{k}: {v}" for k, v in attrs.items() if v])
                
                widget_table.add_row(
                    widget.get('type', 'N/A'),
                    widget.get('name', 'N/A'),
                    widget.get('id', 'N/A'),
                    attrs_str[:50] + "..." if len(attrs_str) > 50 else attrs_str
                )
            console.print(widget_table)
        
        # Dynamic elements
        dynamic_elements = form.get('dynamic_elements', [])
        if dynamic_elements:
            console.print(f"\n[yellow]Dynamic Elements ({len(dynamic_elements)}):[/yellow]")
            dynamic_table = Table(show_header=True, header_style="bold magenta")
            dynamic_table.add_column("Text")
            dynamic_table.add_column("ID")
            dynamic_table.add_column("Role")
            dynamic_table.add_column("Data Attributes")
            
            for dyn in dynamic_elements:
                data_attrs = []
                if dyn.get('data_toggle'):
                    data_attrs.append(f"data-toggle: {dyn.get('data_toggle')}")
                if dyn.get('data_target'):
                    data_attrs.append(f"data-target: {dyn.get('data_target')}")
                data_str = ", ".join(data_attrs)
                
                dynamic_table.add_row(
                    dyn.get('text', 'N/A'),
                    dyn.get('id', 'N/A'),
                    dyn.get('role', 'N/A'),
                    data_str[:50] + "..." if len(data_str) > 50 else data_str
                )
            console.print(dynamic_table)
        
        # Validation elements
        validation_elements = form.get('validation_elements', [])
        if validation_elements:
            console.print(f"\n[yellow]Validation Elements ({len(validation_elements)}):[/yellow]")
            validation_table = Table(show_header=True, header_style="bold magenta")
            validation_table.add_column("Text")
            validation_table.add_column("ID")
            validation_table.add_column("Role")
            validation_table.add_column("Aria Live")
            
            for val in validation_elements:
                validation_table.add_row(
                    val.get('text', 'N/A'),
                    val.get('id', 'N/A'),
                    val.get('role', 'N/A'),
                    val.get('aria_live', 'N/A')
                )
            console.print(validation_table)

async def main():
    """Demo the enhanced form extractor"""
    console.print("[bold green]Enhanced Form Extractor Demo[/bold green]")
    console.print("This demo shows comprehensive form element extraction including:")
    console.print("• Inputs with validation attributes")
    console.print("• Submit triggers (buttons, custom elements)")
    console.print("• Validation elements")
    console.print("• Custom widgets (date pickers, file uploads, sliders)")
    console.print("• Dynamic elements (collapsible sections, toggles)")
    
    # Test with a sample URL (you can change this)
    test_url = "https://shop.deere.com/us/diagrams?dealer-id=036816&story=st969494&catalog_no=11945"
    console.print(f"\n[bold]Testing with URL: {test_url}[/bold]")
    
    try:
        form_data = await extract_enhanced_forms(test_url)
        
        if not form_data:
            console.print("[red]No forms found on this website![/red]")
            return
        
        console.print(f"[green]Found {len(form_data)} form(s)[/green]")
        
        # Display the enhanced form data
        display_enhanced_form_data(form_data)
        
        # Save detailed JSON output
        with open("enhanced_form_data.json", "w") as f:
            json.dump(form_data, f, indent=2)
        console.print(f"\n[green]Detailed form data saved to: enhanced_form_data.json[/green]")
        
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")

if __name__ == "__main__":
    asyncio.run(main()) 