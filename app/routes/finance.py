@finance_bp.route("/payments/create/<int:procurement_id>", methods=["GET", "POST"])
@login_required
def create_payment(procurement_id):
    from app.models import ProcurementRequest, Payment
    from app.extensions import db
    from datetime import datetime

    pr = ProcurementRequest.query.get_or_404(procurement_id)

    if request.method == "POST":
        payment = Payment(
            procurement_id=pr.id,
            amount=pr.amount,
            method=request.form.get("method"),
            reference=request.form.get("reference"),
            created_at=datetime.utcnow()
        )

        db.session.add(payment)
        db.session.commit()

        flash("Payment recorded successfully", "success")
        return redirect(url_for("finance.list_payments"))

    return render_template(
        "finance/create_payment.html",
        pr=pr
    )
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
finance_bp = Blueprint('finance', __name__)
from app.models import Payment
@finance_bp.route("/payments", methods=["GET"])
@login_required
def list_payments():
    from app.extensions import db

    payments = Payment.query.all()

    return render_template(
        "finance/list_payments.html",
        payments=payments
    )
from app.extensions import db
from app.models import Payment
@finance_bp.route("/payments/delete/<int:payment_id>", methods=["POST"])
@login_required
def delete_payment(payment_id):
    payment = Payment.query.get_or_404(payment_id)

    db.session.delete(payment)
    db.session.commit()

    flash("Payment deleted successfully", "success")
    return redirect(url_for("finance.list_payments"))
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
finance_bp = Blueprint('finance', __name__)         
from app.models import ProcurementRequest, Payment
from app.extensions import db
from datetime import datetime   
@finance_bp.route("/payments/edit/<int:payment_id>", methods=["GET", "POST"])
@login_required
def edit_payment(payment_id):
    payment = Payment.query.get_or_404(payment_id)

    if request.method == "POST":
        payment.method = request.form.get("method")
        payment.reference = request.form.get("reference")
        payment.updated_at = datetime.utcnow()

        db.session.commit()

        flash("Payment updated successfully", "success")
        return redirect(url_for("finance.list_payments"))

    return render_template(
        "finance/edit_payment.html",
        payment=payment
    )       
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
finance_bp = Blueprint('finance', __name__)
from app.models import ProcurementRequest, Payment
from app.extensions import db
from datetime import datetime
@finance_bp.route("/payments/view/<int:payment_id>", methods=["GET"])
@login_required
def view_payment(payment_id):
    payment = Payment.query.get_or_404(payment_id)

    return render_template(
        "finance/view_payment.html",
        payment=payment
    )
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
finance_bp = Blueprint('finance', __name__)
from app.models import ProcurementRequest, Payment
from app.extensions import db
from datetime import datetime
@finance_bp.route("/payments/create/<int:procurement_id>", methods=["GET", "POST"])
@login_required
def create_payment(procurement_id):
    pr = ProcurementRequest.query.get_or_404(procurement_id)

    if request.method == "POST":
        payment = Payment(
            procurement_id=pr.id,
            amount=pr.amount,
            method=request.form.get("method"),
            reference=request.form.get("reference"),
            created_at=datetime.utcnow()
        )

        db.session.add(payment)
        db.session.commit()

        flash("Payment recorded successfully", "success")
        return redirect(url_for("finance.list_payments"))

    return render_template(
        "finance/create_payment.html",
        pr=pr
    )
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
finance_bp = Blueprint('finance', __name__)
from app.models import ProcurementRequest, Payment
from app.extensions import db
from datetime import datetime
@finance_bp.route("/payments/create/<int:procurement_id>", methods=["GET", "    POST"])
@login_required
def create_payment(procurement_id):
    pr = ProcurementRequest.query.get_or_404(procurement_id)

    if request.method == "POST":
        payment = Payment(
            procurement_id=pr.id,
            amount=pr.amount,
            method=request.form.get("method"),
            reference=request.form.get("reference"),
            created_at=datetime.utcnow()
        )

        db.session.add(payment)
        db.session.commit()

        flash("Payment recorded successfully", "success")
        return redirect(url_for("finance.list_payments"))

    return render_template(
        "finance/create_payment.html",
        pr=pr
    )   