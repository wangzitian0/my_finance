# Monitoring and Maintenance

## System Monitoring Architecture

### 1. Health Check Endpoints

#### Application Health
```python
from fastapi import FastAPI, HTTPException
from datetime import datetime
import psutil
import asyncio

@app.get("/api/v1/health")
async def comprehensive_health_check():
    """Comprehensive system health check"""
    
    health_report = {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": get_app_version(),
        "components": {},
        "metrics": {}
    }
    
    # Database connectivity
    try:
        from neomodel import db
        start_time = time.time()
        db.cypher_query("RETURN 1")
        response_time = (time.time() - start_time) * 1000
        
        health_report["components"]["neo4j"] = {
            "status": "healthy",
            "response_time_ms": round(response_time, 2),
            "last_check": datetime.now().isoformat()
        }
    except Exception as e:
        health_report["components"]["neo4j"] = {
            "status": "unhealthy",
            "error": str(e),
            "last_check": datetime.now().isoformat()
        }
        health_report["status"] = "degraded"
    
    # LLM Service availability
    try:
        llm_health = await check_llm_service_health()
        health_report["components"]["llm_service"] = llm_health
    except Exception as e:
        health_report["components"]["llm_service"] = {
            "status": "unhealthy",
            "error": str(e)
        }
        health_report["status"] = "degraded"
    
    # System resources
    health_report["metrics"]["system"] = {
        "cpu_usage_percent": psutil.cpu_percent(interval=1),
        "memory_usage_percent": psutil.virtual_memory().percent,
        "disk_usage_percent": psutil.disk_usage('/').percent,
        "load_average": psutil.getloadavg()
    }
    
    # Data pipeline status
    pipeline_status = check_data_pipeline_status()
    health_report["components"]["data_pipeline"] = pipeline_status
    
    return health_report
```

### 2. Metrics Collection

#### Performance Metrics
```python
import time
from functools import wraps
from collections import defaultdict
import threading

class MetricsCollector:
    def __init__(self):
        self.metrics = defaultdict(list)
        self.counters = defaultdict(int)
        self.lock = threading.Lock()
    
    def record_response_time(self, endpoint, duration_ms):
        """Record API response time"""
        with self.lock:
            self.metrics[f"{endpoint}_response_time"].append({
                'value': duration_ms,
                'timestamp': datetime.now().isoformat()
            })
            
            # Keep only last 1000 records per endpoint
            if len(self.metrics[f"{endpoint}_response_time"]) > 1000:
                self.metrics[f"{endpoint}_response_time"] = \
                    self.metrics[f"{endpoint}_response_time"][-1000:]
    
    def increment_counter(self, metric_name):
        """Increment counter metric"""
        with self.lock:
            self.counters[metric_name] += 1
    
    def record_dcf_calculation_metrics(self, ticker, calculation_time_ms, success):
        """Record DCF calculation specific metrics"""
        with self.lock:
            self.record_response_time("dcf_calculation", calculation_time_ms)
            
            if success:
                self.increment_counter("dcf_calculations_success")
            else:
                self.increment_counter("dcf_calculations_failed")
            
            self.increment_counter(f"dcf_calculations_by_ticker_{ticker}")

# Global metrics collector
metrics = MetricsCollector()

def monitor_performance(endpoint_name):
    """Decorator to monitor endpoint performance"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                metrics.increment_counter(f"{endpoint_name}_success")
                return result
            except Exception as e:
                metrics.increment_counter(f"{endpoint_name}_error")
                raise
            finally:
                duration_ms = (time.time() - start_time) * 1000
                metrics.record_response_time(endpoint_name, duration_ms)
        return wrapper
    return decorator
```

