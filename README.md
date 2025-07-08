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
├── test_cases/                 # Generated test cases (created automatically)
│   └── [domain]/               # Organized by website domain
│       ├── json/               # JSON format test cases
│       ├── csv/                # CSV format test cases
│       ├── reports/            # Markdown reports
│       ├── test_scripts/       # Python test scripts
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
- Creates Python test scripts
- Generates comprehensive documentation

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
3. **Customization**: Modify generated test scripts for your framework
4. **Integration**: Import test cases into your test management system

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
- **Ready-to-Run Scripts**: Generated Python test scripts
- **Framework Integration**: JSON/CSV formats for any test management system
- **CI/CD Ready**: Structured output for automated pipelines

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

## 📈 Best Practices

### 1. API Key Management
- Store API keys in environment variables
- Use `.env` files for local development
- Never commit API keys to version control

### 2. Test Case Organization
- Use the generated directory structure
- Keep test cases organized by domain
- Version control your test cases

### 3. Continuous Integration
- Run crawlers as part of your CI pipeline
- Automate test case generation
- Integrate with your test management system

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

## 📄 License

This project is open source and available under the MIT License.

## 🆘 Support

For issues and questions:
1. Check the troubleshooting section
2. Review the generated test cases for examples
3. Open an issue on the repository

---

**Happy Testing! 🧪✨** 