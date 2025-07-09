#!/usr/bin/env python3
"""
Comprehensive System Shutdown Script for Restyle Project
Automatically shuts down all services, processes, and containers
"""

import os
import sys
import signal
import subprocess
import time
import psutil
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('shutdown.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class SystemShutdown:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.backend_dir = self.project_root / "backend"
        self.frontend_dir = self.project_root / "frontend"
        self.processes_to_kill = []
        
    def log_step(self, message):
        """Log a shutdown step with timestamp"""
        logger.info(f"🔄 {message}")
        
    def log_success(self, message):
        """Log a successful operation"""
        logger.info(f"✅ {message}")
        
    def log_error(self, message):
        """Log an error"""
        logger.error(f"❌ {message}")
        
    def log_warning(self, message):
        """Log a warning"""
        logger.warning(f"⚠️ {message}")
        
    def find_processes_by_name(self, process_names):
        """Find processes by name and return list of PIDs"""
        found_processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                for name in process_names:
                    if name.lower() in proc.info['name'].lower():
                        found_processes.append(proc.info['pid'])
                        break
                    # Also check command line
                    if proc.info['cmdline']:
                        cmdline = ' '.join(proc.info['cmdline']).lower()
                        if name.lower() in cmdline:
                            found_processes.append(proc.info['pid'])
                            break
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return found_processes
        
    def kill_processes(self, pids, force=False):
        """Kill processes by PID"""
        for pid in pids:
            try:
                proc = psutil.Process(pid)
                if force:
                    proc.kill()
                    self.log_success(f"Force killed process {pid}")
                else:
                    proc.terminate()
                    self.log_success(f"Terminated process {pid}")
            except psutil.NoSuchProcess:
                self.log_warning(f"Process {pid} already terminated")
            except psutil.AccessDenied:
                self.log_error(f"Access denied to process {pid}")
                
    def stop_django_server(self):
        """Stop Django development server"""
        self.log_step("Stopping Django development server...")
        
        # Find Django processes
        django_pids = self.find_processes_by_name([
            'manage.py', 'runserver', 'python', 'django'
        ])
        
        if django_pids:
            self.log_step(f"Found {len(django_pids)} Django processes: {django_pids}")
            self.kill_processes(django_pids)
            time.sleep(2)  # Give processes time to terminate
            
            # Force kill if still running
            remaining = self.find_processes_by_name(['manage.py', 'runserver'])
            if remaining:
                self.log_warning(f"Force killing remaining Django processes: {remaining}")
                self.kill_processes(remaining, force=True)
        else:
            self.log_success("No Django processes found")
            
    def stop_frontend_server(self):
        """Stop React development server"""
        self.log_step("Stopping React development server...")
        
        # Find Node.js/React processes
        node_pids = self.find_processes_by_name([
            'node', 'npm', 'yarn', 'react-scripts'
        ])
        
        if node_pids:
            self.log_step(f"Found {len(node_pids)} Node.js processes: {node_pids}")
            self.kill_processes(node_pids)
            time.sleep(2)
            
            # Force kill if still running
            remaining = self.find_processes_by_name(['node', 'npm'])
            if remaining:
                self.log_warning(f"Force killing remaining Node.js processes: {remaining}")
                self.kill_processes(remaining, force=True)
        else:
            self.log_success("No Node.js processes found")
            
    def stop_celery_workers(self):
        """Stop Celery workers and beat scheduler"""
        self.log_step("Stopping Celery workers and beat scheduler...")
        
        # Find Celery processes
        celery_pids = self.find_processes_by_name([
            'celery', 'celerybeat', 'celeryd'
        ])
        
        if celery_pids:
            self.log_step(f"Found {len(celery_pids)} Celery processes: {celery_pids}")
            self.kill_processes(celery_pids)
            time.sleep(2)
            
            # Force kill if still running
            remaining = self.find_processes_by_name(['celery'])
            if remaining:
                self.log_warning(f"Force killing remaining Celery processes: {remaining}")
                self.kill_processes(remaining, force=True)
        else:
            self.log_success("No Celery processes found")
            
    def stop_docker_containers(self):
        """Stop all Docker containers"""
        self.log_step("Stopping Docker containers...")
        
        try:
            # List running containers
            result = subprocess.run(
                ['docker', 'ps', '--format', '{{.ID}}'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0 and result.stdout.strip():
                container_ids = result.stdout.strip().split('\n')
                self.log_step(f"Found {len(container_ids)} running containers")
                
                for container_id in container_ids:
                    if container_id:
                        try:
                            subprocess.run(
                                ['docker', 'stop', container_id],
                                capture_output=True,
                                timeout=10
                            )
                            self.log_success(f"Stopped container {container_id}")
                        except subprocess.TimeoutExpired:
                            self.log_error(f"Timeout stopping container {container_id}")
                        except Exception as e:
                            self.log_error(f"Error stopping container {container_id}: {e}")
            else:
                self.log_success("No running Docker containers found")
                
        except FileNotFoundError:
            self.log_warning("Docker not found or not installed")
        except Exception as e:
            self.log_error(f"Error checking Docker containers: {e}")
            
    def stop_docker_compose(self):
        """Stop Docker Compose services"""
        self.log_step("Stopping Docker Compose services...")
        
        compose_file = self.project_root / "docker-compose.yml"
        if compose_file.exists():
            try:
                subprocess.run(
                    ['docker-compose', 'down'],
                    cwd=self.project_root,
                    capture_output=True,
                    timeout=30
                )
                self.log_success("Docker Compose services stopped")
            except FileNotFoundError:
                self.log_warning("Docker Compose not found")
            except subprocess.TimeoutExpired:
                self.log_error("Timeout stopping Docker Compose services")
            except Exception as e:
                self.log_error(f"Error stopping Docker Compose: {e}")
        else:
            self.log_success("No docker-compose.yml found")
            
    def cleanup_temp_files(self):
        """Clean up temporary files and logs"""
        self.log_step("Cleaning up temporary files...")
        
        temp_files = [
            "celerybeat-schedule",
            "*.pyc",
            "__pycache__",
            ".pytest_cache",
            "*.log",
            "node_modules/.cache"
        ]
        
        for pattern in temp_files:
            try:
                if '*' in pattern:
                    # Use glob for wildcard patterns
                    import glob
                    files = glob.glob(str(self.project_root / pattern))
                    for file in files:
                        try:
                            if os.path.isfile(file):
                                os.remove(file)
                            elif os.path.isdir(file):
                                import shutil
                                shutil.rmtree(file)
                        except Exception as e:
                            self.log_warning(f"Could not remove {file}: {e}")
                else:
                    file_path = self.project_root / pattern
                    if file_path.exists():
                        file_path.unlink()
                        self.log_success(f"Removed {pattern}")
            except Exception as e:
                self.log_warning(f"Error cleaning up {pattern}: {e}")
                
    def stop_port_processes(self):
        """Stop processes running on specific ports"""
        self.log_step("Stopping processes on specific ports...")
        
        ports_to_check = [8000, 3000, 5000, 5432, 6379]  # Common ports
        
        for port in ports_to_check:
            try:
                # Find process using the port
                result = subprocess.run(
                    ['netstat', '-ano', '|', 'findstr', f':{port}'],
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                
                if result.stdout.strip():
                    lines = result.stdout.strip().split('\n')
                    for line in lines:
                        if f':{port}' in line:
                            parts = line.split()
                            if len(parts) >= 5:
                                pid = parts[-1]
                                try:
                                    self.kill_processes([int(pid)])
                                    self.log_success(f"Stopped process on port {port}")
                                except ValueError:
                                    continue
                                    
            except Exception as e:
                self.log_warning(f"Error checking port {port}: {e}")
                
    def stop_python_processes(self):
        """Stop all Python processes related to the project"""
        self.log_step("Stopping Python processes...")
        
        python_pids = self.find_processes_by_name(['python', 'python3'])
        
        if python_pids:
            self.log_step(f"Found {len(python_pids)} Python processes: {python_pids}")
            
            # Only kill processes that are likely part of our project
            project_pids = []
            for pid in python_pids:
                try:
                    proc = psutil.Process(pid)
                    cmdline = ' '.join(proc.cmdline()).lower()
                    if any(keyword in cmdline for keyword in ['restyle', 'manage.py', 'celery', 'django']):
                        project_pids.append(pid)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
                    
            if project_pids:
                self.log_step(f"Killing {len(project_pids)} project-related Python processes")
                self.kill_processes(project_pids)
                time.sleep(2)
                
                # Force kill remaining project processes
                remaining = self.find_processes_by_name(['python'])
                if remaining:
                    self.log_warning(f"Force killing remaining Python processes: {remaining}")
                    self.kill_processes(remaining, force=True)
            else:
                self.log_success("No project-related Python processes found")
        else:
            self.log_success("No Python processes found")
            
    def stop_ebay_monitoring(self):
        """Stop any eBay monitoring processes"""
        self.log_step("Stopping eBay monitoring processes...")
        
        ebay_pids = self.find_processes_by_name([
            'ebay', 'monitoring', 'refresh', 'token'
        ])
        
        if ebay_pids:
            self.log_step(f"Found {len(ebay_pids)} eBay monitoring processes: {ebay_pids}")
            self.kill_processes(ebay_pids)
            time.sleep(2)
            
            # Force kill if still running
            remaining = self.find_processes_by_name(['ebay', 'monitoring'])
            if remaining:
                self.log_warning(f"Force killing remaining eBay processes: {remaining}")
                self.kill_processes(remaining, force=True)
        else:
            self.log_success("No eBay monitoring processes found")
            
    def verify_shutdown(self):
        """Verify that all services have been stopped"""
        self.log_step("Verifying shutdown...")
        
        # Check for remaining processes
        remaining_processes = []
        
        # Check Django
        django_pids = self.find_processes_by_name(['manage.py', 'runserver'])
        if django_pids:
            remaining_processes.extend([('Django', pid) for pid in django_pids])
            
        # Check Node.js
        node_pids = self.find_processes_by_name(['node', 'npm'])
        if node_pids:
            remaining_processes.extend([('Node.js', pid) for pid in node_pids])
            
        # Check Celery
        celery_pids = self.find_processes_by_name(['celery'])
        if celery_pids:
            remaining_processes.extend([('Celery', pid) for pid in celery_pids])
            
        # Check Python
        python_pids = self.find_processes_by_name(['python'])
        if python_pids:
            remaining_processes.extend([('Python', pid) for pid in python_pids])
            
        if remaining_processes:
            self.log_warning(f"Found {len(remaining_processes)} remaining processes:")
            for service, pid in remaining_processes:
                self.log_warning(f"  - {service}: PID {pid}")
        else:
            self.log_success("All services successfully stopped")
            
    def shutdown_system(self, force=False):
        """Complete system shutdown"""
        logger.info("🚀 Starting comprehensive system shutdown...")
        
        try:
            # 1. Stop Django server
            self.stop_django_server()
            
            # 2. Stop frontend server
            self.stop_frontend_server()
            
            # 3. Stop Celery workers
            self.stop_celery_workers()
            
            # 4. Stop eBay monitoring
            self.stop_ebay_monitoring()
            
            # 5. Stop Python processes
            self.stop_python_processes()
            
            # 6. Stop processes on specific ports
            self.stop_port_processes()
            
            # 7. Stop Docker containers
            self.stop_docker_containers()
            
            # 8. Stop Docker Compose
            self.stop_docker_compose()
            
            # 9. Clean up temporary files
            self.cleanup_temp_files()
            
            # 10. Verify shutdown
            self.verify_shutdown()
            
            logger.info("🎉 System shutdown completed successfully!")
            
        except KeyboardInterrupt:
            logger.info("⚠️ Shutdown interrupted by user")
            sys.exit(1)
        except Exception as e:
            logger.error(f"❌ Error during shutdown: {e}")
            sys.exit(1)
            
    def emergency_shutdown(self):
        """Emergency shutdown - force kill all related processes"""
        logger.warning("🚨 EMERGENCY SHUTDOWN - Force killing all processes...")
        
        # Force kill all related processes
        all_pids = self.find_processes_by_name([
            'python', 'node', 'npm', 'celery', 'django', 'manage.py',
            'runserver', 'react-scripts', 'ebay', 'monitoring'
        ])
        
        if all_pids:
            self.log_step(f"Force killing {len(all_pids)} processes: {all_pids}")
            self.kill_processes(all_pids, force=True)
            
        # Stop all Docker containers
        try:
            subprocess.run(['docker', 'stop', '$(docker ps -q)'], shell=True)
        except:
            pass
            
        logger.info("🚨 Emergency shutdown completed")

def main():
    """Main function"""
    shutdown = SystemShutdown()
    
    if len(sys.argv) > 1 and sys.argv[1] == '--emergency':
        shutdown.emergency_shutdown()
    else:
        shutdown.shutdown_system()

if __name__ == "__main__":
    main() 