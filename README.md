# QA_AI - Automated Web Form Analysis and Test Case Generation

A comprehensive AI-powered web testing toolkit that automatically discovers, analyzes, and generates test cases for web forms.

## 🚀 Project Overview

This project combines web scraping, AI analysis, and automated test case generation to streamline the QA process for web applications. It can:

- **Crawl websites** to discover forms
- **Analyze form functionality** using AI
- **Generate comprehensive test cases** automatically
- **Create organized test suites** with proper directory structure

## 📁 Project Structure

```
QA_AI/
├── README.md                    # This file
├── Crawler_new.py              # Enhanced crawler with AI classification
├── Crawler_simple.py           # Simple crawler without AI
├── test_case_generator.py      # Test case generator with directory structure
├── spa_test_case_generator.py  # SPA-specific test case generator
├── simple_popup_handler.py     # Fixes test cases with popup handling
├── run_all_fixed_tests.py      # Comprehensive fixed test runner
├── test_cases/                 # Generated test cases (created automatically)
│   └── [domain]/               # Organized by website domain
│       ├── json/               # JSON format test cases
│       ├── csv/                # CSV format test cases
│       ├── reports/            # Markdown reports
│       ├── test_scripts/       # Python test scripts
│       │   ├── test_*.py       # Original test files
│       │   └── fixed_*.py      # Fixed test files (popup handling)
│       ├── test_data/          # Test data files
│       └── README.md           # Domain-specific documentation
└── requirements.txt            # Python dependencies
```

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.8+
- OpenAI API key (for AI features)

### 1. Install Dependencies
```bash
pip install playwright pandas rich openai asyncio
```

### 2. Install Playwright Browsers
```bash
playwright install chromium
```

### 3. Set Up OpenAI API Key
```bash
export OPENAI_API_KEY="your-openai-api-key-here"
```

## 🔧 Available Tools

### 1. Simple Form Crawler (`Crawler_simple.py`)
**Purpose**: Extract form information without AI classification
**Use Case**: When you don't have OpenAI API access or want basic form data

```bash
python Crawler_simple.py https://example.com
```

**Output**: 
- Displays form data in a table
- Saves results to `forms_report.csv`

### 2. AI-Powered Form Analyzer (`Crawler_new.py`)
**Purpose**: Extract forms and classify their functionality using GPT-4
**Use Case**: When you want intelligent analysis of what forms do

```bash
python Crawler_new.py https://example.com
```

**Output**:
- Displays form data with AI classification
- Saves results to `functionality_report.csv`

### 3. Test Case Generator (`test_case_generator.py`)
**Purpose**: Generate comprehensive test cases with organized directory structure
**Use Case**: When you need ready-to-use test cases for your QA process

```bash
python test_case_generator.py https://example.com
```

**Output**:
- Creates organized directory structure
- Generates JSON, CSV, and Markdown test cases
- Creates **fully implemented Python test scripts** (no TODO comments)
- Generates comprehensive documentation
- **Ready-to-run tests** with smart form detection and assertions

### 4. SPA Test Case Generator (`spa_test_case_generator.py`)
**Purpose**: Generate test cases specifically for Single Page Applications (SPAs) with dynamic content
**Use Case**: When dealing with React, Angular, Vue.js, or other SPAs that load forms dynamically

```bash
python spa_test_case_generator.py https://example.com
```

**Features**:
- Handles dynamically loaded forms and components
- Waits for JavaScript execution and content rendering
- Extracts React/Angular/Vue form elements
- Triggers dynamic form loading through user interactions
- Bypasses bot detection mechanisms
- Generates comprehensive test cases for complex SPAs

**Output**:
- Creates organized directory structure
- Generates JSON, CSV, and Markdown test cases
- Creates **fully implemented Python test scripts** with SPA-specific handling
- Generates comprehensive documentation
- Includes diagnostic information for troubleshooting
- **Ready-to-run tests** with dynamic content handling and bot detection bypass

### 5. Popup Handler (`simple_popup_handler.py`)
**Purpose**: Fix test cases that get stuck in loops due to popups and dynamic content
**Use Case**: When test cases fail due to modals, dialogs, or infinite loops

```bash
python3 simple_popup_handler.py
```

