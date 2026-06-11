from flask import Flask, request
import requests
from flask_cors import CORS 
import os 
import random

app = Flask(__name__)
CORS(app)  
servers = [
    "https://load-balancer-server-1.onrender.com",
    "https://load-balancer-server-2.onrender.com",
    "https://load-balancer-server-3.onrender.com"
]


rr_current = 0


server_weights = {
    servers[0]: 3,
    servers[1]: 2,
    servers[2]: 1
}

weighted_pool = []
for server_url, weight in server_weights.items():
    weighted_pool.extend([server_url] * weight)
w_current = 0


last_known_latency = {server: 0.0 for server in servers}


@app.route('/')
def balance():
    global rr_current, w_current
    
    
    algo = request.args.get('algo', 'round_robin')
    selected_server = servers[0] # Fallback path

    if algo == 'round_robin':
        selected_server = servers[rr_current]
        rr_current = (rr_current + 1) % len(servers)

   
    elif algo == 'weighted':
        selected_server = weighted_pool[w_current]
        w_current = (w_current + 1) % len(weighted_pool)

    
    elif algo == 'p2c':
        
        sampled_servers = random.sample(servers, 2)
        s1, s2 = sampled_servers[0], sampled_servers[1]
        
        
        if last_known_latency[s1] <= last_known_latency[s2]:
            selected_server = s1
        else:
            selected_server = s2

    
    elif algo == 'least_time':
        
        selected_server = min(last_known_latency, key=last_known_latency.get)

   
    try:
        response = requests.get(selected_server, timeout=4)
        response_data = response.json()
        
        
        node_latency = float(response_data.get('response_time', 0.100))
        last_known_latency[selected_server] = node_latency
        
        
        response_data['active_algorithm'] = algo
        return response_data
        
    except Exception as e:
       
        last_known_latency[selected_server] = 2.0  
        return {
            "error": "Server Down",
            "attempted_server": selected_server,
            "active_algorithm": algo
        }

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
