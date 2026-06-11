from flask import Flask, request
import requests
from flask_cors import CORS 
import os 
import random

app = Flask(__name__)
CORS(app)

# Your live target Render backend cluster URLs
servers = [
    "https://load-balancer-server-1.onrender.com",
    "https://load-balancer-server-2.onrender.com",
    "https://load-balancer-server-3.onrender.com"
]

# --- ALGORITHM STATE TRACKERS ---
rr_current = 0

# Weighted Round Robin (3:2:1)
server_weights = {servers[0]: 3, servers[1]: 2, servers[2]: 1}
weighted_pool = []
for server_url, weight in server_weights.items():
    weighted_pool.extend([server_url] * weight)
w_current = 0

# Real-time Metrics Cache (Initialized with healthy baseline parameters)
last_known_latency = {server: 0.05 for server in servers}
last_known_cpu = {server: 10.0 for server in servers}


@app.route('/')
def balance():
    global rr_current, w_current
    
    # -------------------------------------------------------------------------
    # AUTONOMOUS ALGORITHM SELECTION ENGINE (Self-Thinking Logic)
    # -------------------------------------------------------------------------
    max_current_cpu = max(last_known_cpu.values())
    max_current_latency = max(last_known_latency.values())

    if max_current_latency > 0.400:
        # CRITICAL LAG DETECTED: Switch to Least Response Time to bypass lagging links
        algo = 'least_time'
    elif max_current_cpu > 80.0:
        # SERVER OVERLOAD DETECTED: Switch to P2C to rapidly shed load from hot nodes
        algo = 'p2c'
    else:
        # SYSTEM HEALTHY: Use Weighted Round Robin to distribute resource traffic proportionally
        algo = 'weighted'

    selected_server = servers[0]

    # Execute Selected Strategy
    if algo == 'weighted':
        selected_server = weighted_pool[w_current]
        w_current = (w_current + 1) % len(weighted_pool)

    elif algo == 'p2c':
        sampled_servers = random.sample(servers, 2)
        s1, s2 = sampled_servers[0], sampled_servers[1]
        selected_server = s1 if last_known_latency[s1] <= last_known_latency[s2] else s2

    elif algo == 'least_time':
        selected_server = min(last_known_latency, key=last_known_latency.get)

    # -------------------------------------------------------------------------
    # NETWORK ROUTING & METRICS FEEDBACK LOOP
    # -------------------------------------------------------------------------
    try:
        response = requests.get(selected_server, timeout=4)
        response_data = response.json()
        
        # Pull latest metrics from the responding server node
        node_latency = float(response_data.get('response_time', 0.05))
        node_cpu = float(response_data.get('cpu', 10.0))
        
        # Save them to memory cache so the engine adapts on the next loop tick
        last_known_latency[selected_server] = node_latency
        last_known_cpu[selected_server] = node_cpu
        
        # Send active_algorithm to frontend so the PCAP terminal can show what the balancer chose!
        response_data['active_algorithm'] = f"auto_({algo})"
        return response_data
        
    except Exception as e:
        # Severely penalize broken servers so the engine drops them immediately
        last_known_latency[selected_server] = 5.0  
        last_known_cpu[selected_server] = 100.0
        return {
            "error": "Server Down",
            "attempted_server": selected_server,
            "active_algorithm": f"auto_failover_({algo})"
        }

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
