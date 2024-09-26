from flask import Blueprint, current_app, jsonify
from ..factory import get_statistics_repository


stats_blueprint = Blueprint("stats_blueprint", __name__)

@stats_blueprint.route("/api/v1/stats/<table_name>", methods=["GET"])
def table_count(table_name):
    stats_repo = get_statistics_repository(current_app.config)
    if stats_repo.check_table_name(table_name):
        row = stats_repo.get_number_of_rows(table_name)
        return jsonify({"message": "Number of Rows", "rows": row}), 200
    return jsonify({"message": "Table name not found"}), 404
