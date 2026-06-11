from flask import Flask
import requests
from flask_cors import CORS 
import os 

app = Flask(__name__)
CORS(app)  


servers = [
   "https://load-balancer-server-1.onrender.com",
    "https://load-balancer-server-2.onrender.com",
    "https://load-balancer-server-3.onrender.com"
]

current = 0

@app.route('/')
def balance():
    global current
    server = servers[current]
    current = (current + 1) % len(servers)

    try:
        response = requests.get(server)
        return response.json()
    except:
        return {
            "error": "Server Down",
            "attempted_server": server 
        }


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
