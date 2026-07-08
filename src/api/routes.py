from flask import Flask, request, jsonify, url_for, Blueprint, current_app
from sqlalchemy import select, func
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required
from api.models import db, Meteorological, Recommendation, Users, WorkRecommendation, Alerts
from datetime import datetime
from datetime import date


api = Blueprint('api', __name__)

ALERTS_TO_RECOMMENDATIONS = {
    # AEMET oficiales
    'Temperatura máxima': 'temperatura',
    'Temperatura mínima': 'temperatura',
    'Rachas máximas': 'viento',
    'Viento': 'viento',
    'Lluvia': 'precipitacion',
    'Precipitación acumulada': 'precipitacion',
    'Tormentas': 'precipitacion',
    # Internas COEX
    'Viento máximo sostenido': 'viento',
    'Precipitación': 'precipitacion',
}
CATEGORIES_TO_RECOMMENDATIONS = {
    
    'amarillo': '3',
    'naranja': '4',
    'rojo': '5',
    'precaución (riesgo muy bajo)': '1',
    'precaución alta (riesgo bajo)': '2',
    'alerta amarilla (riesgo medio)': '3',
    'alerta naranja (riesgo alto)': '4',
    'alerta roja (riesgo muy alto)': '5',
}


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
        access_token = create_access_token(
            identity=str(user.id))
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

    freak = db.session.execute(select(Meteorological).where(
        Meteorological.id == id)).scalar_one_or_none()

    if not freak:
        return jsonify({"error": "Freak not found"}), 400

    freak.cat = data.get('cat')
    freak.title = data.get('title')

    for rec in freak.recommendation_list:
        db.session.delete(rec)

    for work_rec in freak.work_recommendation_list:
        db.session.delete(work_rec)

    for recommendation in data.get('recommendation_list', []):
        db.session.add(Recommendation(
            freak_id=id, recommendation=recommendation))
    for recommendation in data.get('work_recommendation_list', []):
        db.session.add(WorkRecommendation(
            freak_id=id, type='precaucion', work_recommendation=recommendation))
    for recommendation in data.get('prohibition_list', []):
        db.session.add(WorkRecommendation(
            freak_id=id, type='prohibicion', work_recommendation=recommendation))

    db.session.commit()

    return jsonify({'msg': 'Updated successfully', 'recommendation': freak.serialize()}), 200


@api.route('/recommendation/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_recommendation(id):
    recommendation = Recommendation.query.get(id)

    if recommendation is None:
        return jsonify({"error": "Recommendation not found"}), 400
    db.session.delete(recommendation)
    db.session.commit()

    return jsonify({"msg": "Recommendation deleted successfully"}), 200


@api.route('/alerts', methods=['POST'])
def post_alerts():
    data = request.get_json(silent=True)
    if data is None:
        return jsonify({'error': 'Invalid JSON'}), 400
    items = data.get('alertas') if isinstance(data, dict) else data
    if not isinstance(items, list) or not items:
        return jsonify({'error': 'It is waiting an alerts list'}), 400

    creadas = 0
    actualizadas = 0
    resultados = []

    for item in items:
        try:
            date_str = item.get("fecha") or date.today().isoformat()
            fecha = datetime.fromisoformat(date_str).date()
            zona = item.get("zona", "")[:120]
            parametro = item.get("parametro", "")[:120]
            origen = item.get("origen", "aemet")[:20]

            # Buscar si ya existe para hoy + zona + parametro + origen
            existente = Alerts.query.filter_by(
                date=fecha,
                zone=zona,
                parameter=parametro,
                origin=origen,
            ).first()

            if existente:
                existente.level = item.get("nivel", "")[:30]
                existente.description = item.get("descripcion", "")
                existente.start = (item.get("inicio") or "")[:8]
                existente.end = (item.get("fin") or "")[:8]
                existente.event = item.get("evento", "nueva")[:30]
                resultados.append(existente)
                actualizadas += 1
            else:
                alerta = Alerts(
                    zone=zona,
                    parameter=parametro,
                    level=item.get("nivel", "")[:30],
                    description=item.get("descripcion", ""),
                    start=(item.get("inicio") or "")[:8],
                    end=(item.get("fin") or "")[:8],
                    date=fecha,
                    origin=origen,
                    event=item.get("evento", "nueva")[:30],
                )
                db.session.add(alerta)
                resultados.append(alerta)
                creadas += 1
        except (ValueError, TypeError) as e:
            db.session.rollback()
            return jsonify({"error": f"Invalid alert: {e}"}), 400

    db.session.commit()
    return jsonify({
        "created": creadas,
        "updated": actualizadas,
        "alerts": [a.serialize() for a in resultados],
    }), 201


@api.route('/alerts', methods=['GET'])
def get_alerts():
    alert = Alerts.query

    date = request.args.get('date')

    if date:
        alert = alert.filter(Alerts.date == date)

    init = request.args.get('init')
    until = request.args.get('until')

    if init:
        alert = alert.filter(Alerts.date >= init)
    if until:
        alert = alert.filter(Alerts.date <= until)

    level = request.args.get('level')

    if level:
        alert = alert.filter(Alerts.level == level.lower())

    alerts = alert.order_by(Alerts.created_at.desc()).limit(200).all()
    return jsonify([a.serialize() for a in alerts]), 200


@api.route('/alerts/recommendation', methods=['GET'])
def get_alerts_with_recommendations():
    date = request.args.get('date')
    if not date:
        return jsonify({'error': 'date is required'}), 400

    alerts = Alerts.query.filter(Alerts.date == date).all()

    if not alerts:
        return jsonify([]), 200

    recommendations_needed = set()

    for alert in alerts:
        recommendation = ALERTS_TO_RECOMMENDATIONS.get(alert.parameter)
        if recommendation:
            recommendations_needed.add(recommendation)

    categories_needed = set()

    for alert in alerts:
        category = CATEGORIES_TO_RECOMMENDATIONS.get(alert.level)
        if category:
            categories_needed.add(category)

    meteo_data = Meteorological.query.filter(
        Meteorological.freak.in_(recommendations_needed), Meteorological.cat.in_(categories_needed)).all()

    meteo_data_by_alert = {}

    for meteo in meteo_data:
        meteo_data_by_alert[meteo.freak, meteo.cat] = meteo.serialize()

    data = []

    for alert in alerts:
        freak = ALERTS_TO_RECOMMENDATIONS.get(alert.parameter)
        cat = CATEGORIES_TO_RECOMMENDATIONS.get(alert.level)
        data.append({
            **alert.serialize(),
            "recommendations": meteo_data_by_alert.get((freak, cat))
        })
    return jsonify(data), 200
