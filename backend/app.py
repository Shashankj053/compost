from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
import pandas as pd
import json
from datetime import datetime, timedelta
import os

from database import db, init_db
from models import User, CompostingExperiment
from auth import hash_password, verify_password
from analysis import calculate_efficiency_score, generate_insights
from reports import generate_pdf_report

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///composting.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'your-jwt-secret-key'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)

# Initialize extensions
db.init_app(app)
CORS(app)
jwt = JWTManager(app)

# Initialize database
with app.app_context():
    init_db()

@app.route('/api/register', methods=['POST'])
def register():
    """Register a new user"""
    try:
        data = request.get_json()
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        
        if User.query.filter_by(username=username).first():
            return jsonify({'error': 'Username already exists'}), 400
            
        if User.query.filter_by(email=email).first():
            return jsonify({'error': 'Email already exists'}), 400
        
        hashed_password = hash_password(password)
        user = User(username=username, email=email, password_hash=hashed_password)
        db.session.add(user)
        db.session.commit()
        
        access_token = create_access_token(identity=username)
        return jsonify({'access_token': access_token, 'username': username}), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/login', methods=['POST'])
def login():
    """Login user"""
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        user = User.query.filter_by(username=username).first()
        if user and verify_password(password, user.password_hash):
            access_token = create_access_token(identity=username)
            return jsonify({'access_token': access_token, 'username': username}), 200
        
        return jsonify({'error': 'Invalid credentials'}), 401
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/experiments', methods=['POST'])
@jwt_required()
def add_experiment():
    """Add a new composting experiment"""
    try:
        data = request.get_json()
        username = get_jwt_identity()
        user = User.query.filter_by(username=username).first()
        
        # Calculate efficiency score
        efficiency_score = calculate_efficiency_score(data)
        
        experiment = CompostingExperiment(
            user_id=user.id,
            bin_id=data.get('bin_id'),
            cn_ratio=float(data.get('cn_ratio')),
            moisture_level=float(data.get('moisture_level')),
            aeration_frequency=int(data.get('aeration_frequency')),
            daily_temperature=float(data.get('daily_temperature')),
            odor_level=int(data.get('odor_level')),
            decomposition_days=int(data.get('decomposition_days')),
            final_n=float(data.get('final_n')),
            final_p=float(data.get('final_p')),
            final_k=float(data.get('final_k')),
            efficiency_score=efficiency_score
        )
        
        db.session.add(experiment)
        db.session.commit()
        
        return jsonify({'message': 'Experiment added successfully', 'id': experiment.id}), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/experiments', methods=['GET'])
