# Online Support Ticket Application
# Tushar Supe : 21f1003637
# Vaidehi Agarwal: 21f1003880
# File Info: This is main app file where backend application starts.

# --------------------  Imports  --------------------

from application import create_app
from application.globals import HOST, PORT, DEBUG, ENV_TYPE

# --------------------  Initialization  --------------------

app = create_app(env_type=ENV_TYPE)

# --------------------  Main  --------------------
if __name__ == "__main__":
    app.run(host=HOST, port=PORT, debug=DEBUG)

# --------------------  End  --------------------
