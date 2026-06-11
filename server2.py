

from flask import Flask, Response
from prometheus_client import Counter, Gauge, generate_latest
import time
import random

app = Flask(__name__)


REQUEST_COUNT = Counter(
    'server2_requests_total',
    'Total Requests Handled by Server 2'
)

CPU_LOAD = Gauge(
    'server2_cpu_usage',
    'CPU Usage of Server 2'
)

MEMORY_LOAD = Gauge(
    'server2_memory_usage',
    'Memory Usage of Server 2'
)

RESPONSE_TIME = Gauge(
    'server2_response_time',
    'Response Time of Server 2'
)


@app.route('/')
def home():

    start = time.time()

    REQUEST_COUNT.inc()

  
    cpu = random.randint(40, 60)
    memory = random.randint(40, 60)

    CPU_LOAD.set(cpu)
    MEMORY_LOAD.set(memory)

    delay = random.uniform(0.2, 0.7)
    time.sleep(delay)

    response = time.time() - start
    RESPONSE_TIME.set(response)

    return {
        "server": "Server 2",
        "status": "ACTIVE",
        "cpu": cpu,
        "memory": memory,
        "response_time": response
    }


@app.route('/health')
def health():
    return {
        "server": "Server 2",
        "health": "UP"
    }


@app.route('/metrics')
def metrics():
    return Response(
        generate_latest(),
        mimetype='text/plain'
    )


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002)