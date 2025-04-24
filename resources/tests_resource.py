from flask_restful import reqparse, abort, Api, Resource
from flask import jsonify
from data import db_session
from data.questions import Question

class TestsResource(Resource):
    def get(self):
        session = db_session.create_session()
        tests = session.query(Question).filter(Question.is_private == 0).all()
        return jsonify({
            'tests': [i.to_dict(only=('title', 'description', 'created_date')) for i in tests]
        })
