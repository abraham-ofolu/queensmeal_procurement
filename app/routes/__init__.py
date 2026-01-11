from .auth import auth_bp
from .procurement import procurement_bp
from .finance import finance_bp
from .vendors import vendors_bp
from .director import director_bp

__all__ = ["auth_bp", "procurement_bp", "finance_bp", "vendors_bp", "director_bp"]
