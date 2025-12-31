def register_blueprints(app):
    """Register all blueprints with the Flask app"""
    from routes.login import login_bp
    from routes.register import register_bp
    from routes.dashboard import dashboard_bp
    from routes.transfer import transfer_bp
    from routes.user import user_bp
    from routes.qna import qna_bp

    app.register_blueprint(login_bp)
    app.register_blueprint(register_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(transfer_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(qna_bp)
