from flask import Blueprint, render_template, request, session, redirect, current_app
from app.models import Item
from app.utils.helpers import current_profile

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def index():
    profile = current_profile()
    item_count = Item.query.filter_by(profile_id=profile).count()
    return render_template("main/index.html", item_count=item_count)


@main_bp.route("/switch-profile", methods=["POST"])
def switch_profile():
    profiles = current_app.config["PROFILES"]
    name = request.form.get("profile", "").strip()
    if name in profiles:
        session["profile"] = name
    return redirect(request.referrer or "/")
