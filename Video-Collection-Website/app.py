from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash, abort, send_from_directory
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# import pandas as pd
# import numpy as np
import os, secrets, time

app = Flask(__name__, static_folder='static')

# UPLOAD_FOLDER = 'static' #'uploads'
# if not os.path.exists(UPLOAD_FOLDER):
#     os.makedirs(UPLOAD_FOLDER)
# app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

VIDEOS_DIR = 'videos'
if not os.path.exists(VIDEOS_DIR):
    os.makedirs(VIDEOS_DIR)

app.secret_key = secrets.token_hex(16) #'123'

# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///feedback.db'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////Users/eduardo/code/db/feedback'

app.config['SESSION_PERMANENT'] = False
app.config['SESSION_USE_SIGNER'] = True
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

# from flask_session import Session
# Session(app)

db = SQLAlchemy(app)

# class Feedback(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     score = db.Column(db.Integer, nullable=False)
#     comment = db.Column(db.Text, nullable=True)
#     timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class Participant(db.Model):
    __tablename__ = 'participant'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    date_of_birth = db.Column(db.Date, nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    pathology = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    # Relationship to videos
    videos = db.relationship('Video', backref='participant', lazy=True)

    # Relationship with user
    creator = db.relationship('User', backref='created_participants')

class Video(db.Model):
    __tablename__ = 'video'

    id = db.Column(db.Integer, primary_key=True)
    participant_id = db.Column(db.Integer, db.ForeignKey('participant.id'), nullable=False)
    url = db.Column(db.String(200), nullable=False)
    score = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    #participant = db.relationship('Participant', backref=db.backref('video', lazy=True))
    creator = db.relationship('User', backref='created_videos')

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

with app.app_context():
    db.create_all()

@app.route('/')
def index():
    return render_template('landing.html')

@app.route('/home')
def home():
    #return render_template('index.html')
    total_participants = Participant.query.count()
    total_videos = Video.query.count()
    return render_template('home.html', total_participants=total_participants, total_videos=total_videos)

@app.route('/instructions')
def instructions():
    return render_template('instructions.html')

@app.route('/record')
def record():
    participant_id = request.args.get('participant_id', default=None, type=int)
    participants = Participant.query.order_by(db.func.lower(Participant.name)).all()
    return render_template('record.html', participants=participants, selected_participant_id=participant_id)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'video' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    participant_id = request.form.get('participant_id')

    file = request.files['video']
    
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if file:
        current_timestamp = datetime.now().strftime("%Y%m%d%H%M%S") #int(time.time())
        filename = f"video_{participant_id}_{current_timestamp}.mp4"
        filepath = os.path.join(VIDEOS_DIR, filename)
        file.save(filepath)

        session['video_filename'] = filename
        session['participant_id'] = participant_id
        session['current_timestamp'] = current_timestamp

        #### filename = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        # timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        # filename = os.path.join(app.config['UPLOAD_FOLDER'], f'video_{timestamp}.mp4')
        # session['latest_video'] = filename

        #### file.save(filename)
        return jsonify({'success': 'File uploaded successfully'}), 200
    
@app.route('/preview')
def preview():
    video_filename = session.get('video_filename')
    participant_id = session.get('participant_id')

    if not video_filename or not participant_id:
        flash('Você precisa gravar um vídeo para acessar o preview', 'warning')
        return redirect(url_for('record'))

    participant = Participant.query.get(participant_id)
    participants = Participant.query.all()

    # print("Participant ID:", participant_id)

    return render_template('preview.html', video_filename=video_filename, participants=participants, participant=participant)
    # return render_template('preview.html') #, video_filename=latest_video)

@app.route('/videos/<filename>')
def uploaded_video(filename):
    return send_from_directory(VIDEOS_DIR, filename)

@app.route('/save_video', methods=['POST'])
def save_video():
    if request.method == 'POST':
        # Extract data from form
        participant_id = session.get('participant_id') #request.form['participant_id']
        score = request.form['score']
        comment = request.form['comment']
        video_filename = session.get('video_filename')
        timestamp = session.get('current_timestamp')
        print("session:", session.items())
        created_at = datetime.strptime(timestamp, "%Y%m%d%H%M%S") #datetime.fromtimestamp(timestamp)


        video = Video(
            participant_id=participant_id,
            url=video_filename,
            created_at=created_at, #datetime.utcfromtimestamp(current_timestamp),
            score=score,
            comment=comment,
            created_by=session['user_id']
        )

        db.session.add(video)
        db.session.commit()

        flash('Vídeo enviado com sucesso!', 'success')
        return redirect(url_for('list_videos'))

'''
        current_timestamp = int(time.time())

        # Generate unique filename using the timestamp
        filename = f"video_{participant_id}_{current_timestamp}.mp4"
        filepath = os.path.join(VIDEOS_DIR, filename)

        # Save video to filesystem
        # with open(filepath, 'wb') as f:
        #     f.write(video_data)  # Assuming video_data is the binary data of the video
        video_file = request.files.get('video_file')
        video_file.save(filepath)
        # url = filename

        # Save video details to database
        video = Video(
            participant_id=participant_id,
            url=filepath,
            created_at=datetime.utcfromtimestamp(current_timestamp),  # Use timestamp for created_at
            score=score,
            comment=comment
        )
        db.session.add(video)
        db.session.commit()

        flash('Video saved successfully!', 'success')
        return redirect(url_for('list_videos'))
'''


'''
@app.route('/save_feedback', methods=['POST'])
def save_feedback():
    if request.method == 'POST':
        # Extract data from form
        participant_id = '' #request.form['participant_id']
        score = request.form['score']
        comment = request.form['comment']

        url = ''

        # Create a new Feedback instance
        feedback = Feedback(score=score, comment=comment)
        video = Video(url=url, participant_id=participant_id, score=score, comment=comment)

        # Add and commit to database
        db.session.add(feedback)
        db.session.commit()

        db.session.add(video)
        db.session.commit()

        # You can return a success message or redirect to another page
        # flash('Enviado com sucesso!', 'success')
        # return redirect(url_for('index'))
        
        ###return render_template('index.html', message="Enviado com sucesso!")
        flash('Enviado com sucesso!', 'success')
        # return redirect(url_for('home'))
        return render_template('home.html')
'''




@app.route('/add_participant', methods=['GET', 'POST'])
def add_participant():
    if request.method == 'POST':
        # Extract data from the form
        name = request.form.get('name')
        date_of_birth = request.form.get('date_of_birth')
        date_of_birth_formatted = datetime.strptime(date_of_birth, '%Y-%m-%d').date()
        gender = request.form.get('gender')
        pathology = request.form.get('pathology')
        
        # Create a new participant instance
        participant = Participant(name=name, date_of_birth=date_of_birth_formatted, gender=gender, pathology=pathology, created_by=session['user_id'])
        
        # Save to database
        db.session.add(participant)
        db.session.commit()
        
        flash('Participante adicionado com sucesso!', 'success')
        # return redirect(url_for('list_participants'))
        return redirect(url_for('view_participant', id=participant.id))
        # return render_template('list_participants.html', message="Enviado com sucesso!")

    return render_template('add_participant.html')

@app.route('/participants')
def list_participants():
    # page = request.args.get('page', 1, type=int)
    # per_page = 10

    search = request.args.get('search')

    '''
    if search:
        # participants = Participant.query.filter(Participant.name.ilike(f'%{search}%')).all()
        participants = Participant.query.filter(Participant.name.ilike(f'%{search}%')).paginate(page=page, per_page=per_page, error_out=False)
    else:
        # participants = Participant.query.all()
        participants = Participant.query.paginate(page=page, per_page=per_page, error_out=False)
    '''

    query = db.session.query(
        Participant, 
        db.func.count(Video.id).label('video_count'),
        User.name.label('name')
    ).outerjoin(Video, Participant.id == Video.participant_id) \
     .outerjoin(User, Participant.created_by == User.id)

    if search:
        query = query.filter(Participant.name.ilike(f"%{search}%"))
    
    participants = query.group_by(Participant.id).all()

    # participants = Participant.query.all()
    # return render_template('list_participants.html', participants=participants)
    # return render_template('list_participants.html', participants=participants.items, pagination=participants, search_query=search)
    return render_template('list_participants.html', participants=participants)

''' # list_participants.html
<!-- Pagination controls -->

<p class="center-text pagination-title">Página{% if participants.pages > 1 %}s{% endif %}</p>
<div class="pagination">
    {% if participants.has_prev %}
        <a href="{{ url_for('list_participants', page=1) }}">Primeiro</a>
        <a href="{{ url_for('list_participants', page=participants.prev_num) }}">Anterior</a>
    {% endif %}
    
    {% if participants.page - 3 > 1 %}
        <a href="#">...</a>
    {% endif %}
    {% for p in range(participants.page - 2, participants.page + 3) %}
        {% if p > 0 and p <= participants.pages %}
            {% if p != participants.page %}
                <a href="{{ url_for('list_participants', page=p) }}">{{ p }}</a>
            {% else %}
                <strong>{{ p }}</strong>
            {% endif %}
        {% endif %}
    {% endfor %}
    {% if participants.page + 2 < participants.pages %}
        <a href="#">...</a>
    {% endif %}
    
    {% if participants.has_next %}
        <a href="{{ url_for('list_participants', page=participants.next_num) }}">Próximo</a>
        <a href="{{ url_for('list_participants', page=participants.pages) }}">Último</a>
    {% endif %}
</div>
'''

@app.route('/participant/<int:id>')
def view_participant(id):
    # participant = Participant.query.get(id)
    # if not participant:
    #     abort(404)
    participant = Participant.query.get_or_404(id)

    creator = User.query.get(participant.created_by)
    creator_name = creator.name if creator else "N/A"

    # videos = Video.query.filter_by(participant_id=id).all()

    videos = db.session.query(
        Video,
        User.name.label('creator_name')
    ).outerjoin(User, Video.created_by == User.id) \
     .filter(Video.participant_id == id).all()

    return render_template('view_participant.html', participant=participant, videos=videos, creator_name=creator_name)

@app.route('/participant/<int:id>/edit', methods=['GET', 'POST'])
def edit_participant(id):
    participant = Participant.query.get(id)
    if not participant:
        abort(404)
    if request.method == 'POST':
        participant.name = request.form['name']
        participant.date_of_birth = datetime.strptime(request.form['date_of_birth'], '%Y-%m-%d').date()
        participant.gender = request.form['gender']
        db.session.commit()
        flash('Participante atualizado com sucesso!', 'success')
        return redirect(url_for('view_participant', id=participant.id))
    return render_template('edit_participant.html', participant=participant)

@app.route('/participant/<int:id>/delete', methods=['POST'])
def delete_participant(id):
    participant = Participant.query.get(id)
    if not participant:
        abort(404)
    db.session.delete(participant)
    db.session.commit()
    flash('Participante deletado com sucesso!', 'warning')
    return redirect(url_for('list_participants'))

#<a href="{{ url_for('select_participant_for_recording') }}" class="action-btn">Record Video</a>
#<a href="{{ url_for('search') }}" class="action-btn">Search</a>



@app.route('/list_videos')
def list_videos():
    # videos = Video.query.all()

    videos = db.session.query(
        Video,
        User.name.label('name')
    ).outerjoin(User, Video.created_by == User.id).all() 

    return render_template('list_videos.html', videos=videos)



@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            session['user_id'] = user.id
            session['user_fullname'] = user.name
            session['username'] = user.username
            return redirect(url_for('home'))
        else:
            flash('Usuário ou senha inválidos', 'warning')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('username', None)

    flash('Usuário deslogado', 'warning')
    return redirect(url_for('index'))

@app.before_request
def require_login():
    allowed_routes = ['static', 'login', 'landing', 'index', '/']
    if 'user_id' not in session and request.endpoint not in allowed_routes:
        #return redirect(url_for('login'))

        flash('Você precisa estar logado para acessar essa página', 'warning')
        return render_template('landing.html')


if __name__ == "__main__":
    app.run(debug=True)
