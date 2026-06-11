

from flask import Flask, Response
from prometheus_client import Counter, Gauge, generate_latest
import time
import random

app = Flask(__name__)


REQUEST_COUNT = Counter(
    'server3_requests_total',
    'Total Requests Handled by Server 3'
)

CPU_LOAD = Gauge(
    'server3_cpu_usage',
    'CPU Usage of Server 3'
)

MEMORY_LOAD = Gauge(
    'server3_memory_usage',
    'Memory Usage of Server 3'
)

RESPONSE_TIME = Gauge(
    'server3_response_time',
    'Response Time of Server 3'
)


@app.route('/')
def home():

    start = time.time()

    REQUEST_COUNT.inc()

    
    cpu = random.randint(40, 60)
    memory = random.randint(40, 60)

    CPU_LOAD.set(cpu)
    MEMORY_LOAD.set(memory)

   
    delay = random.uniform(0.3, 1.0)
    time.sleep(delay)

    response = time.time() - start
    RESPONSE_TIME.set(response)

    return {
        "server": "Server 3",
        "status": "ACTIVE",
        "cpu": cpu,
        "memory": memory,
        "response_time": response
    }


@app.route('/health')
def health():
    return {
        "server": "Server 3",
        "health": "UP"
    }


@app.route('/metrics')
def metrics():
    return Response(
        generate_latest(),
        mimetype='text/plain'
    )


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5003)