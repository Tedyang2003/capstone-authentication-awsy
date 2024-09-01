from flask import Flask, render_template, request
from flask_mysqldb import MySQL
import datetime
import os
import jwt


server = Flask(__name__)
mysql = MySQL(server)

server.config['MYSQL_HOST'] = os.environ.get("MYSQL_HOST")
server.config['MYSQL_USER'] = os.environ.get("MYSQL_USER")
server.config['MYSQL_PASSWORD'] = os.environ.get("MYSQL_PASSWORD")
server.config['MYSQL_DB'] = os.environ.get("MYSQL_DB")
server.config['MYSQL_PORT'] = int(os.environ.get("MYSQL_PORT"))
server.config["MYSQL_CUSTOM_OPTIONS"] = {"ssl": {"ca": "./isrgrootx1.pem"}} 

jwt_secret = os.environ.get("JWT_SECRET")

# server.config['MYSQL_HOST'] = "gateway01.ap-southeast-1.prod.aws.tidbcloud.com"
# server.config['MYSQL_USER'] = "49AANmU89zpJQGt.root"
# server.config['MYSQL_PASSWORD'] = "EmaKcVw88peONnKT"
# server.config['MYSQL_DB'] = "auth"
# server.config['MYSQL_PORT'] = 4000
# jwt_secret = "sarcasm"
# server.config['MYSQL_SSL_CA'] = "../../../isrgrootx1.pem"

# @server.route("/", methods=['GET'])
# def home():
    
#     cur = mysql.connection.cursor()
#     cur.execute(
#         "SELECT email, password FROM user;", 
#     )
#     return cur.fetchone()

@server.route('/login', methods=['POST'])
def login():
    auth = request.authorization #Auth is a request header key

    if not auth: 
        return "Missing credentials", 401

    cur = mysql.connection.cursor()
    res = cur.execute(
        "SELECT email, password FROM user WHERE email=%s;", (auth.username, ), 
    )

    if res > 0:
        user_row = cur.fetchone()
        email = user_row[0]
        password = user_row[1]

        if auth.username != email or auth.password != password:
            return "invalid credentials", 401
        else:
            print(createJWT(auth.username, jwt_secret, True))
            return createJWT(auth.username, jwt_secret, True)
    else: 
        return "invalid credentials", 401

@server.route('/validate', methods=['POST'])
def validate():

    encoded_jwt = request.headers['Authorization']

    if not encoded_jwt:
        return 'missing credentials', 401

    encoded_jwt = encoded_jwt.split(" ")[1]

    try:
        decoded = jwt.decode(
            encoded_jwt,
            os.environ.get("JWT_SECRET"),
            algorithms=["HS256"]
        )
    except:
        return "not authorized", 403

    return decoded, 200

        

def createJWT(username, secret, authz):
    return jwt.encode(
        { #Content
            'username': username,
            'exp': datetime.datetime.now(tz=datetime.timezone.utc) + datetime.timedelta(days=1), #Requires timezone to understand how to add 1 day
            'iat': datetime.datetime.utcnow(),
            'admin': authz,
        },
        secret, # Secret
        algorithm='HS256' # Algroithm used
    )

if __name__ == '__main__':
    # Starts the Flask app and listens on all interfaces on port 5000
    server.run(host='0.0.0.0', port=5000)