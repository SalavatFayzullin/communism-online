from flask import Flask, render_template, request, redirect, url_for, flash, session, g
import os
import secrets
from werkzeug.utils import secure_filename
import logging
from datetime import datetime
from flask_babel import Babel, gettext as _, refresh

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = os.urandom(24)  # For session management
# Use absolute path for the upload folder
base_dir = os.path.abspath(os.path.dirname(__file__))
app.config['UPLOAD_FOLDER'] = os.path.join(base_dir, 'static', 'uploads', 'profile_pics')
app.config['MUSIC_FOLDER'] = os.path.join(base_dir, 'static', 'uploads', 'music')
app.config['GALLERY_FOLDER'] = os.path.join(base_dir, 'static', 'uploads', 'gallery')
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}
app.config['ALLOWED_MUSIC_EXTENSIONS'] = {'mp3', 'wav', 'ogg'}
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB max upload

# Babel configuration
app.config['BABEL_DEFAULT_LOCALE'] = 'en'
app.config['BABEL_TRANSLATION_DIRECTORIES'] = 'translations'
babel = Babel(app)

@babel.localeselector
def get_locale():
    # if a user is logged in, use the locale from the session
    if 'language' in session:
        return session['language']
    return request.accept_languages.best_match(['en', 'ru', 'default'])

# Create upload folders if they don't exist
try:
    upload_path = app.config['UPLOAD_FOLDER']
    music_path = app.config['MUSIC_FOLDER']
    gallery_path = app.config['GALLERY_FOLDER']
    os.makedirs(upload_path, exist_ok=True)
    os.makedirs(music_path, exist_ok=True)
    os.makedirs(gallery_path, exist_ok=True)
    logger.debug(f"Upload directory created/confirmed at: {upload_path}")
    logger.debug(f"Music directory created/confirmed at: {music_path}")
    logger.debug(f"Gallery directory created/confirmed at: {gallery_path}")
    logger.debug(f"Directory exists: {os.path.exists(upload_path)}")
    logger.debug(f"Directory is writable: {os.access(upload_path, os.W_OK)}")
except Exception as e:
    logger.error(f"Error creating upload directories: {str(e)}")

# Mock user database - in a real app, you would use a database
users = {
    'admin': {
        'password': 'admin123',
        'bio': _('Supreme leader of the Communist Party'),
        'name': 'Administrator',
        'email': 'admin@communismonline.com',
        'icon': '☭',
        'profile_pic': None,
        'is_admin': True  # Admin role flag
    }
}

# Function to check if current user is an admin
def is_admin():
    if 'username' not in session:
        return False
    username = session['username']
    return username in users and users[username].get('is_admin', False)

# Mock groups database
groups = {}

# Track group memberships
group_memberships = {}

# Mock group chat messages
group_messages = {}

# Mock channels database
channels = {
    "general": {
        "name": _("General"),
        "description": _("General discussion for all comrades"),
        "posts": []
    },
    "theory": {
        "name": _("Theory"),
        "description": _("Discussion of communist theory and literature"),
        "posts": []
    },
    "news": {
        "name": _("News"),
        "description": _("Current events and news from around the world"),
        "posts": []
    }
}

