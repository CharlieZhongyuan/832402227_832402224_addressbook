import os
from flask import Flask, request, jsonify, send_file, send_from_directory
from flask_cors import CORS
from src.database import init_db, get_all_contacts, add_contact, update_contact, delete_contact, toggle_favorite
from src.excel_utils import export_to_excel, import_from_excel

app = Flask(__name__, static_folder="../static", static_url_path="")
CORS(app)

init_db()

@app.route("/")
def index():
    return send_from_directory(app.static_folder, "index.html")

@app.route("/api/contacts", methods=["GET"])
def list_contacts():
    return jsonify({"success": True, "contacts": get_all_contacts()})

@app.route("/api/contacts", methods=["POST"])
def create_contact():
    data = request.get_json()
    name = data.get("name", "").strip()
    if not name:
        return jsonify({"success": False, "message": "姓名不能为空"}), 400
    methods = data.get("methods", [])
    new_id = add_contact(name, methods)
    return jsonify({"success": True, "id": new_id}), 201

@app.route("/api/contacts/<int:contact_id>", methods=["PUT"])
def edit_contact(contact_id):
    data = request.get_json()
    name = data.get("name", "").strip()
    methods = data.get("methods", [])
    update_contact(contact_id, name, methods)
    return jsonify({"success": True})

@app.route("/api/contacts/<int:contact_id>", methods=["DELETE"])
def remove_contact(contact_id):
    delete_contact(contact_id)
    return jsonify({"success": True})

@app.route("/api/contacts/<int:contact_id>/favorite", methods=["PATCH"])
def fav_contact(contact_id):
    toggle_favorite(contact_id)
    return jsonify({"success": True})

@app.route("/api/export", methods=["GET"])
def export_excel():
    buffer = export_to_excel()
    return send_file(
        buffer,
        as_attachment=True,
        download_name="contacts.xlsx",
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

@app.route("/api/import", methods=["POST"])
def import_excel():
    if "file" not in request.files:
        return jsonify({"success": False, "message": "没有收到文件"}), 400
    file = request.files["file"]
    content = file.read()
    try:
        count = import_from_excel(content)
        return jsonify({"success": True, "imported": count})
    except Exception as e:
        return jsonify({"success": False, "message": f"导入失败: {str(e)}"}), 400

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
