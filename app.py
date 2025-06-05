from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///moods.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Database Models
class Mood(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)

# Initialize DB with default moods
def init_db():
    db.create_all()
    if not Mood.query.first():
        moods = ['Happy', 'Sad', 'Angry', 'Calm', 'Anxious', 'Excited', 'Tired', 'Bored']
        for m in moods:
            db.session.add(Mood(name=m))
        db.session.commit()

with app.app_context():
    init_db()

# Homepage - Mood selection
@app.route('/')
def home():
    moods = Mood.query.all()
    return render_template('home.html', moods=moods)

# Mood Feed Page
@app.route('/mood/<mood_name>')
def mood_feed(mood_name):
    mood = Mood.query.filter_by(name=mood_name.capitalize()).first_or_404()

    # Emoji dictionary
    emoji_dict = {
        "Happy": "😄",
        "Sad": "😢",
        "Angry": "😠",
        "Calm": "😌",
        "Anxious": "😰",
        "Excited": "🤩",
        "Tired": "😴",
        "Bored": "😐"
    }
    emoji = emoji_dict.get(mood.name, "🌀")  # fallback emoji

    # Image dataset path based on mood
    folder_path = os.path.join('static/dataset', mood.name.lower())
    if not os.path.exists(folder_path):
        return f"No images found for mood '{mood.name}'", 404

    # Fetch all image filenames
    image_files = [
        f'dataset/{mood.name.lower()}/{file}'
        for file in os.listdir(folder_path)
        if file.lower().endswith(('.jpg', '.jpeg', '.png', '.gif'))
    ]

    # Build post list
    posts = []
    for img in image_files:
        posts.append({
            'title': f"{mood.name} Image",
            'content': f"This image represents the {mood.name.lower()} mood.",
            'image_url': img
        })

    return render_template('mood_feed.html', mood=mood, posts=posts, emoji=emoji)

# App runner
if __name__ == '__main__':
    app.run(debug=True, port=5001)
