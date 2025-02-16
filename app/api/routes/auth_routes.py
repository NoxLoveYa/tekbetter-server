import re
import time

from flask import request

from app.models.Student import Student
from app.services.student_service import StudentService
from app.tools.jwt_engine import generate_jwt
from app.tools.password_tools import check_password


def load_auth_routes(app):
    @app.route("/api/auth/email", methods=["POST"])
    def login_with_email_route():
        data = request.json
        email = data.get("email")

        if email is None:
            return {"error": "Missing email"}, 400

        student = StudentService.get_student_by_login(email)
        if student is None:
            ticket = StudentService.create_register_ticket(email)
            return {"status": "register"}, 200

        return {"status": "login"}, 200

    @app.route("/api/auth/login", methods=["POST"])
    def validate_email_login():
        data = request.json
        email = data.get("email")
        password = data.get("password")

        if email is None or password is None:
            return {"error": "Missing email or password"}, 400

        student = StudentService.get_student_by_login(email)
        if student is None:
            return {"error": "Invalid email or password"}, 400

        if not check_password(password, student.password_hash):
            return {"error": "Invalid email or password"}, 400

        token = StudentService.generate_jwt_token(student)
        return {"token": token}, 200

    @app.route("/api/auth/register", methods=["POST"])
    def register_student():
        data = request.json

        ticket = data.get("ticket", None)
        if ticket is None:
            return {"error": "Missing ticket"}, 400
        password = data.get("password", None)
        # 8 characters, 1 uppercase, 1 lowercase, 1 digit
        regex = "^(?=.*\d)(?=.*[a-z])(?=.*[A-Z]).{8,}$"
        if password is None or not re.match(regex, password):
            return {"error": "Invalid password"}, 400

        student = StudentService.create_student_by_ticket(ticket, password)
        if student is None:
            return {"error": "Invalid ticket"}, 400

        token = StudentService.generate_jwt_token(student)
        return {"token": token}, 200

    @app.route("/api/auth/ticket", methods=["POST"])
    def check_ticket():
        data = request.json
        ticket = data.get("ticket", None)
        if ticket is None:
            return {"error": "Missing ticket"}, 400

        user = StudentService.get_ticket_email(ticket)
        if user is None:
            return {"error": "Invalid ticket"}, 400

        return {"login": user}, 200
