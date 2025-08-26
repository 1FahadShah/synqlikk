from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from web.forms import LoginForm, RegisterForm
from web.models import create_user, get_user_by_username, get_user_by_email
import os

auth_bp = Blueprint("auth_bp", __name__, template_folder="templates")

DB_PATH = os.getenv("DB_PATH")

# =========================
# Register Route
# =========================
@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        username = form.username.data.strip()
        email = form.email.data.strip() if form.email.data else None
        password = form.password.data

        # Check if username or email already exists
        if get_user_by_username(DB_PATH, username):
            flash("Username already exists.", "danger")
            return render_template("register.html", form=form)

        if email and get_user_by_email(DB_PATH, email):
            flash("Email already registered.", "danger")
            return render_template("register.html", form=form)

        # Hash the password
        password_hash = generate_password_hash(password)

        # Create user
        user_id = create_user(DB_PATH, username, password_hash, email)
        flash("Account created successfully. Please login.", "success")
        return redirect(url_for("auth_bp.login"))

    return render_template("register.html", form=form)


# =========================
# Login Route
# =========================
@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data.strip()
        password = form.password.data

        user = get_user_by_username(DB_PATH, username)

        if user and check_password_hash(user["password_hash"], password):
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            flash(f"Welcome, {user['username']}!", "success")
            return redirect(url_for("main_bp.dashboard"))
        else:
            flash("Invalid username or password.", "danger")

    return render_template("login.html", form=form)


# =========================
# Logout Route
# =========================
@auth_bp.route("/logout")
def logout():
    session.clear()
    flash("Logged out successfully.", "success")
    return redirect(url_for("auth_bp.login"))
