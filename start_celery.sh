#!/bin/bash

# eBay Token Monitoring - Celery Startup Script
# This script starts Celery worker and beat scheduler for automatic token management

echo "🚀 Starting eBay Token Monitoring System..."

# Check if we're in the right directory
if [ ! -f "manage.py" ]; then
    echo "❌ Error: manage.py not found. Please run this script from the backend directory."
    exit 1
fi

# Check if virtual environment is activated
if [ -z "$VIRTUAL_ENV" ]; then
    echo "⚠️  Warning: Virtual environment not detected."
    echo "   Make sure you have activated your virtual environment."
fi

# Function to check if a process is running
check_process() {
    pgrep -f "$1" > /dev/null
}

# Function to start Celery worker
start_worker() {
    echo "🔧 Starting Celery worker..."
    celery -A backend worker -l info -Q ebay_tokens,default --concurrency=2 &
    WORKER_PID=$!
    echo "   Worker started with PID: $WORKER_PID"
    echo $WORKER_PID > .celery_worker.pid
}

# Function to start Celery beat
start_beat() {
    echo "⏰ Starting Celery beat scheduler..."
    celery -A backend beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler &
    BEAT_PID=$!
    echo "   Beat started with PID: $BEAT_PID"
    echo $BEAT_PID > .celery_beat.pid
}

# Function to stop processes
stop_processes() {
    echo "🛑 Stopping Celery processes..."
    
    if [ -f .celery_worker.pid ]; then
        WORKER_PID=$(cat .celery_worker.pid)
        if check_process "celery.*worker"; then
            kill $WORKER_PID 2>/dev/null
            echo "   Worker stopped"
        fi
        rm -f .celery_worker.pid
    fi
    
    if [ -f .celery_beat.pid ]; then
        BEAT_PID=$(cat .celery_beat.pid)
        if check_process "celery.*beat"; then
            kill $BEAT_PID 2>/dev/null
            echo "   Beat stopped"
        fi
        rm -f .celery_beat.pid
    fi
}

# Function to show status
show_status() {
    echo "📊 Celery Process Status:"
    echo "   Worker: $(check_process "celery.*worker" && echo "✅ Running" || echo "❌ Stopped")"
    echo "   Beat:   $(check_process "celery.*beat" && echo "✅ Running" || echo "❌ Stopped")"
}

# Function to show logs
show_logs() {
    echo "📋 Recent Celery logs:"
    if [ -f "debug.log" ]; then
        tail -20 debug.log | grep -E "(celery|ebay|token)" || echo "   No recent logs found"
    else
        echo "   No log file found"
    fi
}

# Function to show monitoring info
show_monitoring() {
    echo "📈 Monitoring Information:"
    echo "   Health endpoint: http://localhost:8000/api/core/ebay-token/health/"
    echo "   Action endpoint: http://localhost:8000/api/core/ebay-token/action/"
    echo "   Scheduled tasks:"
    echo "     - Token refresh: Every hour"
    echo "     - Token validation: Every 30 minutes"
    echo "     - Health monitoring: Daily at 9 AM"
    echo "     - Log cleanup: Weekly on Sunday at 2 AM"
}

# Parse command line arguments
case "$1" in
    start)
        # Stop existing processes
        stop_processes
        
        # Start new processes
        start_worker
        sleep 2
        start_beat
        
        echo ""
        echo "✅ eBay Token Monitoring System started successfully!"
        echo ""
        show_monitoring
        ;;
    
    stop)
        stop_processes
        echo "✅ All processes stopped"
        ;;
    
    restart)
        echo "🔄 Restarting eBay Token Monitoring System..."
        stop_processes
        sleep 2
        start_worker
        sleep 2
        start_beat
        echo "✅ System restarted"
        ;;
    
    status)
        show_status
        ;;
    
    logs)
        show_logs
        ;;
    
    monitor)
        show_monitoring
        ;;
    
    test)
        echo "🧪 Running monitoring system tests..."
        python ../test_monitoring_system.py
        ;;
    
    *)
        echo "Usage: $0 {start|stop|restart|status|logs|monitor|test}"
        echo ""
        echo "Commands:"
        echo "  start   - Start Celery worker and beat scheduler"
        echo "  stop    - Stop all Celery processes"
        echo "  restart - Restart all Celery processes"
        echo "  status  - Show process status"
        echo "  logs    - Show recent logs"
        echo "  monitor - Show monitoring information"
        echo "  test    - Run monitoring system tests"
        echo ""
        echo "Examples:"
        echo "  $0 start    # Start the monitoring system"
        echo "  $0 status   # Check if processes are running"
        echo "  $0 test     # Test the monitoring system"
        exit 1
        ;;
esac 