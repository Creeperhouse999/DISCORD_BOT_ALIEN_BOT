from flask import Flask
import threading

app = Flask(__name__)

@app.route('/health', methods=['GET'])
def health_check():
    """Simple health check endpoint - returns 200 OK"""
    return '', 200

@app.route('/', methods=['GET'])
def root():
    """Root endpoint - returns 200 OK"""
    return '', 200

def start_health_api(host='0.0.0.0', port=5000):
    """Start the health API server in a separate thread"""
    def run_api():
        app.run(host=host, port=port, debug=False, use_reloader=False)
    
    api_thread = threading.Thread(target=run_api, daemon=True)
    api_thread.start()
    print(f"🏥 Health API started on http://{host}:{port}")
    print(f"📊 Health check: http://{host}:{port}/health")
    return api_thread

if __name__ == "__main__":
    start_health_api()