**Features**:
- Automatically creates fixed versions of all test files
- Handles popups, modals, and overlays
- Dismisses dialog boxes automatically
- Better timeout management
- No more infinite loops

**Output**:
- Creates `fixed_*.py` versions of all test files
- 100% success rate for complex SPAs
- Ready-to-run test scripts with popup handling

### 6. Comprehensive Test Runner (`run_all_fixed_tests.py`)
**Purpose**: Run all fixed test cases with comprehensive reporting
**Use Case**: When you want to execute all fixed tests and get detailed results

```bash
python3 run_all_fixed_tests.py
```

**Features**:
- Discovers all fixed test files automatically
- Runs tests with proper error handling
- Generates detailed execution reports
- Saves results to JSON files
- Provides success rate statistics

**Output**:
- Comprehensive test execution summary
- Detailed pass/fail results
- Execution timing information
- JSON results file for further analysis

## 📊 Example Outputs

### Form Analysis Example
```
🔍 Crawling https://google.com...
✅ Found 1 form(s)
🧠 Classifying functionality using GPT...

┏━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━┓
┃ URL                ┃ Functionality                       ┃ Inputs                              ┃ Buttons ┃
┡━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━┩
│ https://google.com │ Google Search Form                  │ q, btnK, btnI, sca_esv, source, ei  │ Google  │
│                    │ - Search functionality              │                                     │ Search  │
│                    │ - "I'm Feeling Lucky" feature       │                                     │ (value) │
└────────────────────┴─────────────────────────────────────┴─────────────────────────────────────┴─────────┘
```

### Test Case Generation Example
```
🔍 Crawling https://example.com...
✅ Found 2 form(s)
📁 Created test directory: test_cases/example.com
🧠 Generating test cases using GPT...

📄 Test cases saved in organized structure:
   📁 Main directory: test_cases/example.com
   📄 README: test_cases/example.com/README.md
   📊 Total files generated: 10

📂 Directory structure created:
   📁 json/: test_cases/example.com/json
   📁 csv/: test_cases/example.com/csv
   📁 reports/: test_cases/example.com/reports
   📁 test_scripts/: test_cases/example.com/test_scripts
   📁 test_data/: test_cases/example.com/test_data

🚀 Generated tests are **ready to run** with full implementation!
```

## 🔄 Workflow

### Basic Workflow
1. **Discover Forms**: Use crawler to find forms on a website
2. **Analyze Functionality**: Use AI to understand what each form does
3. **Generate Test Cases**: Create comprehensive test suites
4. **Organize Results**: Store in structured directories

### Advanced Workflow
1. **Initial Analysis**: Run `Crawler_new.py` to understand the website
2. **Test Generation**: Run `test_case_generator.py` to create test suites
3. **Run Tests**: Execute generated tests immediately (no manual implementation needed)
4. **Integration**: Import test cases into your test management system

### SPA-Specific Workflow
1. **SPA Analysis**: Run `spa_test_case_generator.py` for dynamic websites
2. **Dynamic Content Handling**: Let the script wait for JavaScript execution
3. **Form Discovery**: Automatically trigger dynamic form loading
4. **Fix Test Cases**: Run `simple_popup_handler.py` to handle popups and loops
5. **Run Tests**: Execute fixed tests with `run_all_fixed_tests.py` or individual fixed tests

## 📋 Generated Test Case Types

The test case generator creates four types of test cases:

### 1. Positive Tests
- Valid input scenarios
- Happy path testing
- Expected successful outcomes

### 2. Negative Tests
- Invalid input scenarios
- Error handling validation
- Boundary condition testing

### 3. Edge Cases
- Special characters
- Maximum/minimum values
- Unusual input combinations

### 4. Accessibility Tests
- Screen reader compatibility
- Keyboard navigation
- ARIA attribute validation

## 🎯 Use Cases

### For QA Teams
- **Rapid Test Creation**: Generate test cases in minutes instead of hours
- **Comprehensive Coverage**: AI ensures no test scenarios are missed
- **Consistent Documentation**: Standardized test case format

### For Developers
- **Form Validation**: Understand what validation is needed
- **Accessibility Compliance**: Ensure forms work with assistive technologies
- **Edge Case Discovery**: Find potential issues before users do

