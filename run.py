from skip_db_lib import create_app
from skip_db_lib import config


if __name__ == "__main__":
    app = create_app(config.DevConfig)
    app.run(host="localhost", port=4995, debug=True)