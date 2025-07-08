#!/usr/bin/env python3
"""
Timeout Diagnostic Script
Helps identify why a website query is timing out
"""

import asyncio
import time
from playwright.async_api import async_playwright
from rich.console import Console
from rich.table import Table

console = Console()

async def diagnose_timeout(url):
    """Diagnose timeout issues with a website"""
    console.print(f"[bold blue]Diagnosing timeout issues for: {url}[/bold blue]")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        # Set up event listeners for debugging
        page.on("request", lambda request: console.print(f"[cyan]Request: {request.method} {request.url}[/cyan]"))
        page.on("response", lambda response: console.print(f"[green]Response: {response.status} {response.url}[/green]"))
        page.on("console", lambda msg: console.print(f"[yellow]Console: {msg.text}[/yellow]"))
        
        try:
            console.print("[yellow]Starting navigation...[/yellow]")
            start_time = time.time()
            
            # Try with different timeout strategies
            try:
                # Strategy 1: Quick timeout to see if it's a network issue
                console.print("[yellow]Strategy 1: Quick timeout test (30s)[/yellow]")
                await page.goto(url, timeout=30000)
                console.print(f"[green]Success! Page loaded in {time.time() - start_time:.2f}s[/green]")
            except Exception as e:
                console.print(f"[red]Strategy 1 failed: {e}[/red]")
                
                # Strategy 2: Longer timeout with different approach
                try:
                    console.print("[yellow]Strategy 2: Longer timeout with wait (60s)[/yellow]")
                    await page.goto(url, timeout=60000, wait_until="domcontentloaded")
                    console.print(f"[green]Success! Page loaded in {time.time() - start_time:.2f}s[/green]")
                except Exception as e:
                    console.print(f"[red]Strategy 2 failed: {e}[/red]")
                    
                    # Strategy 3: Try without waiting for network idle
                    try:
                        console.print("[yellow]Strategy 3: Load without network idle wait[/yellow]")
                        await page.goto(url, timeout=60000, wait_until="load")
                        console.print(f"[green]Success! Page loaded in {time.time() - start_time:.2f}s[/green]")
                    except Exception as e:
                        console.print(f"[red]Strategy 3 failed: {e}[/red]")
                        console.print("[red]All strategies failed. Site may be blocking automated access.[/red]")
                        await browser.close()
                        return False
            
            # Check page state
            try:
                title = await page.title()
                console.print(f"[green]Page title: {title}[/green]")
            except Exception as e:
                console.print(f"[red]Could not get page title: {e}[/red]")
            
            # Check for common blocking mechanisms
            console.print("[yellow]Checking for common blocking mechanisms...[/yellow]")
            
            # Check for Cloudflare
            cloudflare_check = await page.query_selector("div[id='cf-wrapper']")
            if cloudflare_check:
                console.print("[red]⚠️  Cloudflare protection detected![/red]")
                console.print("[yellow]This site may be blocking automated access.[/yellow]")
            
            # Check for bot detection
            bot_check = await page.query_selector("div[class*='bot'], div[class*='captcha'], div[id*='captcha']")
            if bot_check:
                console.print("[red]⚠️  Bot detection/CAPTCHA detected![/red]")
            
            # Check for JavaScript errors
            console.print("[yellow]Checking for JavaScript errors...[/yellow]")
            js_errors = await page.evaluate("""
                () => {
                    const errors = [];
                    window.addEventListener('error', (e) => {
                        errors.push(e.message);
                    });
                    return errors;
                }
            """)
            
            if js_errors:
                console.print(f"[red]JavaScript errors found: {js_errors}[/red]")
            
            # Check page load time
            load_time = time.time() - start_time
            console.print(f"[green]Total load time: {load_time:.2f} seconds[/green]")
            
            if load_time > 30:
                console.print("[yellow]⚠️  Slow loading site detected[/yellow]")
                console.print("[yellow]Consider increasing timeout or using a different approach[/yellow]")
            
            # Check for forms
            forms = await page.query_selector_all("form")
            console.print(f"[green]Found {len(forms)} form(s)[/green]")
            
            # Check for dynamic content
            console.print("[yellow]Checking for dynamic content...[/yellow]")
            await page.wait_for_timeout(3000)
            
            # Check if page is still loading
            try:
                await page.wait_for_load_state("networkidle", timeout=10000)
                console.print("[green]Page finished loading[/green]")
            except Exception as e:
                console.print(f"[yellow]Page may still be loading: {e}[/yellow]")
            
            await browser.close()
            return True
            
        except Exception as e:
            console.print(f"[red]Diagnostic failed: {e}[/red]")
            await browser.close()
            return False

async def test_simple_sites():
    """Test with simple sites to compare performance"""
    console.print("[bold blue]Testing with simple sites for comparison[/bold blue]")
    
    test_sites = [
        "https://www.google.com",
        "https://httpbin.org/",
        "https://example.com"
    ]
    
    for site in test_sites:
        console.print(f"\n[yellow]Testing: {site}[/yellow]")
        success = await diagnose_timeout(site)
        if success:
            console.print(f"[green]✓ {site} works fine[/green]")
        else:
            console.print(f"[red]✗ {site} has issues[/red]")

async def main():
    """Main diagnostic function"""
    console.print("[bold green]Timeout Diagnostic Tool[/bold green]")
    console.print("This tool helps identify why website queries are timing out.")
    
    # Test the problematic URL
    url = "https://shop.deere.com/us/diagrams?dealer-id=036816&story=st969494&catalog_no=11945"
    
    console.print(f"\n[bold]Testing problematic URL: {url}[/bold]")
    success = await diagnose_timeout(url)
    
    if not success:
        console.print("\n[bold red]Recommendations:[/bold red]")
        console.print("1. The site may have anti-bot protection")
        console.print("2. Try using a different user agent")
        console.print("3. Consider using a proxy or VPN")
        console.print("4. The site may be blocking automated access")
        console.print("5. Try accessing the site manually first")
        
        # Test with simple sites for comparison
        await test_simple_sites()

if __name__ == "__main__":
    asyncio.run(main()) 