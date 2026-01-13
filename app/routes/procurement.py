from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from app.extensions import db
from app.models.procurement_request import ProcurementRequest

procurement_bp = Blueprint("procurement", __name__, url_prefix="/procurement")


@procurement_bp.route("/")
@login_required
def index():
    requests_list = (
        ProcurementRequest.query
        .order_by(
            ProcurementRequest.is_urgent.desc(),
            ProcurementRequest.created_at.desc()
        )
        .all()
    )
    return render_template("procurement/index.html", requests=requests_list)


@procurement_bp.route("/create", methods=["GET", "POST"])
@login_required
def create():
    if request.method == "POST":
        item = request.form.get("item")
        quantity = request.form.get("quantity")
        amount = request.form.get("amount")

        # 🚨 URGENCY CHECKBOX
        is_urgent = True if request.form.get("is_urgent") == "on" else False
        is_urgent = bool(request)

        if not item or not quantity or not amount:
            flash("All fields are required.", "danger")
            return redirect(url_for("procurement.create"))

        new_request = ProcurementRequest(
            item=item,
            quantity=int(quantity),
            amount=amount,
            is_urgent=is_urgent
        )

        db.session.add(new_request)
        db.session.commit()

        flash(
            "Procurement request submitted"
            + (" (URGENT)" if is_urgent else ""),
            "success"
        )
        return redirect(url_for("procurement.index"))

    return render_template("procurement/create.html")
