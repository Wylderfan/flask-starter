from flask import Blueprint, render_template, redirect, url_for, request, flash
from app import db
from app.models import Item
from app.utils.helpers import current_profile

items_bp = Blueprint("items", __name__)


@items_bp.route("/")
def index():
    profile = current_profile()
    items = Item.query.filter_by(profile_id=profile).order_by(Item.created_at.desc()).all()
    return render_template("items/index.html", items=items)


@items_bp.route("/add", methods=["GET", "POST"])
def add():
    if request.method == "POST":
        profile = current_profile()
        name = request.form.get("name", "").strip()
        if not name:
            flash("Name is required.", "error")
            return redirect(url_for("items.add"))

        item = Item(profile_id=profile, name=name)
        db.session.add(item)
        try:
            db.session.commit()
            flash(f"'{item.name}' added.", "success")
            return redirect(url_for("items.index"))
        except Exception:
            db.session.rollback()
            flash("Something went wrong. Please try again.", "error")
            return redirect(url_for("items.add"))

    return render_template("items/add.html")


@items_bp.route("/<int:item_id>/edit", methods=["GET", "POST"])
def edit(item_id):
    profile = current_profile()
    item = Item.query.filter_by(id=item_id, profile_id=profile).first_or_404()

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        if not name:
            flash("Name is required.", "error")
            return redirect(url_for("items.edit", item_id=item_id))

        item.name = name
        try:
            db.session.commit()
            flash(f"'{item.name}' updated.", "success")
            return redirect(url_for("items.index"))
        except Exception:
            db.session.rollback()
            flash("Something went wrong. Please try again.", "error")
            return redirect(url_for("items.edit", item_id=item_id))

    return render_template("items/edit.html", item=item)


@items_bp.route("/<int:item_id>/delete", methods=["POST"])
def delete(item_id):
    profile = current_profile()
    item = Item.query.filter_by(id=item_id, profile_id=profile).first_or_404()
    name = item.name
    db.session.delete(item)
    try:
        db.session.commit()
        flash(f"'{name}' deleted.", "success")
    except Exception:
        db.session.rollback()
        flash("Could not delete the item. Please try again.", "error")
    return redirect(url_for("items.index"))
