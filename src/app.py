from dotenv import load_dotenv
from flask import Flask, request, jsonify
from src.config import load_config
from src.controllers.statistics_controller import stats_blueprint
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from sqlalchemy.exc import OperationalError
from src.models import viewCustomers, viewInteractions, User, Type, Occupation, Customer
from src.db import db
from werkzeug.security import generate_password_hash, check_password_hash
import re
import Levenshtein

load_dotenv()

def create_app(testing=False):
    try:
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
        current_user = get_jwt_identity()
        user = User.query.filter_by(username=current_user).first()

        params = request.args.to_dict()
        page = int(params.pop('page', 1))
        page_size = int(params.pop('page_size', 1000))

        response, status_code = fetch_customers(user, params, page, page_size)
        return jsonify(response), status_code
        
    def fetch_customers(user, params, page, page_size):
        try:
            permissions = user.permissions
            if not permissions.get("read_all") == "X" and not "R" in permissions.get("get_customers"):
                return {'message': 'User has insufficient permissions for this endpoint/method'}, 403

            # Fetch customers
            if params:
                customers = viewCustomers.query.filter_by(**params).all()
            else:
                customers = viewCustomers.query.all()  # Get all customers if no filters

            result = [customer.as_dict() for customer in customers]
            response = enrichResponse(result, page, page_size)
            return response, 200
        except OperationalError as e:
            return {"error": str(e.orig)}, 500
        except Exception as e:
            return {'error': str(e)}, 500

    @app.route('/api/v1/customers', methods=['POST'])
    @jwt_required()
    def create_customers():
        try:
            current_user = get_jwt_identity()
            user = User.query.filter_by(username=current_user).first()
            permissions = user.permissions

            if not permissions.get("write_all") == "X" and not "W" in permissions.get("create_customers"):
                return jsonify({'message': 'User has insufficient permissions for this endpoint/method'}), 403
            
            customer_name = request.json.get('customer_name')
            customer_occupation = request.json.get('occupation_name')
            customer_type = request.json.get('type_name')
            
            customer_name = remove_non_ascii(customer_name)
            customer_occupation = remove_non_ascii(customer_occupation)
            customer_type = remove_non_ascii(customer_type)

            types = Type.query.all()
            type_names = [type.type_name for type in types]
            customer_type = find_closest_entry(type_names, customer_type)
            type_id = Type.query.filter_by(type_name=customer_type).first().id_customer_type
            if not type_id:
                type_id = create_type(customer_type)

            occupations = Occupation.query.all()
            occupation_names = [occupation.occupation_name for occupation in occupations]
            customer_occupation = find_closest_entry(occupation_names, customer_occupation)
            occupation_id = Occupation.query.filter_by(occupation_name=customer_occupation).first().id_customer_occupation
            if not occupation_id:
                occupation_id = create_occupation(customer_occupation)

            new_customer_id = create_customer(type_id, customer_name, occupation_id)
            params = {"id_customer": new_customer_id}
            customer_response = viewCustomers.query.filter_by(**params).all()
            result = [customer.as_dict() for customer in customer_response]
            response = enrichResponse(result)

            return jsonify(response)
        except OperationalError as e:
            return jsonify({"error": str(e.orig)}), 500
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/v1/interactions/', defaults={'id_customer': None}, methods=['GET'])
    @app.route('/api/v1/interactions/<int:id_customer>', methods=['GET'])
    @jwt_required()
    def get_interactions(id_customer):
        try:
            current_user = get_jwt_identity()
            user = User.query.filter_by(username=current_user).first()
            permissions = user.permissions
            
            if not permissions.get("read_all") == "X" and not "R" in permissions.get("get_interactions"):
                return jsonify({'message': 'User has insufficient permissions for this endpoint/method'}), 403

            params = request.args.to_dict()
            page = int(params.pop('page', 1))
            page_size = int(params.pop('page_size', 1000))

            if id_customer:
                params_user = {'id_customer': id_customer}
                response, status_code = fetch_customers(user, params_user, 1, 1)
                id_customer_type = response['data'][0]['id_customer_type']
                interactions = viewInteractions.query.filter_by(id_customer_type=id_customer_type).all()
                result = [interaction.as_dict() for interaction in interactions]
                result[0]["customer_id"] = id_customer
            else:
                interactions = viewInteractions.query.all()
                result = [interaction.as_dict() for interaction in interactions]

            response = enrichResponse(result, page, page_size)
            return jsonify(response)
        except OperationalError as e:
            return jsonify({'error': str(e.orig)}), 500
        except Exception as e:
            return jsonify({'error': str(e)}), 500
        
    def create_type(type_name):
        new_type = Type(type_name=type_name)
        db.session.add(new_type)
        db.session.commit()

        return new_type.id_customer_type
    
    def create_occupation(occupation_name):
        new_occupation = Occupation(occupation_name=occupation_name)
        db.session.add(new_occupation)
        db.session.commit()

        return new_occupation.id_customer_occupation
    
    def create_customer(id_customer_type,customer_name,id_customer_occupation):
        new_customer = Customer(
            id_customer_type=id_customer_type,
            customer_name=customer_name,
            id_customer_occupation=id_customer_occupation)
        db.session.add(new_customer)
        db.session.commit()

        return new_customer.id_customer
    
    def scale_down_list(elements, page, page_size):
        try:
            start_index = (page - 1) * page_size
            paginated_elements = elements[start_index:start_index + page_size]
            return paginated_elements
        except Exception as e:
            print(f"scale_down_list failed: {e}")

    def remove_non_ascii(string):
        return re.sub(r'[^\x00-\x7F]', '', string)

    def find_closest_entry(all_entries, new_entry):
        for entry in all_entries:
            if Levenshtein.distance(entry.lower(), new_entry.lower()) < 2:
                return entry
        return new_entry

    def enrichResponse(query, page=1, page_size=1):
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
