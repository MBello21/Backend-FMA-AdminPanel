from flask import Flask, request, jsonify, url_for, Blueprint, current_app
from sqlalchemy import select, func
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required
from api.models import db, Meteorological, Recommendation, Users, WorkRecommendation


api = Blueprint('api', __name__)


@api.route('/health', methods=['GET'])
def get_health():
    return jsonify({'msg': 'ok'}), 200


@api.route('/sign-up', methods=['POST'])
def signup():
    data = request.get_json()

    required_field = ['firstname', 'lastname', 'email', 'category', 'password']
    missing = [req for req in required_field if not data.get(req)]

    if missing:
        return jsonify({'error': 'All fields are required'}), 400

    user_exist = db.session.execute(select(Users).where(
        Users.email == data.get('email'))).scalar_one_or_none()

    if user_exist:
        return jsonify({'error': 'User already exist'}), 400

    new_user = Users(
        firstname=data.get('firstname'),
        lastname=data.get('lastname'),
        email=data.get('email'),
        category=data.get('category'),
    )
    new_user.generate_hash(data.get('password'))
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'msg': 'User created succesfully'}), 200


@api.route('/signin', methods=['POST'])
def signin():
    data = request.get_json()

    required_field = ['email', 'password']
    missing = [req for req in required_field if not data.get(req)]

    if missing:
        return jsonify({'error': 'All fields are required'}), 400

    user = db.session.execute(select(Users).where(
        Users.email == data.get('email'))).scalar_one_or_none()

    if user is None:
        return jsonify({'error': 'User does not exist'}), 400

    if user.check_password(data.get('password')):
        access_token = create_access_token(identity=str(user.id))
        return jsonify({'msg': 'Login success',
                        'token': access_token})
    else:
        return jsonify({'error': 'Invalid user or password'}), 401


@api.route('/user', methods=['GET'])
@jwt_required()
def get_user():
    user_id = get_jwt_identity()
    user = db.session.execute(select(Users).where(
        Users.id == int(user_id))).scalar_one_or_none()

    if not user:
        return jsonify({'error': 'Not found'}), 404
    return jsonify(user.serialize()), 200


@api.route('/recommendations', methods=['GET'])
@jwt_required()
def get_recommendations():
    result = Meteorological.query.all()
    return jsonify([f.serialize() for f in result]), 200


@api.route('/freak/<int:id>', methods=['GET'])
def get_freak(id):
    result = db.session.execute(select(
        Meteorological).where(Meteorological.id == id)).scalar_one_or_none()
    if not result:
        return jsonify({'error': 'Freak not found'}), 404
    return jsonify(result.serialize()), 200


@api.route('/recommendations', methods=['POST'])
@jwt_required()
def post_temperature():
    data = request.get_json()

    required_fields = ["freak", "cat", "title"]
    missing = [req for req in required_fields if not data.get(req)]

    if not data.get("recommendation_list"):
        missing.append("recommendation_list")

    if missing:
        return jsonify({'error': 'All fields are required'}), 400

    recommendations = data.get("recommendation_list")
    work_recommendations = data.get("work_recommendation_list", [])
    prohibition_recommendations = data.get("prohibition_list", [])
    new_meteorological = Meteorological(
        freak=data.get("freak", "temperatura"),
        cat=data.get("cat"),
        title=data.get("title"),
    )

    db.session.add(new_meteorological)
    db.session.commit()

    for recommendation in recommendations:
        new_recommendation = Recommendation(
            freak_id=new_meteorological.id,
            recommendation=recommendation
        )
        db.session.add(new_recommendation)
    for recommendation in work_recommendations:
        new_work_recommendation = WorkRecommendation(
            freak_id=new_meteorological.id,
            type='precaucion',
            work_recommendation=recommendation
        )
        db.session.add(new_work_recommendation)
    for recommendation in prohibition_recommendations:
        new_prohibition_recommendations = WorkRecommendation(
            freak_id=new_meteorological.id,
            type='prohibicion',
            work_recommendation=recommendation
        )
        db.session.add(new_prohibition_recommendations)
    db.session.commit()

    return jsonify({
        "msg": "Created successfully",
        "recommendation": new_meteorological.serialize()
    }), 201


@api.route('/freak/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_freak(id):
    freak = Meteorological.query.get(id)

    if freak is None:
        return jsonify({"error": "Freak not found"}), 400
    db.session.delete(freak)
    db.session.commit()

    return jsonify({"msg": "Freak deleted successfully"}), 200


@api.route("/recommendation/<int:id>", methods=["PATCH"])
@jwt_required()
def patch_recommendation(id):
    data = request.get_json()

    required_fields = ["new_recommendation"]
    missing = [req for req in required_fields if not data.get(req)]

    if missing:
        return jsonify({'error': 'All fields are required'}), 400

    recommendation = db.session.execute(select(Recommendation).where(
        Recommendation.id == id)).scalar_one_or_none()
    if not recommendation:
        return jsonify({"error": "Recommendation not found"}), 400
    recommendation.recommendation = data.get("new_recommendation")
    db.session.commit()

    return jsonify({"msg": "ok"}), 200


@api.route('/recommendation/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_recommendation(id):
    recommendation = Recommendation.query.get(id)

    if recommendation is None:
        return jsonify({"error": "Recommendation not found"}), 400
    db.session.delete(recommendation)
    db.session.commit()

    return jsonify({"msg": "Recommendation deleted successfully"}), 200
