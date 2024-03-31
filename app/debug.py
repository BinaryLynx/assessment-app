from app.app_factory import get_app
from app.config_object import DevConfig


app = get_app(DevConfig)


# if __name__ == "__main__":
#     app.run(host="0.0.0.0", port=5000, use_debugger=True, use_reloader=True, passthrough_errors=True, debug=True)