# Initialize with some example posts
example_posts = [
    {
        "id": "post1",
        "channel": "general",
        "author": "system",
        "title": _("Welcome to Communism Online"),
        "content": _("Welcome to our platform where all comrades can share ideas for the collective good!"),
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "comments": [
            {
                "id": "comment1",
                "author": "system",
                "content": _("First comment on our glorious platform!"),
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        ]
    }
]

# Add example posts to channels
for post in example_posts:
    channels[post["channel"]]["posts"].append(post)

# Mock music database
music_files = [
    {
        'id': 'example1',
        'title': 'The Internationale',
        'artist': 'Pierre De Geyter',
        'description': _('The anthem of the international communist movement'),
        'filename': 'example_music.mp3',  # This would be a real file in production
        'original_filename': 'the_internationale.mp3',
        'mimetype': 'audio/mp3',
        'uploader': 'system',
        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    },
    {
        'id': 'example2',
        'title': 'Soviet National Anthem',
        'artist': 'The Red Army Choir',
        'description': _('The national anthem of the Soviet Union from 1944 to 1991'),
        'filename': 'example_music2.mp3',  # This would be a real file in production
        'original_filename': 'soviet_anthem.mp3',
        'mimetype': 'audio/mp3',
        'uploader': 'system',
        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
]

# Mock gallery database
gallery_images = []

# Mock gallery comments database
gallery_comments = {}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def allowed_music_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_MUSIC_EXTENSIONS']

@app.route('/switch_language/<language>')
def switch_language(language):
    # Save the current URL to redirect back to it after language switch
    next_url = request.args.get('next') or request.referrer or url_for('index')
    
    # Set new language in session
    session['language'] = language
    refresh()  # Refresh translations
    
    return redirect(next_url)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/channels')
def channels_list():
    if 'username' not in session:
        flash(_('You must join the ranks first, Comrade!'))
        return redirect(url_for('login'))
    
    return render_template('channels.html', channels=channels)

@app.route('/channel/<channel_id>')
def channel_view(channel_id):
    if 'username' not in session:
        flash(_('You must join the ranks first, Comrade!'))
        return redirect(url_for('login'))
    
    if channel_id not in channels:
        flash(_('This channel does not exist, Comrade!'))
        return redirect(url_for('channels_list'))
    
    channel = channels[channel_id]
    return render_template('channel.html', channel=channel, channel_id=channel_id)

@app.route('/create_post/<channel_id>', methods=['GET', 'POST'])
def create_post(channel_id):
    if 'username' not in session:
        flash(_('You must join the ranks first, Comrade!'))
        return redirect(url_for('login'))
    
    if channel_id not in channels:
        flash(_('This channel does not exist, Comrade!'))
        return redirect(url_for('channels_list'))
    
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        
        if not title or not content:
            flash(_('All fields are required for the glory of the collective!'))
            return redirect(url_for('create_post', channel_id=channel_id))
        
        post_id = f"post_{secrets.token_hex(8)}"
        new_post = {
            "id": post_id,
            "channel": channel_id,
            "author": session['username'],
            "title": title,
            "content": content,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "comments": []
        }
        
        channels[channel_id]["posts"].insert(0, new_post)  # Add to the beginning
        flash(_('Your message has been shared with the collective!'))
        return redirect(url_for('channel_view', channel_id=channel_id))
    
    return render_template('create_post.html', channel_id=channel_id, channel=channels[channel_id])

@app.route('/post/<channel_id>/<post_id>')
def view_post(channel_id, post_id):
    if 'username' not in session:
        flash(_('You must join the ranks first, Comrade!'))
        return redirect(url_for('login'))
    
    if channel_id not in channels:
        flash(_('This channel does not exist, Comrade!'))
        return redirect(url_for('channels_list'))
    
    # Find the post
    post = None
    for p in channels[channel_id]["posts"]:
        if p["id"] == post_id:
            post = p
            break
    
    if not post:
        flash(_('This post has been redistributed, Comrade!'))
        return redirect(url_for('channel_view', channel_id=channel_id))
    
    return render_template('post.html', channel_id=channel_id, post=post, channel=channels[channel_id])

@app.route('/add_comment/<channel_id>/<post_id>', methods=['POST'])
def add_comment(channel_id, post_id):
    if 'username' not in session:
        flash(_('You must join the ranks first, Comrade!'))
        return redirect(url_for('login'))
    
    if channel_id not in channels:
        flash(_('This channel does not exist, Comrade!'))
        return redirect(url_for('channels_list'))
    
    content = request.form.get('content', '')
    
    if not content:
        flash(_('Comments require content for the betterment of the collective!'))
        return redirect(url_for('view_post', channel_id=channel_id, post_id=post_id))
    
    # Find the post and add the comment
    for post in channels[channel_id]["posts"]:
        if post["id"] == post_id:
            comment_id = f"comment_{secrets.token_hex(8)}"
            comment = {
                "id": comment_id,
                "author": session['username'],
                "content": content,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            post["comments"].append(comment)
            flash(_('Your comment has been added to the collective discourse!'))
            break
    
    return redirect(url_for('view_post', channel_id=channel_id, post_id=post_id))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if username in users and users[username]['password'] == password:
            session['username'] = username
            flash(_('Welcome back, Comrade!'))
            return redirect(url_for('profile'))
        else:
            flash(_('Invalid credentials, Comrade. The Party demands accuracy!'))
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if username in users:
            flash(_('This comrade name is already serving the cause!'))
        else:
            users[username] = {
                'password': password,
                'bio': _('A loyal comrade of the Party'),
                'name': username,
                'email': '',
                'icon': '☭',
                'profile_pic': None,
                'is_admin': False  # Regular users are not admins by default
            }
            flash(_('Welcome to the ranks, Comrade!'))
            session['username'] = username
            return redirect(url_for('profile'))
    
    return render_template('register.html')

@app.route('/groups')
def groups_list():
    if 'username' not in session:
        flash(_('You must join the ranks first, Comrade!'))
        return redirect(url_for('login'))
    
    # Get the list of groups the user belongs to
    user_groups = []
    username = session['username']
    if username in group_memberships:
        for group_id in group_memberships[username]:
            if group_id in groups:
                user_groups.append(groups[group_id])
    
    return render_template('groups.html', groups=groups, user_groups=user_groups)

@app.route('/create_group', methods=['GET', 'POST'])
def create_group():
    if 'username' not in session:
        flash(_('You must join the ranks first, Comrade!'))
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        
        if not name or not description:
            flash(_('All fields are required for the glory of the collective!'))
            return redirect(url_for('create_group'))
        
        # Create a unique group ID
        group_id = f"group_{secrets.token_hex(8)}"
        
        # Create the group
        groups[group_id] = {
            "id": group_id,
            "name": name,
            "description": description,
            "creator": session['username'],
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
        
        # Initialize group chat messages
        group_messages[group_id] = []
        
        # Add creator to the group
        username = session['username']
        if username not in group_memberships:
            group_memberships[username] = []
        group_memberships[username].append(group_id)
        
        flash(_('New collective has been formed!'))
        return redirect(url_for('group_view', group_id=group_id))
    
    return render_template('create_group.html')

@app.route('/group/<group_id>')
def group_view(group_id):
    if 'username' not in session:
        flash(_('You must join the ranks first, Comrade!'))
        return redirect(url_for('login'))
    
    if group_id not in groups:
        flash(_('This collective does not exist, Comrade!'))
        return redirect(url_for('groups_list'))
    
    group = groups[group_id]
    is_member = False
    username = session['username']
    
    if username in group_memberships and group_id in group_memberships[username]:
        is_member = True
    
    return render_template('group.html', group=group, is_member=is_member)

@app.route('/join_group/<group_id>')
def join_group(group_id):
    if 'username' not in session:
        flash(_('You must join the ranks first, Comrade!'))
        return redirect(url_for('login'))
    
    if group_id not in groups:
        flash(_('This collective does not exist, Comrade!'))
        return redirect(url_for('groups_list'))
    
    username = session['username']
    if username not in group_memberships:
        group_memberships[username] = []
    
    if group_id not in group_memberships[username]:
        group_memberships[username].append(group_id)
        flash(_('You have joined the collective!'))
    else:
        flash(_('You are already a member of this collective!'))
    
    return redirect(url_for('group_view', group_id=group_id))

@app.route('/leave_group/<group_id>')
def leave_group(group_id):
    if 'username' not in session:
        flash(_('You must join the ranks first, Comrade!'))
        return redirect(url_for('login'))
    
    if group_id not in groups:
        flash(_('This collective does not exist, Comrade!'))
        return redirect(url_for('groups_list'))
    
    username = session['username']
    if username in group_memberships and group_id in group_memberships[username]:
        group_memberships[username].remove(group_id)
        flash(_('You have left the collective!'))
    else:
        flash(_('You are not a member of this collective!'))
    
    return redirect(url_for('groups_list'))

@app.route('/group_chat/<group_id>', methods=['GET', 'POST'])
def group_chat(group_id):
    if 'username' not in session:
        flash(_('You must join the ranks first, Comrade!'))
        return redirect(url_for('login'))
    
    if group_id not in groups:
        flash(_('This collective does not exist, Comrade!'))
        return redirect(url_for('groups_list'))
    
    username = session['username']
    # Check if user is a member of the group
    if username not in group_memberships or group_id not in group_memberships[username]:
        flash(_('You must join the collective to participate in discussions!'))
        return redirect(url_for('group_view', group_id=group_id))
    
    # Handle new message submission
    if request.method == 'POST':
        message_content = request.form.get('message', '')
        
        if message_content:
            # Create a new message
            message = {
                "id": f"msg_{secrets.token_hex(8)}",
                "author": username,
                "content": message_content,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            # Add message to the group chat
            if group_id not in group_messages:
                group_messages[group_id] = []
            
            group_messages[group_id].append(message)
            
            flash(_('Your message has been shared with the collective!'))
            # No redirect to stay on the chat page
    
    # Get all messages for this group
    messages = group_messages.get(group_id, [])
    group = groups[group_id]
    
    return render_template('group_chat.html', group=group, messages=messages)

@app.route('/profile')
def profile():
    if 'username' not in session:
        flash(_('You must join the ranks first, Comrade!'))
        return redirect(url_for('login'))
    
    user_data = users.get(session['username'], {})
    
    # Get the list of groups the user belongs to
    user_groups = []
    username = session['username']
    if username in group_memberships:
        for group_id in group_memberships[username]:
            if group_id in groups:
                user_groups.append(groups[group_id])
    
    return render_template('profile.html', username=session['username'], user_data=user_data, user_groups=user_groups)

@app.route('/edit_profile', methods=['GET', 'POST'])
def edit_profile():
    if 'username' not in session:
        flash(_('You must join the ranks first, Comrade!'))
        return redirect(url_for('login'))
    
    # Ensure upload directory exists
    try:
        upload_path = app.config['UPLOAD_FOLDER']
        os.makedirs(upload_path, exist_ok=True)
        logger.debug(f"In edit_profile: Upload directory path: {upload_path}")
        logger.debug(f"Directory exists: {os.path.exists(upload_path)}")
        logger.debug(f"Directory is writable: {os.access(upload_path, os.W_OK)}")
    except Exception as e:
        logger.error(f"Error ensuring upload directory exists: {str(e)}")
    
    username = session['username']
    if username not in users:
        flash(_('Comrade not found in our records!'))
        return redirect(url_for('logout'))
    
    user_data = users[username]
    
    if request.method == 'POST':
        # Update user information - Don't translate user-provided content
        users[username]['bio'] = request.form.get('bio', '')
        if not users[username]['bio']:
            users[username]['bio'] = _('A loyal comrade of the Party')
            
        users[username]['name'] = request.form.get('name', username)
        users[username]['email'] = request.form.get('email', '')
        users[username]['icon'] = request.form.get('icon', '☭')
        
        # Handle profile picture upload
        if 'profile_pic' in request.files:
            file = request.files['profile_pic']
            logger.debug(f"File uploaded: {file.filename if file else 'No file'}")
            
            if file and file.filename != '':
                if allowed_file(file.filename):
                    try:
                        # Generate a secure filename
                        filename = secure_filename(file.filename)
                        logger.debug(f"Secure filename: {filename}")
                        
                        # Add random string to ensure uniqueness
                        random_hex = secrets.token_hex(8)
                        base_name, file_ext = os.path.splitext(filename)
                        picture_filename = random_hex + file_ext
                        logger.debug(f"Generated filename: {picture_filename}")
                        
                        # Save the file - use the absolute path directly
                        file_path = os.path.join(app.config['UPLOAD_FOLDER'], picture_filename)
                        logger.debug(f"Trying to save file to: {file_path}")
                        
                        file.save(file_path)
                        logger.debug(f"File saved successfully to {file_path}")
                        logger.debug(f"File exists after save: {os.path.exists(file_path)}")
                        
                        # Store just the filename in the user data
                        users[username]['profile_pic'] = picture_filename
                        logger.debug(f"Updated user profile_pic to: {picture_filename}")
                    except Exception as e:
                        logger.error(f"Error saving file: {str(e)}")
                        flash(_('Error saving file: {error}').format(error=str(e)))
                else:
                    logger.warning(f"Invalid file type: {file.filename}")
                    flash(_('Comrade, only image files are allowed!'))
            else:
                logger.debug("No file or empty filename")
        else:
            logger.debug("No 'profile_pic' in request.files")
        
        flash(_('Your profile has been updated for the glory of the collective!'))
        return redirect(url_for('profile'))
    
    return render_template('edit_profile.html', username=username, user_data=user_data)

@app.route('/logout')
def logout():
    session.pop('username', None)
    flash(_('You have left the assembly, Comrade. Return soon!'))
    return redirect(url_for('index'))

@app.route('/music')
def music_library():
    if 'username' not in session:
        flash(_('You must join the ranks first, Comrade!'))
        return redirect(url_for('login'))
    
    search_query = request.args.get('search', '').lower()
    
    if search_query:
        filtered_music = [music for music in music_files if 
                         search_query in music['title'].lower() or 
                         search_query in music['artist'].lower() or 
                         (music['description'] and search_query in music['description'].lower())]
        return render_template('music.html', music_files=filtered_music)
    
    return render_template('music.html', music_files=music_files)

@app.route('/upload_music', methods=['POST'])
def upload_music():
    if 'username' not in session:
        flash(_('You must join the ranks first, Comrade!'))
        return redirect(url_for('login'))
    
    if 'music_file' not in request.files:
        flash(_('No music file selected for the revolution, Comrade!'))
        return redirect(url_for('music_library'))
    
    music_file = request.files['music_file']
    
    if music_file.filename == '':
        flash(_('No music file selected for the revolution, Comrade!'))
        return redirect(url_for('music_library'))
    
    title = request.form.get('title', '')
    artist = request.form.get('artist', '')
    description = request.form.get('description', '')
    
    if not title or not artist:
        flash(_('Title and artist are required for revolutionary music, Comrade!'))
        return redirect(url_for('music_library'))
    
    if music_file and allowed_music_file(music_file.filename):
        # Secure the filename
        original_filename = secure_filename(music_file.filename)
        filename_parts = original_filename.rsplit('.', 1)
        random_hex = secrets.token_hex(8)
        filename = f"{random_hex}.{filename_parts[1]}"
        
        # Save the file
        filepath = os.path.join(app.config['MUSIC_FOLDER'], filename)
        music_file.save(filepath)
        
        # Get the mimetype for audio playback
        mimetype = f"audio/{filename_parts[1]}"
        
        # Add to music library
        new_music = {
            'id': random_hex,
            'title': title,
            'artist': artist,
            'description': description,
            'filename': filename,
            'original_filename': original_filename,
            'mimetype': mimetype,
            'uploader': session['username'],
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        music_files.append(new_music)
        
        flash(_('Your revolutionary music has been shared with the collective!'))
        return redirect(url_for('music_library'))
    
    flash(_('Only .mp3, .wav, and .ogg files are allowed for revolutionary music!'))
    return redirect(url_for('music_library'))

@app.route('/gallery')
def gallery():
    if 'username' not in session:
        flash(_('You must join the ranks first, Comrade!'))
        return redirect(url_for('login'))
    
    search_query = request.args.get('search', '').lower()
    
    if search_query:
        filtered_images = [image for image in gallery_images if 
                         search_query in image['title'].lower() or 
                         search_query in image['author'].lower() or 
                         (image['description'] and search_query in image['description'].lower())]
        return render_template('gallery.html', gallery_images=filtered_images)
    
    return render_template('gallery.html', gallery_images=gallery_images)

@app.route('/upload_image', methods=['POST'])
def upload_image():
    if 'username' not in session:
        flash(_('You must join the ranks first, Comrade!'))
        return redirect(url_for('gallery'))
    
    if 'image_file' not in request.files:
        flash(_('No image file selected for the gallery, Comrade!'))
        return redirect(url_for('gallery'))
    
    image_file = request.files['image_file']
    
    if image_file.filename == '':
        flash(_('No image file selected for the gallery, Comrade!'))
        return redirect(url_for('gallery'))
    
    title = request.form.get('title', '')
    description = request.form.get('description', '')
    
    if not title:
        flash(_('Title is required for revolutionary images, Comrade!'))
        return redirect(url_for('gallery'))
    
    if image_file and allowed_file(image_file.filename):
        # Secure the filename
        original_filename = secure_filename(image_file.filename)
        filename_parts = original_filename.rsplit('.', 1)
        random_hex = secrets.token_hex(8)
        filename = f"{random_hex}.{filename_parts[1]}"
        
        # Save the file
        filepath = os.path.join(app.config['GALLERY_FOLDER'], filename)
        image_file.save(filepath)
        
        # Add to gallery
        image_id = random_hex
        new_image = {
            'id': image_id,
            'title': title,
            'description': description,
            'filename': filename,
            'author': session['username'],
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        gallery_images.append(new_image)
        gallery_comments[image_id] = []
        
        flash(_('Your revolutionary image has been shared with the collective!'))
        return redirect(url_for('gallery'))
    
    flash(_('Only image files are allowed for the revolutionary gallery!'))
    return redirect(url_for('gallery'))

@app.route('/gallery_image/<image_id>')
def gallery_image(image_id):
    if 'username' not in session:
        flash(_('You must join the ranks first, Comrade!'))
        return redirect(url_for('login'))
    
    # Find the image
    image = None
    for img in gallery_images:
        if img["id"] == image_id:
            image = img
            break
    
    if not image:
        flash(_('This image has been redistributed, Comrade!'))
        return redirect(url_for('gallery'))
    
    # Get the comments for this image
    comments = gallery_comments.get(image_id, [])
    
    return render_template('gallery_image.html', image=image, comments=comments)

@app.route('/add_gallery_comment/<image_id>', methods=['POST'])
def add_gallery_comment(image_id):
    if 'username' not in session:
        flash(_('You must join the ranks first, Comrade!'))
        return redirect(url_for('login'))
    
    # Check if the image exists
    image_exists = False
    for img in gallery_images:
        if img["id"] == image_id:
            image_exists = True
            break
    
    if not image_exists:
        flash(_('This image has been redistributed, Comrade!'))
        return redirect(url_for('gallery'))
    
    content = request.form.get('content', '')
    
    if not content:
        flash(_('Comments require content for the betterment of the collective!'))
        return redirect(url_for('gallery_image', image_id=image_id))
    
    # Create and add the comment
    comment_id = f"comment_{secrets.token_hex(8)}"
    comment = {
        "id": comment_id,
        "author": session['username'],
        "content": content,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    if image_id not in gallery_comments:
        gallery_comments[image_id] = []
    
    gallery_comments[image_id].append(comment)
    flash(_('Your comment has been added to the collective discourse!'))
    
    return redirect(url_for('gallery_image', image_id=image_id))

# Admin routes
@app.route('/admin')
def admin_panel():
    if 'username' not in session:
        flash(_('You must join the ranks first, Comrade!'))
        return redirect(url_for('login'))
    
    if not is_admin():
        flash(_('Only Party leaders can access this area, Comrade!'))
        return redirect(url_for('index'))
    
    return render_template('admin_panel.html', users=users, groups=groups, 
                          music_files=music_files, gallery_images=gallery_images)

@app.route('/admin/delete_user', methods=['POST'])
def delete_user():
    if 'username' not in session or not is_admin():
        flash(_('Only Party leaders can perform this action, Comrade!'))
        return redirect(url_for('index'))
    
    username = request.form.get('username')
    
    # Cannot delete admin or current user
    if username == 'admin' or username == session['username']:
        flash(_('This comrade cannot be removed!'))
        return redirect(url_for('admin_panel'))
    
    # Delete user
    if username in users:
        # Remove user from all groups
        if username in group_memberships:
            # No need to update groups themselves since they only track creator
            group_memberships.pop(username)
        
        # Delete user
        users.pop(username)
        flash(_('Comrade has been removed from the Party!'))
    else:
        flash(_('Comrade not found!'))
    
    return redirect(url_for('admin_panel'))

@app.route('/admin/delete_group', methods=['POST'])
def delete_group():
    if 'username' not in session or not is_admin():
        flash(_('Only Party leaders can perform this action, Comrade!'))
        return redirect(url_for('index'))
    
    group_id = request.form.get('group_id')
    
    if group_id in groups:
        # Remove group from all users' memberships
        for user, memberships in group_memberships.items():
            if group_id in memberships:
                memberships.remove(group_id)
        
        # Remove group messages
        if group_id in group_messages:
            group_messages.pop(group_id)
        
        # Remove group
        groups.pop(group_id)
        flash(_('Collective has been dissolved!'))
    else:
        flash(_('Collective not found!'))
    
    return redirect(url_for('admin_panel'))

@app.route('/admin/delete_music', methods=['POST'])
def delete_music():
    if 'username' not in session or not is_admin():
        flash(_('Only Party leaders can perform this action, Comrade!'))
        return redirect(url_for('index'))
    
    music_id = request.form.get('music_id')
    
    # Find and remove music file
    for i, music in enumerate(music_files):
        if music['id'] == music_id:
            # Delete the actual file
            try:
                file_path = os.path.join(app.config['MUSIC_FOLDER'], music['filename'])
                if os.path.exists(file_path):
                    os.remove(file_path)
            except Exception as e:
                logger.error(f"Error removing music file: {str(e)}")
            
            # Remove from list
            music_files.pop(i)
            flash(_('Revolutionary music has been removed!'))
            break
    else:
        flash(_('Music file not found!'))
    
    return redirect(url_for('admin_panel'))

@app.route('/admin/delete_image', methods=['POST'])
def delete_image():
    if 'username' not in session or not is_admin():
        flash(_('Only Party leaders can perform this action, Comrade!'))
        return redirect(url_for('index'))
    
    image_id = request.form.get('image_id')
    
    # Find and remove image
    for i, image in enumerate(gallery_images):
        if image['id'] == image_id:
            # Delete the actual file
            try:
                file_path = os.path.join(app.config['GALLERY_FOLDER'], image['filename'])
                if os.path.exists(file_path):
                    os.remove(file_path)
            except Exception as e:
                logger.error(f"Error removing image file: {str(e)}")
            
            # Remove from list
            gallery_images.pop(i)
            
            # Remove comments
            if image_id in gallery_comments:
                gallery_comments.pop(image_id)
            
            flash(_('Revolutionary image has been removed!'))
            break
    else:
        flash(_('Image not found!'))
    
    return redirect(url_for('admin_panel'))

if __name__ == '__main__':
    app.run(debug=True) 