# QualiGPT Web Application

A modern web-based version of QualiGPT - an AI-powered qualitative data analysis tool that uses state-of-the-art LLMs (OpenAI GPT-4o, Anthropic Claude, Google Gemini, DeepSeek) to perform thematic analysis on interview data, focus groups, and social media posts.

> **Looking for in-depth architecture & developer docs?  See [`docs/DETAILED_DOCUMENTATION.md`](docs/DETAILED_DOCUMENTATION.md).**

## 🚀 What's New in the Web Version

- **No Installation Hassles**: Runs in any web browser
- **Modern Interface**: Clean, responsive design with real-time feedback
- **Interactive Results Table**: Beautiful, sortable, searchable, and exportable table for analysis results
- **Advanced Model Selection**: Choose from OpenAI, Anthropic, Gemini, DeepSeek and their latest models
- **Advanced Settings**: Control temperature, max tokens, and more from the UI
- **Reliable CSV Export**: Exports exactly what you see in the table, compatible with Excel/Sheets
- **Multi-Provider Support**: Plug-and-play with OpenAI GPT-4o, Anthropic Claude, Google Gemini, DeepSeek
- **Cross-Platform**: Works on Mac, Windows, Linux, tablets
- **Easy Deployment**: Run locally or deploy to cloud platforms
- **Docker Support**: Complete containerization with production-ready Gunicorn deployment
- **Clean Output**: Enhanced prompts for structured results without extra commentary

## ✨ Screenshots

![QualiGPT Interactive Table Screenshot](graph/QualiGPT-workflow.png)

## Features

- **Easy API Integration**: Simple connection to your favorite LLM provider with key validation
- **Multiple File Formats**: Support for CSV, XLSX, and DOCX files
- **Flexible Analysis Types**: 
  - Interviews
  - Focus Groups
  - Social Media Posts
- **Customizable Analysis**:
  - Adjustable number of themes (1-20)
  - Role-playing mode for expert analysis
  - Custom prompts for specific needs
  - Advanced settings (temperature, max tokens)
- **Smart Data Handling**: Automatic segmentation for large datasets (up to 120k tokens)
- **Provider & Model Choice**: Select your provider and model directly from the UI
- **Export Options**: Save results as CSV (table) or TXT (raw + summary)
- **Production Ready**: Docker support with Gunicorn for scalable deployment

## 🛠️ Installation

### Prerequisites
- Python 3.8+
- (Optional) Docker

### Option 1: Run with Python (Recommended for Development)

```bash
# Clone the repository
git clone <repository-url>
cd QualiGPT-MT

# Create a virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Download NLTK data (one-time setup)
python -c "import nltk; nltk.download('punkt_tab')"

# Start the web server
python qualigpt-webapp.py
```

Open your browser to: **http://localhost:5000**

### Option 2: Run with Docker (Recommended for Production)

```bash
docker-compose up --build
```

Open your browser to: **http://localhost:5005**

## 📖 How to Use QualiGPT

### Step 1: Connect to Your Provider
1. Select your provider (OpenAI, Anthropic, Gemini, DeepSeek)
2. Choose your model (e.g., GPT-4o, Gemini 2.5 Flash, Claude 3.5 Sonnet)
3. Enter your API key
4. Click "Connect" to validate your key
5. Wait for the green "Connected" status

### Step 2: Upload Your Data
1. Click the upload area or drag-and-drop your file
2. **Supported formats**: CSV, XLSX, DOCX
3. **File size limit**: 16MB maximum
4. Preview your data to ensure it loaded correctly

### Step 3: Configure Analysis
1. **Select Data Type**: Interview, Focus Group, or Social Media Posts
2. **Set Number of Themes**: Choose 1-20 themes to extract
3. **Advanced Settings**: Adjust temperature and max tokens as needed
4. **Optional**: Enable Role-Playing Mode or add a Custom Prompt

### Step 4: Run Analysis
1. Click "Analyze Data"
2. Wait for processing (5-30 seconds for most files)
3. Large files are automatically segmented and processed in parts
4. View the structured results in a beautiful, interactive table

### Step 5: Export Results
- **CSV Export**: Download exactly what you see in the table (works in Excel/Sheets)
- **Text Export**: Save the raw response and a formatted summary

## 📂 Sample Data Files

- `qualigpt-test-data.csv` - Sample CSV interview data
- `sample-social-media.xlsx` - Sample Excel social media data
- `sample-interview.docx` - Sample Word document

## 📝 File Format Guidelines

### CSV/XLSX Files
```csv
Participant,Age,Response
P1,25,"I think remote work has improved my work-life balance"
P2,32,"The biggest challenge is staying connected with the team"
P3,28,"I miss the spontaneous conversations in the office"
```

### DOCX Files
- Each paragraph becomes a separate data entry

## 🧑‍💻 Developer Notes
- See [`docs/DETAILED_DOCUMENTATION.md`](docs/DETAILED_DOCUMENTATION.md) for architecture, API, and extension details.
- See [`docs/PROJECT_PLAN.md`](docs/PROJECT_PLAN.md) for roadmap and future features.

## �� License
MIT

## 🔮 Future Enhancements

- Support for additional AI models (Claude, Gemini)
- Batch processing for multiple files
- Real-time collaborative analysis
- Advanced visualization dashboards
- Integration with survey platforms
- API for programmatic access

## 📄 License

This project is released under the MIT License.

## 🙏 Credits

- **Original QualiGPT**: He Zhang et al. - Desktop application research
- **Web Version**: Modern reimplementation for accessible qualitative research
- **AI Integration**: OpenAI GPT-4o for enhanced analysis capabilities

## 📞 Support

For issues or questions:
1. Check the troubleshooting section above
2. Review sample files for format examples
3. Verify your OpenAI API key and credits
4. Ensure your data meets format requirements

---

**Ready to analyze your qualitative data? Start with the installation instructions above! 🚀**
