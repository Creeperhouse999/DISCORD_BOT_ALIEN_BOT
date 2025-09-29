from flask import Flask, jsonify
import threading
import time
from datetime import datetime
import os

# Global variables to track bot status
bot_status = {
    "is_running": False,
    "start_time": None,
    "uptime": 0,
    "last_heartbeat": None,
    "guilds_count": 0,
    "commands_processed": 0,
    "errors_count": 0
}

app = Flask(__name__)

def update_bot_status(is_running=False, guilds_count=0, commands_processed=0, errors_count=0):
    """Update bot status information"""
    global bot_status
    bot_status["is_running"] = is_running
    bot_status["guilds_count"] = guilds_count
    bot_status["commands_processed"] = commands_processed
    bot_status["errors_count"] = errors_count
    bot_status["last_heartbeat"] = datetime.now().isoformat()
    
    if is_running and bot_status["start_time"] is None:
        bot_status["start_time"] = datetime.now().isoformat()
    elif not is_running:
        bot_status["start_time"] = None

def calculate_uptime():
    """Calculate bot uptime in seconds"""
    if bot_status["start_time"]:
        start_time = datetime.fromisoformat(bot_status["start_time"])
        uptime = (datetime.now() - start_time).total_seconds()
        bot_status["uptime"] = int(uptime)
    else:
        bot_status["uptime"] = 0

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    calculate_uptime()
    
    health_data = {
        "status": "healthy" if bot_status["is_running"] else "unhealthy",
        "bot_running": bot_status["is_running"],
        "uptime_seconds": bot_status["uptime"],
        "uptime_formatted": format_uptime(bot_status["uptime"]),
        "guilds_connected": bot_status["guilds_count"],
        "commands_processed": bot_status["commands_processed"],
        "errors_count": bot_status["errors_count"],
        "last_heartbeat": bot_status["last_heartbeat"],
        "start_time": bot_status["start_time"],
        "timestamp": datetime.now().isoformat()
    }
    
    status_code = 200 if bot_status["is_running"] else 503
    return jsonify(health_data), status_code

@app.route('/status', methods=['GET'])
def status():
    """Detailed status endpoint"""
    calculate_uptime()
    
    status_data = {
        "bot": {
            "running": bot_status["is_running"],
            "uptime": bot_status["uptime"],
            "uptime_formatted": format_uptime(bot_status["uptime"]),
            "start_time": bot_status["start_time"],
            "last_heartbeat": bot_status["last_heartbeat"]
        },
        "discord": {
            "guilds_connected": bot_status["guilds_count"]
        },
        "metrics": {
            "commands_processed": bot_status["commands_processed"],
            "errors_count": bot_status["errors_count"]
        },
        "api": {
            "endpoint": "/health",
            "status_endpoint": "/status",
            "timestamp": datetime.now().isoformat()
        }
    }
    
    return jsonify(status_data), 200

@app.route('/', methods=['GET'])
def root():
    """Root endpoint with basic info"""
    return jsonify({
        "service": "AlienBot Health API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "status": "/status"
        },
        "timestamp": datetime.now().isoformat()
    }), 200

def format_uptime(seconds):
    """Format uptime in human readable format"""
    if seconds < 60:
        return f"{seconds}s"
    elif seconds < 3600:
        minutes = seconds // 60
        return f"{minutes}m {seconds % 60}s"
    elif seconds < 86400:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        return f"{hours}h {minutes}m"
    else:
        days = seconds // 86400
        hours = (seconds % 86400) // 3600
        return f"{days}d {hours}h"

def start_health_api(host='0.0.0.0', port=5000):
    """Start the health API server in a separate thread"""
    def run_api():
        app.run(host=host, port=port, debug=False, use_reloader=False)
    
    api_thread = threading.Thread(target=run_api, daemon=True)
    api_thread.start()
    print(f"🏥 Health API started on http://{host}:{port}")
    print(f"📊 Health check: http://{host}:{port}/health")
    print(f"📈 Status: http://{host}:{port}/status")
    return api_thread

if __name__ == "__main__":
    start_health_api()
