from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
import os, random

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///moods.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Models
class Mood(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text)
    image_url = db.Column(db.String(255))
    mood_id = db.Column(db.Integer, db.ForeignKey('mood.id'))
    mood = db.relationship('Mood', backref=db.backref('posts', lazy=True))
    likes = db.Column(db.Integer, default=0)

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    post = db.relationship('Post', backref=db.backref('comments', lazy=True))

# Captions
CAPTIONS = {
    "Happy": [
         "Happiness is contagious 😄",
        "Be the reason someone smiles today 😊",
        "Positive vibes only ✨",
        "Keep shining and spreading joy 💫",
        "Smiles are free but priceless 😊",
        "Joy is the simplest form of gratitude 🌟",
        "Sunshine mixed with a little bit of smile ☀️",
        "Laugh louder, live brighter 😍",
        "Smile big, worry small 🌈",
        "Good vibes, good life ✌️",
        "Smiling through life’s little moments 💛",
        "Happiness looks good on you 😉",
        "Your vibe attracts your tribe 🧡",
        "Choose happiness, always 🌼",
        "Radiate positivity 🔆"
    ],
    "Sad": [
        "It's okay to not be okay 💙",
        "Every storm runs out of rain 🌧️",
        "Tears are words the heart can't say 💧",
        "Healing takes time, and that's okay 🌱"
        "Tough times never last, but tough people do 💪",
        "Every storm runs out of rain 🌧️➡️🌤️",
        "You are stronger than you think ✨",
        "It's okay to not be okay 🤍",
        "This too shall pass ⏳",
        "Pain is real, but so is hope 🌱",
        "One step at a time, you'll get there 🚶",
        "Your story isn't over yet... 💫",
        "Even the darkest night will end and the sun will rise 🌅",
        "Let your struggle become your strength 🔥",
        "Don't give up, great things take time ⏰",
        "Healing takes time, and that’s okay 🕊️",
        "Keep going, brighter days are coming 🌈",
        "Sometimes you just need to rest, not quit 🌸",
        "Rise above the storm and you will find the sunshine ☀️"
    ],
    "Angry": [
        "Breathe in peace, breathe out anger 🔥",
        "Channel your energy, not your rage ⚡",
        "Even the hottest fire cools with time 🔥➡️🧊"
        "Take a breath. Reset. Refocus 😤➡️😌",
        "Let it go, not worth your peace ☁️",
        "Anger doesn't solve, calm does 🌊",
        "Turn the anger into ambition 🔥",
        "Silence is better than unnecessary words 🤫",
        "Walk away, grow stronger 🚶‍♂️💪",
        "Don’t react. Respond wisely 🧠",
        "Let your energy build, not burn ⚡",
        "Pause. It's power. 🛑",
        "Stay grounded, not heated 🌿"
    ],
    "Calm": [
        "Inhale peace, exhale stress 🌿",
        "Still waters run deep 🧘",
        "Serenity is the new power 🌸"
        "Peace begins with a deep breath 🌬️",
        "Inhale peace, exhale chaos ☁️➡️✨",
        "Stillness speaks loudest 🌊",
        "Just flowing, not forcing 🌿",
        "Find peace in the now 🧘",
        "Soft mind, strong soul 💆‍♂️",
        "Serenity in simplicity 🍃",
        "Floating through moments like clouds ☁️",
        "Quiet mind, beautiful life 🌸",
        "Calm is a superpower 🧠"
    ],
    "Anxious": [
        "One step at a time, you're doing fine 💫",
        "Breathe deeply, you're not alone 🤍",
        "You're stronger than your anxiety 🌈"
        "It's okay to feel it. Just don't let it stay 💭➡️🌤️",
        "One thought at a time 🧩",
        "You’ve made it through 100% of your bad days 🌈",
        "Breathe. You are doing fine 🌬️💚",
        "Progress, not perfection 🚶",
        "Anxiety lies. You are enough 🤍",
        "Small steps every day matter 👣",
        "You are not your thoughts 🧠",
        "Healing is not linear 💫",
        "Feel it. Heal it. Let it go 🌊"
    ],
    "Excited": [
        "Let the excitement lead the way! 🚀",
        "Dream big. Start now. 🤩",
        "Chase your passion with fire 🔥"
        "Can’t keep calm, big things ahead! 🚀",
        "Smiling for no reason and I love it 😁",
        "Good vibes overload 🔥",
        "Adventure begins now! 🧭",
        "Too excited to sit still 💃",
        "Life feels like confetti today 🎊",
        "This energy is unmatched ⚡",
        "Chasing dreams with a grin 🌟",
        "Hype mode: ON 🔛",
        "Heart racing, in the best way 💓"
    ],
    "Tired": [
        "Rest is productive too 😴",
        "Take it slow, you're doing great 💤",
        "Refuel and rise again 🔋"
        "Running low, recharging now 🔋",
        "Some days are just… heavy 💤",
        "Still standing, even when tired 💪",
        "Rest is part of the process 🧸",
        "Not lazy, just low battery ⚠️",
        "Tired but not giving up ✨",
        "Powering down for a reset 🌙",
        "Nap > everything rn 😴",
        "Even warriors need rest 🛌",
        "Mental exhaustion is real. Be kind 🧠"
    ],
    "Bored": [
        "Try something new today 🔄",
        "Even boredom has beauty 🎨",
        "A spark of curiosity can light up the day ✨""Boredom level: expert 🧠💤",
        "If boredom was a sport, I’d win 🥇",
        "Send help. Or snacks. Or memes. 📱",
        "Brain buffering... ⏳",
        "Plot twist: nothing happened 😶",
        "Staring into space like it’ll answer me 🪐",
        "Yawn. Repeat. ☕",
        "Currently available for adventure 📞",
        "Need drama. Even from the cat 🐱",
        "Existential crisis? Or just bored again? 🤷"
    ]
}