#### Data Quality Metrics
```python
class DataQualityMonitor:
    def __init__(self):
        self.quality_thresholds = {
            'sec_filing_completeness': 0.95,
            'price_data_freshness_hours': 24,
            'analyst_data_coverage': 0.80
        }
    
    def monitor_data_quality_continuous(self):
        """Continuous data quality monitoring"""
        
        while True:
            try:
                quality_report = self.generate_quality_report()
                
                # Check for quality degradation
                for metric, threshold in self.quality_thresholds.items():
                    current_value = quality_report.get(metric, 0)
                    
                    if current_value < threshold:
                        self.trigger_quality_alert(metric, current_value, threshold)
                
                # Store quality metrics
                self.store_quality_metrics(quality_report)
                
                time.sleep(300)  # Check every 5 minutes
                
            except Exception as e:
                logger.error(f"Error in data quality monitoring: {e}")
                time.sleep(60)  # Retry in 1 minute on error
    
    def generate_quality_report(self):
        """Generate comprehensive data quality report"""
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'sec_filing_completeness': self.check_sec_filing_completeness(),
            'price_data_freshness_hours': self.check_price_data_freshness(),
            'analyst_data_coverage': self.check_analyst_data_coverage(),
            'data_consistency_score': self.calculate_data_consistency_score()
        }
        
        return report
```

### 3. Alerting System

#### Alert Configuration
```python
from enum import Enum
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class AlertSeverity(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class AlertManager:
    def __init__(self, config):
        self.config = config
        self.alert_rules = self.load_alert_rules()
        self.notification_channels = self.setup_notification_channels()
    
    def trigger_alert(self, alert_type, severity, message, context=None):
        """Trigger an alert with specified severity"""
        
        alert = {
            'id': generate_alert_id(),
            'type': alert_type,
            'severity': severity.value,
            'message': message,
            'context': context or {},
            'timestamp': datetime.now().isoformat(),
            'status': 'ACTIVE'
        }
        
        # Store alert
        self.store_alert(alert)
        
        # Send notifications based on severity
        if severity in [AlertSeverity.HIGH, AlertSeverity.CRITICAL]:
            self.send_immediate_notification(alert)
        elif severity == AlertSeverity.MEDIUM:
            self.queue_notification(alert)
        
        return alert
    
    def send_immediate_notification(self, alert):
        """Send immediate notification for high-severity alerts"""
        
        # Email notification
        if 'email' in self.notification_channels:
            self.send_email_alert(alert)
        
        # Slack notification (if configured)
        if 'slack' in self.notification_channels:
            self.send_slack_alert(alert)
    
    def send_email_alert(self, alert):
        """Send email alert notification"""
        
        subject = f"[{alert['severity'].upper()}] My Finance Alert: {alert['type']}"
        
        body = f"""
        Alert ID: {alert['id']}
        Type: {alert['type']}
        Severity: {alert['severity']}
        Timestamp: {alert['timestamp']}
        
        Message:
        {alert['message']}
        
        Context:
        {json.dumps(alert['context'], indent=2)}
        
        Please investigate and resolve this issue.
        """
        
        msg = MIMEMultipart()
        msg['From'] = self.config['smtp']['from_email']
        msg['To'] = ', '.join(self.config['alert_recipients'])
        msg['Subject'] = subject
        
        msg.attach(MIMEText(body, 'plain'))
        
        try:
            server = smtplib.SMTP(self.config['smtp']['server'], self.config['smtp']['port'])
            server.starttls()
            server.login(self.config['smtp']['username'], self.config['smtp']['password'])
            text = msg.as_string()
            server.sendmail(self.config['smtp']['from_email'], 
                          self.config['alert_recipients'], text)
            server.quit()
        except Exception as e:
            logger.error(f"Failed to send email alert: {e}")
```

