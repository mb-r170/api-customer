from dotenv import load_dotenv
from flask import Flask, request, jsonify
from .config import load_config
from .controllers.statistics_controller import stats_blueprint

from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from sqlalchemy.exc import OperationalError
from .db_handler import viewCustomers, viewInteractions, User
from .db import db
from werkzeug.security import generate_password_hash, check_password_hash
import re

load_dotenv()


def create_app(testing=False):
    try:
        #print(f"Creating app")
        app = Flask(__name__)
        app.register_blueprint(stats_blueprint)
        conf = load_config(testing)
        app.config.from_object(conf)
        db.init_app(app)

        jwt = JWTManager(app)

    except Exception as e:
        print(f"create_app erred: {str(e)}")

    #create an access token
    @app.route('/api/v1/login', methods=['POST'])
    def login():
        try:
            req = request.get_json()
            username = req['username']
            password = req['password']
            user = User.query.filter_by(username=username).first()

            if not user or not check_password_hash(user.password_hash, password):
                return jsonify({'message':  'System offline, try again later.'}), 503

            access_token = create_access_token(identity=username)
            return jsonify({'access_token': access_token})
        except Exception as e:
            print(f"login erred: {str(e)}")
            return jsonify({'message':  'System offline, try again later.'}), 504

    #add new user, must be admin
    @app.route('/api/v1/register', methods=['POST'])
    @jwt_required()
    def register():
        try:
            current_user = get_jwt_identity()
            user = User.query.filter_by(username=current_user).first()
            permissions = user.permissions.get('admin', [])
            
            if 'X' not in permissions:
                return jsonify({'message': 'System offline, try again later.'}), 503

            username = request.json.get('username')
            password = request.json.get('password')
            permissions = request.json.get('permissions', {})

            # Check if username already exists
            if User.query.filter_by(username=username).first():
                return jsonify({'message': 'Username already exists'}), 409  

            # Hash password and create new user
            hashed_password = generate_password_hash(password)
            new_user = User(username=username, password_hash=hashed_password, permissions=permissions)
            db.session.add(new_user)
            db.session.commit()  

            return jsonify({'message': 'User registered successfully'})
        except Exception as e:
            return jsonify({'error': str(e)}), 500


    @app.route('/api/v1/customers', methods=['GET'])
    @jwt_required()
    def get_customers():
        try:
            current_user = get_jwt_identity()
            user = User.query.filter_by(username=current_user).first()
            permissions = user.permissions.get('get_customers', [])

            if 'R' not in permissions:
                return jsonify({'message': 'User has insufficient permissions for this endpoint/method'}), 403
    
            params = request.args.to_dict()
            #print(f"params: {params}")
            page = int(params.pop('page', 1))
            page_size = int(params.pop('page_size', 1000))

            if params:
                customers = viewCustomers.query.filter_by(**params).all()
            else:
                customers = viewCustomers.query.all()  # Get all customers if no filters
            result = [customer.as_dict() for customer in customers]            
            response = enrichResponse(result, page, page_size)
            return jsonify(response)
        except OperationalError as e:
            return jsonify({"error": str(e.orig)}), 500
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/v1/customers', methods=['POST'])
    @jwt_required()
    def create_customers():
        try:
            current_user = get_jwt_identity()
            user = User.query.filter_by(username=current_user).first()
            permissions = user.permissions.get('create_customers', [])

            if 'W' not in permissions:
                return jsonify({'message': 'User has insufficient permissions for this endpoint/method'}), 403
            
            customer_name = request.json.get('customer_name')
            customer_type = request.json.get('customer_type')
            customer_occupation = request.json.get('customer_occupation')


            response = {}
            return jsonify(response)
        except OperationalError as e:
            return jsonify({"error": str(e.orig)}), 500
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/v1/interactions/<int:customer_id>', methods=['GET'])
    @jwt_required()
    def get_interactions(customer_id=None):
        try:
            current_user = get_jwt_identity()
            user = User.query.filter_by(username=current_user).first()
            permissions = user.permissions.get('get_interactions', [])

            if 'R' not in permissions:
                return jsonify({'message': 'User has insufficient permissions for this endpoint/method'}), 403
            
            params = request.args.to_dict()
            page = int(params.pop('page', 1))
            page_size = int(params.pop('page_size', 1000))

            if customer_id:
                interactions = viewInteractions.query.filter_by(customer_id=customer_id).all()
            else:
                interactions = viewInteractions.query.all()

            result = [interaction.as_dict() for interaction in interactions]
            response = enrichResponse(result, page, page_size)
            return jsonify(response)
        except OperationalError as e:
            return jsonify({"error": str(e.orig)}), 500
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    def scale_down_list(elements, page, page_size):
        try:
            start_index = (page - 1) * page_size
            paginated_elements = elements[start_index:start_index + page_size]
            return paginated_elements
        except Exception as e:
            print(f"scale_down_list failed: {e}")

    def enrichResponse(query, page, page_size):
        try:
            total_count = len(query)
            result = scale_down_list(query,page,page_size)
            result_count = len(result)
            response = {
                'response_code': 200,
                'result_count': result_count,
                'page': page,
                'total_count': total_count,
                'data': result
            }
            return response
        except Exception as e:
            print(f"enrichResponse failed: {e}")

    return app