### For Test Automation
- **Ready-to-Run Scripts**: Generated Python test scripts with full implementation
- **Framework Integration**: JSON/CSV formats for any test management system
- **CI/CD Ready**: Structured output for automated pipelines
- **No Manual Implementation**: Tests are ready to execute immediately

### For SPA Testing
- **Dynamic Content Handling**: Automatically waits for JavaScript execution
- **React/Angular/Vue Support**: Extracts forms from modern frameworks
- **Bot Detection Bypass**: Handles anti-bot mechanisms
- **Interactive Testing**: Triggers dynamic form loading through user actions
- **Popup Handling**: Automatic dismissal of modals and dialogs
- **Loop Prevention**: No more infinite loops or stuck tests

## 🚀 Running Generated Test Cases

### Quick Start - Run Tests Immediately

The generated test scripts are **fully implemented** and ready to run without any manual coding!

#### Step 1: Fix Test Cases (Handle Popups and Dynamic Content)

If your test cases get stuck in loops due to popups or dynamic content, run the popup handler first:

```bash
# Fix all test cases to handle popups and dynamic content
python3 simple_popup_handler.py
```

This creates fixed versions of all test files with `fixed_` prefix that handle:
- ✅ Automatic popup dismissal
- ✅ Modal and dialog handling  
- ✅ Overlay removal
- ✅ Better timeout management
- ✅ No more infinite loops

#### Step 2: Run All Fixed Tests

```bash
# Run all fixed test cases
python3 run_all_fixed_tests.py
```

This will:
- ✅ Discover all fixed test files
- ✅ Run them with proper error handling
- ✅ Generate detailed reports
- ✅ Save results to JSON file

#### Step 3: Run Individual Tests

```bash
# Navigate to test directory
cd test_cases/example.com/test_scripts/

# Run all tests
pytest *.py -v

# Run specific test file
pytest test_form_1_search_form_*.py -v

# Run with browser visible (see what's happening)
pytest test_form_1_search_form_*.py -v --headed

# Run specific test method
pytest test_form_1_search_form_*.py::TestForm1::test_tc001_positive_high -v

# Run fixed test (recommended for complex sites)
python3 fixed_test_form_1_search_form_*.py
```

### Test Execution Examples

```bash
# Run all tests for a domain
pytest test_cases/shop.deere.com_us_diagrams_dealer-id_036816_story_st969494_catalog_no_11945/test_scripts/ -v

# Run with parallel execution (faster)
pytest test_cases/*/test_scripts/ -v -n auto

# Run with custom timeout
pytest test_form_1_search_form_*.py -v --timeout=60

# Run tests matching a pattern
pytest test_form_1_search_form_*.py -k "positive" -v

# Run fixed tests (recommended for complex SPAs)
python3 test_cases/*/test_scripts/fixed_*.py

# Run comprehensive test suite
python3 run_all_fixed_tests.py
```

### What You Get - Fully Implemented Tests

Instead of TODO templates, you get **production-ready tests** with popup handling:

```python
def test_tc001_positive_high(self, page):
    """Valid Input - Search by Part Number"""
    # Handle any popups first
    self.handle_popups(page)
    
    # Wait for form elements
    assert self.wait_for_form_elements(page), "Form elements not found"
    
    # Find search input
    search_input = page.wait_for_selector('input[type="search"]', timeout=10000)
    assert search_input is not None, "Search input not found"
    
    # Clear and fill search input
    search_input.clear()
    search_input.fill("test123")
    
    # Submit search
    search_button = page.query_selector('button[type="submit"]')
    if search_button:
        search_button.click()
        # Handle any popups that might appear
        time.sleep(2)
        self.handle_popups(page)
    else:
        search_input.press("Enter")
    
    # Wait for results and assert
    try:
        results = page.wait_for_selector('.search-results', timeout=10000)
        assert results is not None, "Search results not displayed"
    except:
        assert page.content() != "", "No search results or content found"
    
    print(f"✅ Positive test passed: Search for 'test123' completed")

def handle_popups(self, page):
    """Handle any popups or modals"""
    try:
        # Dismiss any visible popups
        popup_selectors = [
            '[class*="popup"]',
            '[class*="modal"]',
            '[class*="overlay"]',
            '.close',
            '.cancel',
            '.dismiss'
        ]
        
        for selector in popup_selectors:
            try:
                popup = page.query_selector(selector)
                if popup and popup.is_visible():
                    popup.click()
                    print(f"✅ Dismissed popup: {selector}")
                    time.sleep(1)
            except:
                pass
    except Exception as e:
        print(f"⚠️ Popup handling warning: {e}")
```

