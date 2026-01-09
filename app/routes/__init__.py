from .main import main_bp
from .auth import auth_bp
from .procurement import procurement_bp
from .vendors import vendors_bp
from .finance import finance_bp
from .reports import reports_bp

__all__ = [
    "main_bp",
    "auth_bp",
    "procurement_bp",
    "vendors_bp",
    "finance_bp",
    "reports_bp",
]