#### Common Alert Rules
```python
class SystemAlertRules:
    def __init__(self, alert_manager):
        self.alert_manager = alert_manager
    
    def check_response_time_alerts(self, endpoint_metrics):
        """Check for response time alerts"""
        
        for endpoint, times in endpoint_metrics.items():
            if not times:
                continue
            
            avg_response_time = sum(times) / len(times)
            p95_response_time = sorted(times)[int(len(times) * 0.95)]
            
            # Alert if average response time > 5 seconds
            if avg_response_time > 5000:
                self.alert_manager.trigger_alert(
                    alert_type="HIGH_RESPONSE_TIME",
                    severity=AlertSeverity.MEDIUM,
                    message=f"Average response time for {endpoint} is {avg_response_time:.2f}ms",
                    context={'endpoint': endpoint, 'avg_time': avg_response_time}
                )
            
            # Alert if P95 response time > 10 seconds
            if p95_response_time > 10000:
                self.alert_manager.trigger_alert(
                    alert_type="VERY_HIGH_RESPONSE_TIME",
                    severity=AlertSeverity.HIGH,
                    message=f"P95 response time for {endpoint} is {p95_response_time:.2f}ms",
                    context={'endpoint': endpoint, 'p95_time': p95_response_time}
                )
    
    def check_error_rate_alerts(self, error_metrics):
        """Check for error rate alerts"""
        
        for endpoint, stats in error_metrics.items():
            total_requests = stats['success'] + stats['error']
            
            if total_requests > 0:
                error_rate = stats['error'] / total_requests
                
                # Alert if error rate > 5%
                if error_rate > 0.05:
                    severity = AlertSeverity.HIGH if error_rate > 0.10 else AlertSeverity.MEDIUM
                    
                    self.alert_manager.trigger_alert(
                        alert_type="HIGH_ERROR_RATE",
                        severity=severity,
                        message=f"Error rate for {endpoint} is {error_rate:.2%}",
                        context={
                            'endpoint': endpoint,
                            'error_rate': error_rate,
                            'total_requests': total_requests
                        }
                    )
```

### 4. Log Management

#### Structured Logging
```python
import logging
import json
from datetime import datetime

class StructuredLogger:
    def __init__(self, name):
        self.logger = logging.getLogger(name)
        self.setup_handlers()
    
    def setup_handlers(self):
        """Setup structured logging handlers"""
        
        # Console handler for development
        console_handler = logging.StreamHandler()
        console_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(console_formatter)
        
        # File handler for production
        file_handler = logging.FileHandler('logs/app.json')
        
        self.logger.addHandler(console_handler)
        self.logger.addHandler(file_handler)
        self.logger.setLevel(logging.INFO)
    
    def log_dcf_calculation(self, ticker, success, duration_ms, error=None):
        """Log DCF calculation event"""
        
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'event_type': 'dcf_calculation',
            'ticker': ticker,
            'success': success,
            'duration_ms': duration_ms,
            'error': str(error) if error else None
        }
        
        if success:
            self.logger.info(json.dumps(log_entry))
        else:
            self.logger.error(json.dumps(log_entry))
    
    def log_api_request(self, endpoint, method, status_code, duration_ms, user_id=None):
        """Log API request"""
        
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'event_type': 'api_request',
            'endpoint': endpoint,
            'method': method,
            'status_code': status_code,
            'duration_ms': duration_ms,
            'user_id': user_id
        }
        
        self.logger.info(json.dumps(log_entry))
```

### 5. Performance Dashboard

#### Metrics API Endpoints
```python
@app.get("/api/v1/metrics/performance")
async def get_performance_metrics(time_range: str = "24h"):
    """Get system performance metrics"""
    
    end_time = datetime.now()
    if time_range == "24h":
        start_time = end_time - timedelta(hours=24)
    elif time_range == "7d":
        start_time = end_time - timedelta(days=7)
    else:
        start_time = end_time - timedelta(hours=1)
    
    metrics_data = {
        'time_range': time_range,
        'api_performance': get_api_performance_metrics(start_time, end_time),
        'dcf_calculation_stats': get_dcf_calculation_stats(start_time, end_time),
        'data_quality_metrics': get_data_quality_metrics(start_time, end_time),
        'system_resources': get_current_system_resources()
    }
    
    return metrics_data

@app.get("/api/v1/metrics/alerts")
async def get_alert_summary(status: str = "active"):
    """Get alert summary"""
    
    alerts = get_alerts_by_status(status)
    
    summary = {
        'total_alerts': len(alerts),
        'by_severity': {},
        'by_type': {},
        'recent_alerts': alerts[:10]  # Last 10 alerts
    }
    
    for alert in alerts:
        severity = alert['severity']
        alert_type = alert['type']
        
        summary['by_severity'][severity] = summary['by_severity'].get(severity, 0) + 1
        summary['by_type'][alert_type] = summary['by_type'].get(alert_type, 0) + 1
    
    return summary
```

