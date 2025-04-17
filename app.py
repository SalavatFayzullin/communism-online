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
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}

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

# Create upload folder if it doesn't exist
try:
    upload_path = app.config['UPLOAD_FOLDER']
    os.makedirs(upload_path, exist_ok=True)
    logger.debug(f"Upload directory created/confirmed at: {upload_path}")
    logger.debug(f"Directory exists: {os.path.exists(upload_path)}")
    logger.debug(f"Directory is writable: {os.access(upload_path, os.W_OK)}")
except Exception as e:
    logger.error(f"Error creating upload directory: {str(e)}")

# Mock user database - in a real app, you would use a database
users = {}

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

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

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
                'profile_pic': None
            }
            flash(_('Welcome to the ranks, Comrade!'))
            session['username'] = username
            return redirect(url_for('profile'))
    
    return render_template('register.html')

@app.route('/profile')
def profile():
    if 'username' not in session:
        flash(_('You must join the ranks first, Comrade!'))
        return redirect(url_for('login'))
    
    user_data = users.get(session['username'], {})
    return render_template('profile.html', username=session['username'], user_data=user_data)

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

if __name__ == '__main__':
    app.run(debug=True) 