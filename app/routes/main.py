from flask import Blueprint

main_bp = Blueprint("main", __name__)

@main_bp.get("/")
def index():
    # IMPORTANT: Must return 200 so Render health checks pass
    return (
        "<h3>Queensmeal Procurement is running ✅</h3>"
        "<p>Go to <a href='/login'>/login</a></p>",
        200,
    )

@main_bp.get("/favicon.ico")
def favicon():
    # Avoid noisy 404s in logs
    return ("", 204)