# Initialize database
def init_db(reset=False):
    db.create_all()

    if reset:
        Comment.query.delete()
        Post.query.delete()
        Mood.query.delete()
        db.session.commit()

    if not Mood.query.first():
        moods = ['Happy', 'Sad', 'Angry', 'Calm', 'Anxious', 'Excited', 'Tired', 'Bored']
        for m in moods:
            mood_obj = Mood(name=m)
            db.session.add(mood_obj)
            db.session.flush()

            folder_path = os.path.join('static/dataset', m.lower())
            if os.path.exists(folder_path):
                image_files = [
                    f'dataset/{m.lower()}/{file}'
                    for file in os.listdir(folder_path)
                    if file.lower().endswith(('.jpg', '.jpeg', '.png', '.gif'))
                ]

                caption_list = CAPTIONS.get(m, ["Feeling something..."])
                for idx, img in enumerate(image_files):
                    caption = caption_list[idx % len(caption_list)]
                    db.session.add(Post(
                        title=f"{m} Image {idx+1}",
                        content=caption,
                        image_url=img,
                        mood_id=mood_obj.id
                    ))

        db.session.commit()

# Run init
with app.app_context():
    init_db(reset=True)  # पुढच्या वेळेला reset=False ठेवा

# Routes
@app.route('/')
def home():
    moods = Mood.query.all()
    return render_template('home.html', moods=moods)

@app.route('/mood/<mood_name>')
def mood_feed(mood_name):
    mood = Mood.query.filter_by(name=mood_name.capitalize()).first_or_404()
    emoji_dict = {
        "Happy": "😄", "Sad": "😢", "Angry": "😠", "Calm": "😌",
        "Anxious": "😰", "Excited": "🤩", "Tired": "😴", "Bored": "😐"
    }
    emoji = emoji_dict.get(mood.name, "🌀")
    posts = Post.query.filter_by(mood_id=mood.id).all()
    return render_template('mood_feed.html', mood=mood, posts=posts, emoji=emoji)

@app.route('/like/<int:post_id>', methods=['POST'])
def like_post(post_id):
    post = Post.query.get_or_404(post_id)
    post.likes += 1
    db.session.commit()
    return jsonify({'likes': post.likes})

@app.route('/comment/<int:post_id>', methods=['POST'])
def add_comment(post_id):
    data = request.get_json()
    comment_text = data.get('text', '').strip()
    if comment_text:
        comment = Comment(text=comment_text, post_id=post_id)
        db.session.add(comment)
        db.session.commit()
        return jsonify({'success': True, 'comment': comment.text})
    return jsonify({'success': False, 'error': 'Empty comment'}), 400

if __name__ == '__main__':
    app.run(debug=True, port=5008)
