from flask import Flask, request
import requests
from flask_cors import CORS 
import os 
import random
import threading
import time

app = Flask(__name__)
CORS(app)

# Your live target Render backend cluster URLs (Mimicking your SERVERS array)
servers = [
    "https://load-balancer-server-1.onrender.com",
    "https://load-balancer-server-2.onrender.com",
    "https://load-balancer-server-3.onrender.com"
]

# --- ENTERPRISE STATE MANAGEMENT SHIELD (Thread-Safe Struct Tracking) ---
state_lock = threading.Lock()

# Sequential counter for the Round Robin comparison node (Mimicking int rr)
rr_counter = 0

# Trackers mirroring your C Server struct parameters dynamically across the cloud links
active_connections = {server: 0 for server in servers}
failed_registry = {server: False for server in servers}
last_health_check = {server: 0.0 for server in servers}

# Constants mimicking your C #define configurations
MAX_CAPACITY = 100       # Hard circuit-break connection limit per node
HEALTH_CHECK_TTL = 10.0  # Seconds to wait before attempting to resurrect a DOWN server

def background_health_recovery(server):
    """
    Asynchronous health recovery mechanism.
    If a server is flagged as down, this function pings it quietly in the background
    after a cooling period to resurrect it when it wakes up.
    """
    try:
        response = requests.get(server, timeout=3)
        if response.status_code == 200:
            with state_lock:
                if failed_registry[server]:
                    failed_registry[server] = False
                    active_connections[server] = 0
    except Exception:
        pass

@app.route('/')
def balance():
    global rr_counter
    
    with state_lock:
        # ---------------------------------------------------------------------
        # STEP 1: BACKGROUND AUTO-RESURRECTION GATEWAY
        # ---------------------------------------------------------------------
        current_time = time.time()
        for server in servers:
            if failed_registry[server] and (current_time - last_health_check[server] > HEALTH_CHECK_TTL):
                last_health_check[server] = current_time
                threading.Thread(target=background_health_recovery, args=(server,), daemon=True).start()

        # Filter out healthy nodes for randomization selection pool
        healthy_pool = [s for s in servers if not failed_registry[s]]
        
        if not healthy_pool:
            return {
                "error": "CRITICAL: CLUSTER_FAILURE",
                "message": "All backend cluster nodes are currently unreachable.",
                "active_algorithm": "emergency_failover"
            }, 503

        # ---------------------------------------------------------------------
        # STEP 2: HYBRID SELECTION PROCESS (S1 via Round Robin, S2 via Random Pool)
        # ---------------------------------------------------------------------
        # Core Logic mimicking your C loop: while(servers[s1].failed)
        s1_index = rr_counter
        attempts = 0
        while failed_registry[servers[s1_index]] and attempts < len(servers):
            s1_index = (s1_index + 1) % len(servers)
            attempts += 1
            
        s1 = servers[s1_index]
        # Increment global turn tracker (rr = (rr + 1) % SERVERS)
        rr_counter = (rr_counter + 1) % len(servers)

        # Grab a second random server from the healthy pool (getRandomHealthyServer)
        s2 = random.choice(healthy_pool)

        # ---------------------------------------------------------------------
        # STEP 3: THE POWER-OF-TWO DECISION GATE
        # ---------------------------------------------------------------------
        # Evaluates which server node is handling a lower active connection load
        if active_connections[s1] <= active_connections[s2]:
            selected_server = s1
        else:
            selected_server = s2

        # ---------------------------------------------------------------------
        # STEP 4: HARD CIRCUIT BREAKER (MAX_CAPACITY Enforcement)
        # ---------------------------------------------------------------------
        if active_connections[selected_server] >= MAX_CAPACITY:
            return {
                "error": "SERVICE_UNAVAILABLE",
                "message": f"Target cluster node has exceeded its secure ceiling limit of {MAX_CAPACITY} active connections.",
                "active_algorithm": "circuit_breaker"
            }, 503

        # Increment active connection count immediately before launching into the network
        active_connections[selected_server] += 1

    # ---------------------------------------------------------------------
    # STEP 5: LIVE HTTP TRANSACTION LOOP & METRICS COLLECTION
    # ---------------------------------------------------------------------
    try:
        # Cross the cloud data center boundary to forward client request
        response = requests.get(selected_server, timeout=4)
        response_data = response.json()
        status_code = 200
        
    except Exception as e:
        # CRASH DETECTED (Mimicking servers[2].failed = 1)
        with state_lock:
            failed_registry[selected_server] = True
            last_health_check[selected_server] = time.time()
            
        response_data = {
            "error": "NODE_CONNECTION_TIMEOUT",
            "message": f"Forwarding failure to destination link: {selected_server}. Fault isolation executed.",
            "attempted_server": selected_server
        }
        status_code = 502

    finally:
        # CONNECTION DRAIN ENVELOPE (Mimicking servers[i].activeConnections -= completed)
        with state_lock:
            if active_connections[selected_server] > 0:
                active_connections[selected_server] -= 1

        # Push these lines to the right so they sit inside the finally block!
        response_data['active_algorithm'] = "hybrid_p2c_c_engine"
    return response_data, status_code

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port, threaded=True)