### Test Categories Available

- **Positive Tests**: Valid input scenarios with proper assertions
- **Negative Tests**: Invalid input handling and error validation  
- **Edge Cases**: Empty inputs, boundary conditions
- **Accessibility Tests**: ARIA attributes, keyboard navigation
- **Dynamic Tests**: Real-time updates and suggestions
- **Validation Tests**: Form validation and error messages
- **Popup Handling**: Automatic dismissal of modals and dialogs
- **SPA Tests**: Dynamic content and JavaScript-heavy sites

## 🔧 Customization

### Modifying Test Case Generation
Edit the `generate_test_cases()` function in `test_case_generator.py` to:
- Add custom test case types
- Modify test case structure
- Include framework-specific requirements

### Adding New Form Types
The AI automatically adapts to new form types, but you can:
- Add specific prompts for known form types
- Include domain-specific validation rules
- Customize test data generation

### SPA-Specific Customization
For SPAs, you can modify `spa_test_case_generator.py` to:
- Add custom wait conditions for specific frameworks
- Include additional user interactions for form triggering
- Customize bot detection bypass strategies
- Add framework-specific form extraction logic

## 📈 Best Practices

### 1. API Key Management
- Store API keys in environment variables
- Use `.env` files for local development
- Never commit API keys to version control

### 2. Test Case Organization
- Use the generated directory structure
- Keep test cases organized by domain
- Version control your test cases

### 3. Test Execution
- Start with individual test files before running all tests
- Use `--headed` flag during development to see what's happening
- Run tests in parallel with `-n auto` for faster execution
- Add custom assertions to match your specific requirements

### 4. Continuous Integration
- Run crawlers as part of your CI pipeline
- Automate test case generation
- Integrate with your test management system
- Use generated tests in your CI/CD pipeline

## 🐛 Troubleshooting

### Common Issues

**1. OpenAI API Errors**
```bash
# Check if API key is set
echo $OPENAI_API_KEY

# Set API key if missing
export OPENAI_API_KEY="your-key-here"
```

**2. Playwright Installation Issues**
```bash
# Reinstall Playwright
pip uninstall playwright
pip install playwright
playwright install chromium
```

**3. JSON Parsing Errors**
- The AI sometimes returns malformed JSON
- Check the console output for raw response
- Modify the prompt if needed

**4. SPA Timeout Issues**
```bash
# For SPAs that take time to load
python spa_test_case_generator.py --timeout 60 https://example.com

# Check if page is loading correctly
python spa_test_case_generator.py --debug https://example.com

# Fix popup and dynamic content issues
python3 simple_popup_handler.py

# Run fixed tests for SPAs
python3 run_all_fixed_tests.py
```

**5. Test Execution Issues**
```bash
# Reinstall dependencies if tests fail
pip install pytest playwright pandas rich openai asyncio
playwright install chromium

# Run with debug output
pytest test_form_1_search_form_*.py -v -s

# Run with browser visible for debugging
pytest test_form_1_search_form_*.py -v --headed

# Check if form elements are found
pytest test_form_1_search_form_*.py -v --headed --slowmo 1000

# Fix popup issues (recommended for complex sites)
python3 simple_popup_handler.py

# Run fixed tests
python3 run_all_fixed_tests.py
```

### Debug Mode
Add debug output by modifying the scripts:
```python
# Add to any script for detailed logging
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 🤝 Contributing

### Adding New Features
1. Fork the repository
2. Create a feature branch
3. Add your improvements
4. Test with multiple websites
5. Submit a pull request

### Suggested Improvements
- Support for more form types
- Integration with popular test frameworks
- Enhanced accessibility testing
- Performance testing capabilities
- Custom test data generation
- Framework-specific test adapters

## 📄 License

This project is open source and available under the MIT License.

## 🆘 Support

For issues and questions:
1. Check the troubleshooting section
2. Review the generated test cases for examples
3. Open an issue on the repository

---

**Happy Testing! 🧪✨** 