@jwt_required()
def get_experiments():
    """Get all experiments for the current user"""
    try:
        username = get_jwt_identity()
        user = User.query.filter_by(username=username).first()
        
        experiments = CompostingExperiment.query.filter_by(user_id=user.id).all()
        
        result = []
        for exp in experiments:
            result.append({
                'id': exp.id,
                'bin_id': exp.bin_id,
                'cn_ratio': exp.cn_ratio,
                'moisture_level': exp.moisture_level,
                'aeration_frequency': exp.aeration_frequency,
                'daily_temperature': exp.daily_temperature,
                'odor_level': exp.odor_level,
                'decomposition_days': exp.decomposition_days,
                'final_n': exp.final_n,
                'final_p': exp.final_p,
                'final_k': exp.final_k,
                'efficiency_score': exp.efficiency_score,
                'date_created': exp.date_created.isoformat()
            })
        
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/experiments/<int:experiment_id>', methods=['DELETE'])
@jwt_required()
def delete_experiment(experiment_id):
    """Delete an experiment"""
    try:
        username = get_jwt_identity()
        user = User.query.filter_by(username=username).first()
        
        experiment = CompostingExperiment.query.filter_by(
            id=experiment_id, user_id=user.id
        ).first()
        
        if not experiment:
            return jsonify({'error': 'Experiment not found'}), 404
        
        db.session.delete(experiment)
        db.session.commit()
        
        return jsonify({'message': 'Experiment deleted successfully'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/analytics', methods=['GET'])
@jwt_required()
def get_analytics():
    """Get analytics data for dashboard"""
    try:
        username = get_jwt_identity()
        user = User.query.filter_by(username=username).first()
        
        experiments = CompostingExperiment.query.filter_by(user_id=user.id).all()
        
        if not experiments:
            return jsonify({'error': 'No experiments found'}), 404
        
        # Convert to DataFrame for analysis
        data = []
        for exp in experiments:
            data.append({
                'bin_id': exp.bin_id,
                'cn_ratio': exp.cn_ratio,
                'moisture_level': exp.moisture_level,
                'aeration_frequency': exp.aeration_frequency,
                'daily_temperature': exp.daily_temperature,
                'odor_level': exp.odor_level,
                'decomposition_days': exp.decomposition_days,
                'final_n': exp.final_n,
                'final_p': exp.final_p,
                'final_k': exp.final_k,
                'efficiency_score': exp.efficiency_score
            })
        
        df = pd.DataFrame(data)
        insights = generate_insights(df)
        
        return jsonify(insights), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/export', methods=['GET'])
@jwt_required()
def export_data():
    """Export data to CSV"""
    try:
        username = get_jwt_identity()
        user = User.query.filter_by(username=username).first()
        
        experiments = CompostingExperiment.query.filter_by(user_id=user.id).all()
        
        data = []
        for exp in experiments:
            data.append({
                'Bin ID': exp.bin_id,
                'C/N Ratio': exp.cn_ratio,
                'Moisture Level (%)': exp.moisture_level,
                'Aeration Frequency': exp.aeration_frequency,
                'Daily Temperature (°C)': exp.daily_temperature,
                'Odor Level': exp.odor_level,
                'Decomposition Days': exp.decomposition_days,
                'Final N': exp.final_n,
                'Final P': exp.final_p,
                'Final K': exp.final_k,
                'Efficiency Score': exp.efficiency_score,
                'Date Created': exp.date_created.strftime('%Y-%m-%d')
            })
        
        df = pd.DataFrame(data)
        filename = f'composting_data_{username}_{datetime.now().strftime("%Y%m%d")}.csv'
        filepath = os.path.join('exports', filename)
        
        os.makedirs('exports', exist_ok=True)
        df.to_csv(filepath, index=False)
        
        return send_file(filepath, as_attachment=True, download_name=filename)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/report', methods=['GET'])
@jwt_required()
def generate_report():
    """Generate PDF report"""
    try:
        username = get_jwt_identity()
        user = User.query.filter_by(username=username).first()
        
        experiments = CompostingExperiment.query.filter_by(user_id=user.id).all()
        
        if not experiments:
            return jsonify({'error': 'No experiments found'}), 404
        
        # Convert to DataFrame
        data = []
        for exp in experiments:
            data.append({
                'bin_id': exp.bin_id,
                'cn_ratio': exp.cn_ratio,
                'moisture_level': exp.moisture_level,
                'aeration_frequency': exp.aeration_frequency,
                'daily_temperature': exp.daily_temperature,
                'odor_level': exp.odor_level,
                'decomposition_days': exp.decomposition_days,
                'final_n': exp.final_n,
                'final_p': exp.final_p,
                'final_k': exp.final_k,
                'efficiency_score': exp.efficiency_score
            })
        
        df = pd.DataFrame(data)
        filename = generate_pdf_report(df, username)
        
        return send_file(filename, as_attachment=True, download_name=f'composting_report_{username}.pdf')
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/best-practices', methods=['GET'])
@jwt_required()
def get_best_practices():
    """Get best practices based on top 3 performing bins"""
    try:
        username = get_jwt_identity()
        user = User.query.filter_by(username=username).first()
        
        experiments = CompostingExperiment.query.filter_by(user_id=user.id)\
            .order_by(CompostingExperiment.efficiency_score.desc()).limit(3).all()
        
        if len(experiments) < 3:
            return jsonify({'error': 'Need at least 3 experiments for best practices'}), 400
        
        # Calculate averages of top 3
        avg_cn = sum(exp.cn_ratio for exp in experiments) / 3
        avg_moisture = sum(exp.moisture_level for exp in experiments) / 3
        avg_aeration = sum(exp.aeration_frequency for exp in experiments) / 3
        avg_temperature = sum(exp.daily_temperature for exp in experiments) / 3
        
        best_practices = {
            'optimal_cn_ratio': round(avg_cn, 1),
            'optimal_moisture': round(avg_moisture, 1),
            'optimal_aeration': round(avg_aeration),
            'optimal_temperature': round(avg_temperature, 1),
            'top_bins': [
                {
                    'bin_id': exp.bin_id,
                    'efficiency_score': exp.efficiency_score,
                    'decomposition_days': exp.decomposition_days
                } for exp in experiments
            ],
            'recommendations': [
                f"Maintain C/N ratio around {avg_cn:.1f} for optimal decomposition",
                f"Keep moisture level at {avg_moisture:.1f}% for best results",
                f"Aerate {avg_aeration:.0f} times per week",
                f"Target temperature around {avg_temperature:.1f}°C",
                "Monitor odor levels regularly and adjust aeration if needed"
            ]
        }
        
        return jsonify(best_practices), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)