## Maintenance Procedures

### 1. Regular Maintenance Tasks

#### Daily Tasks
```bash
#!/bin/bash
# daily_maintenance.sh

echo "Starting daily maintenance tasks..."

# Check disk space
df -h | grep -E "/(data|logs)" | awk '{print $1, $5}' | while read filesystem usage; do
    usage_num=$(echo $usage | sed 's/%//')
    if [ $usage_num -gt 80 ]; then
        echo "WARNING: $filesystem is $usage full"
    fi
done

# Rotate logs
find /app/logs -name "*.log" -mtime +7 -delete
find /app/logs -name "*.json" -mtime +30 -delete

# Check database health
python -c "
from neomodel import db
try:
    result = db.cypher_query('CALL dbms.queryJmx(\"org.neo4j:instance=kernel#0,name=High Availability\") YIELD attributes RETURN attributes.UpdateTime')
    print('Neo4j health check: PASSED')
except Exception as e:
    print(f'Neo4j health check: FAILED - {e}')
"

# Clean up old DCF calculations
python scripts/cleanup_old_calculations.py

echo "Daily maintenance completed"
```

#### Weekly Tasks
```bash
#!/bin/bash
# weekly_maintenance.sh

echo "Starting weekly maintenance tasks..."

# Database maintenance
docker exec finance-neo4j neo4j-admin database check --database=neo4j

# Performance analysis
python scripts/generate_weekly_performance_report.py

# Update data quality baselines
python scripts/update_quality_baselines.py

# Security scan
python scripts/security_health_check.py

echo "Weekly maintenance completed"
```

### 2. Backup and Recovery

#### Automated Backup Script
```python
import subprocess
import os
from datetime import datetime
import logging

class BackupManager:
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(__name__)
    
    def backup_neo4j_database(self):
        """Backup Neo4j database"""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"neo4j_backup_{timestamp}"
        backup_path = os.path.join(self.config['backup_dir'], backup_name)
        
        try:
            # Create database dump
            dump_cmd = [
                'docker', 'exec', 'finance-neo4j',
                'neo4j-admin', 'database', 'dump',
                '--database=neo4j',
                f'--to-path=/data/dumps/{backup_name}.dump'
            ]
            
            subprocess.run(dump_cmd, check=True, capture_output=True, text=True)
            
            # Copy dump to backup directory
            copy_cmd = [
                'docker', 'cp',
                f'finance-neo4j:/data/dumps/{backup_name}.dump',
                f'{backup_path}.dump'
            ]
            
            subprocess.run(copy_cmd, check=True)
            
            # Compress backup
            subprocess.run(['gzip', f'{backup_path}.dump'], check=True)
            
            self.logger.info(f"Neo4j backup completed: {backup_path}.dump.gz")
            
            # Clean up old backups (keep last 30 days)
            self.cleanup_old_backups()
            
            return True
            
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Neo4j backup failed: {e}")
            return False
    
    def cleanup_old_backups(self):
        """Remove backups older than retention period"""
        
        retention_days = self.config.get('backup_retention_days', 30)
        cutoff_time = datetime.now().timestamp() - (retention_days * 24 * 3600)
        
        backup_dir = self.config['backup_dir']
        
        for filename in os.listdir(backup_dir):
            if filename.startswith('neo4j_backup_') and filename.endswith('.gz'):
                file_path = os.path.join(backup_dir, filename)
                if os.path.getctime(file_path) < cutoff_time:
                    os.remove(file_path)
                    self.logger.info(f"Removed old backup: {filename}")
```

---

*Monitoring and maintenance procedures are continuously refined to ensure system reliability*