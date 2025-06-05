# Travel Weather Forecast

A Python project for retrieving and displaying weather forecasts for travel planning. This project is designed to help users check weather conditions for various destinations, making it easier to plan trips and pack accordingly.

## Features
- Fetches weather forecasts for specified locations
- Supports multiple destinations
- Command-line interface for quick access
- Easy to configure and extend

## Requirements
- Python 3.7 or higher
- See `requirements.txt` for dependencies

## Setup
1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd Travel-Weather-Forecast
   ```
2. **Create a virtual environment (recommended):**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```
3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
4. **Set up environment variables:**
   - Create a `.env` directory or file as needed for your API keys and configuration.
   - Example variables:
     ```env
     WEATHER_API_KEY=your_api_key_here
     ```

## Usage
Run the main script to get weather forecasts:
```bash
python main.py
```

You may be prompted to enter destination(s) or configure them in the script.

## Project Structure
- `main.py` — Main application script
- `requirements.txt` — Python dependencies
- `.env/` or `.env` — Environment variables (not tracked by git)

## Notes
- The `.env/` directory and `.env` files are ignored by git for security.
- Make sure to obtain and set your weather API key in the environment variables.

## License
This project is licensed under the MIT License. See the `LICENSE` file for details.