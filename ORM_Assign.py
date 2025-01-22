# Task 1
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from marshmallow import fields
from marshmallow import ValidationError

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:amrit101!@localhost/FITNESS_CENTER_MANAGER'
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'connect_args': 
        {'use_pure': True
    }
}
db = SQLAlchemy(app)
ma = Marshmallow(app)

class MemberSchema(ma.Schema):
    name = fields.String(required=True)
    age = fields.Integer()

    class Meta:
        fields = ('name', 'age', 'id')

member_schema = MemberSchema()
members_schema = MemberSchema(many=True)

class WorkoutSchema(ma.Schema):
    session_date = fields.Date(required=True)
    session_time = fields.String(required=True)
    activity = fields.String(required=True)

    class Meta:
        fields = ('session_date', 'session_time', 'activity', 'member_id')

workout_schema = WorkoutSchema()
workouts_schema = WorkoutSchema(many=True)

class Members(db.Model):
    __tablename__ = 'members'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    age = db.Column(db.Integer)

class WorkoutSessions(db.Model):
    __tablename__ = 'WorkoutSessions'
    session_id = db.Column(db.Integer, primary_key=True, nullable=False)
    member_id = db.Column(db.Integer, db.ForeignKey('members.id'), nullable=False)
    session_date = db.Column(db.Date, nullable=False)
    session_time = db.Column(db.String(50), nullable=False)
    activity = db.Column(db.String(255), nullable=False)

#Task 2
@app.route("/")
def home():
    return "Welcome to Fitness Management System!"

@app.route('/members', methods=['POST'])
def add_members():
    try:
        member_data = member_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400
    
    new_member = Members(name=member_data['name'], age=member_data['age'])
    db.session.add(new_member)
    db.session.commit()
    return jsonify({"message": "New member added successfully"}), 201

@app.route('/members', methods=['GET'])
def get_members():
    members = Members.query.all()
    return members_schema.jsonify(members)

@app.route('/members/<int:id>', methods=['PUT'])
def update_members(id):
    member = Members.query.get_or_404(id)
    try:
        member_data = member_schema.load(request.json)
    except ValidationError as err:
        return jsonify (err.messages), 400

    member.name = member_data['name']
    member.age = member_data['age']

    db.session.commit()
    return jsonify({"Attention": "Member details have been updated successfully"}), 200

@app.route('/members/<int:id>', methods=['DELETE'])
def delete_members(id):
    member = Members.query.get_or_404(id)
    db.session.delete(member)
    db.session.commit()
    return jsonify({"Attention": "Member has been deleted successfully"})

#Task 3
@app.route('/WorkoutSessions', methods=['POST'])
def schedule_workouts():
    try:
        member_workouts = workout_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400

    workout_data = workout_schema.load(request.json)
    new_workout = WorkoutSessions(session_date = workout_data['session_date'], session_time = workout_data['session_time'], activity = workout_data['activity'], member_id = workout_data['member_id'] )
    db.session.add(new_workout)
    db.session.commit()
    return jsonify({"Attention": "New workout session has been added successfully"}), 201

@app.route('/WorkoutSessions/<int:member_id>', methods=['PUT'])
def update_workouts(member_id):
    workouts = WorkoutSessions.query.get_or_404(member_id)
    try:
        workout_data = workout_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400

    workouts.date = workout_data['session_date']
    workouts.time = workout_data['session_time']
    workouts.activity = workout_data['activity']

    db.session.commit()
    return jsonify({"Attention": "Workout details were succesfully updated"})

@app.route('/WorkoutSessions', methods=['GET'])
def display_workouts():
    workouts = WorkoutSessions.query.all()
    return workouts_schema.jsonify(workouts)

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)