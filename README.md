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
- **Revolutionary music sharing and playback system**
- **Collective Groups system for community organization**
- **Revolutionary Image Gallery with commenting system**
- **Group chat system for collective discussions**
- **Admin panel for Party leadership oversight**
- **User profiles with customizable icons and profile pictures**
- **Search functionality for music and gallery images**

## Language Support

The application supports both English and Russian languages. Users can switch between languages by clicking on the language buttons (EN/RU) at the top-right corner of any page.

### Adding New Translations

To add a new language:

1. Create a new directory under `translations/` with the language code
2. Copy the translation templates and translate the strings
3. Compile the translations with `python compile_translations.py` 

## Music Library

The application features a revolutionary music library where users can:

- Upload music files (.mp3, .wav, .ogg)
- Browse music shared by other comrades
- Search for music by title, artist, or description
- Listen to music directly in the browser 

### Music Search Rules

The music search functionality operates according to the following principles:

1. **Case-Insensitive Matching**: All searches are performed case-insensitively, allowing users to find music regardless of capitalization.
2. **Multi-Field Search**: The search engine examines three fields:
   - Song title
   - Artist name
   - Description text
3. **Substring Matching**: The search matches any part of the field content, not just the beginning.
4. **Single Query Approach**: One search term is used to match across all fields simultaneously.
5. **Empty Results Handling**: When no matches are found, a revolutionary message encourages users to contribute.

The search is designed with the ideals of accessibility and community in mind, ensuring all comrades can easily find revolutionary music to inspire their cause.

## Collective Groups

The application features a collective groups system where comrades can:

- Create new collectives with a name and description
- Join existing collectives to participate in group activities
- Leave collectives at any time
- Participate in group discussions via the group chat feature
- View all members of a collective

## Revolutionary Image Gallery

The revolutionary image gallery allows comrades to:

- Upload revolutionary images (.png, .jpg, .jpeg, .gif)
- Provide titles and descriptions for each image
- View images uploaded by other comrades
- Comment on images to stimulate collective discourse
- Search for images by title, author, or description

## Administration Features

Party leaders with administrative privileges can:

- Access a dedicated admin panel
- Remove users from the system when necessary
- Dissolve collectives that no longer serve the revolutionary cause
- Remove revolutionary music that doesn't align with Party values
- Delete gallery images that don't contribute to the collective good

## User Profile System

The profile system allows comrades to:

- Set a personalized revolutionary bio
- Choose a symbolic icon to represent themselves
- Upload a profile picture
- Update personal information
- View all collectives they've joined 