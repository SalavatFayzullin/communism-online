# Communism Online

A Flask web application with a communist-themed welcome page and user authentication system.

## Setup and Running

1. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

2. Compile translations (optional, already compiled in the repository):
   ```
   python compile_translations.py
   ```

3. Run the application:
   ```
   python app.py
   ```

4. Open your web browser and navigate to:
   ```
   http://127.0.0.1:5000/
   ```

## Features

- Communist-themed welcome page using red and orange colors
- User registration and login system with session management
- Personalized user profiles with communist-themed design
- Channels for organizing discussions by topic
- Posts and comments system for user interaction
- Responsive design that works on various screen sizes
- Famous quotes and themed content
- **Multi-language support (English and Russian)**

## Language Support

The application supports both English and Russian languages. Users can switch between languages by clicking on the language buttons (EN/RU) at the top-right corner of any page.

### Adding New Translations

To add a new language:

1. Create a new directory under `translations/` with the language code
2. Copy the translation templates and translate the strings
3. Compile the translations with `python compile_translations.py` 