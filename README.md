# Video Bot

A Python-based bot that generates video responses using AI.

## Features
- Generates video responses from text scripts
- Manages conversation history
- API integration for video generation

## Installation

1. Clone the repository: 
```bash
git clone <repository-url>
```

2. Install required dependencies:
```bash
pip install -r requirements.txt
```

3. Set up your API key in an environment variable or configuration file.

## Usage

```python
from video_bot import VideoBot

# Initialize the bot with your API key
bot = VideoBot(api_key="your-api-key")

# Generate a video response
response = bot.generate_video_response("Your script here")
```

## Configuration
- Create a `.env` file and add your API key:
```
API_KEY=your-api-key-here
```

## Requirements
See `requirements.txt` for a full list of dependencies.

## License
[MIT](LICENSE)
