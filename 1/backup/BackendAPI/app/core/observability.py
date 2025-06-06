#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Production monitoring dashboard and observability system
"""

from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import defaultdict, deque
import time
import json
import asyncio
import logging
import psutil
import docker
import redis
import psycopg2
from pathlib import Path
import statistics

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class ServiceHealth:
    """Service health status"""
    service_name: str
    status: str  # healthy, degraded, unhealthy, unknown
    response_time_ms: float
    error_rate: float
    last_check: datetime
    details: Dict[str, Any] = field(default_factory=dict)
    uptime_seconds: float = 0
    version: Optional[str] = None
    
    @property
    def is_healthy(self) -> bool:
        """Check if service is healthy"""
        return self.status == "healthy"


@dataclass
class SystemMetrics:
    """System-level metrics"""
    timestamp: datetime
    cpu_percent: float
    memory_percent: float
    disk_percent: float
    network_io: Dict[str, int]
    disk_io: Dict[str, int]
    load_average: Tuple[float, float, float]
    process_count: int
    open_files: int


@dataclass
class DatabaseMetrics:
    """Database-specific metrics"""
    timestamp: datetime
    active_connections: int
    max_connections: int
    database_size_mb: float
    cache_hit_ratio: float
    transactions_per_second: float
    slow_queries: int
    locks_count: int
    replication_lag_ms: Optional[float] = None


class SystemMonitor:
    """System-level monitoring"""
    
    def __init__(self):
        self.docker_client = None
        self.redis_client = None
        self.db_connection = None
        self._init_connections()
    
    def _init_connections(self):
        """Initialize monitoring connections"""
        try:
            self.docker_client = docker.from_env()
        except Exception as e:
            logger.warning(f"Could not connect to Docker: {e}")
        
        try:
            self.redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)
            self.redis_client.ping()
        except Exception as e:
            logger.warning(f"Could not connect to Redis: {e}")
            self.redis_client = None
        
        try:
            self.db_connection = psycopg2.connect(
                host="localhost",
                port=5432,
                database="neuroscan_db",
                user="neuroscan",
                password="password"  # This should come from config
            )
        except Exception as e:
            logger.warning(f"Could not connect to database: {e}")
    
    def get_system_metrics(self) -> SystemMetrics:
        """Get current system metrics"""
        try:
            # CPU and memory
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            
            # Disk usage
            disk = psutil.disk_usage('/')
            disk_percent = disk.percent
            
            # Network I/O
            network_io = psutil.net_io_counters()._asdict()
            
            # Disk I/O
            disk_io = psutil.disk_io_counters()._asdict()
            
            # Load average
            load_avg = psutil.getloadavg()
            
            # Process info
            process_count = len(psutil.pids())
            
            # Open files (approximate)
            try:
                open_files = len(psutil.Process().open_files())
            except:
                open_files = 0
            
            return SystemMetrics(
                timestamp=datetime.now(),
                cpu_percent=cpu_percent,
                memory_percent=memory.percent,
                disk_percent=disk_percent,
                network_io=network_io,
                disk_io=disk_io,
                load_average=load_avg,
                process_count=process_count,
                open_files=open_files
            )
            
        except Exception as e:
            logger.error(f"Error getting system metrics: {e}")
            return SystemMetrics(
                timestamp=datetime.now(),
                cpu_percent=0,
                memory_percent=0,
                disk_percent=0,
                network_io={},
                disk_io={},
                load_average=(0, 0, 0),
                process_count=0,
                open_files=0
            )
    
    def get_container_metrics(self) -> Dict[str, Dict]:
        """Get Docker container metrics"""
        if not self.docker_client:
            return {}
        
        container_metrics = {}
        
        try:
            containers = self.docker_client.containers.list()
            
            for container in containers:
                try:
                    stats = container.stats(stream=False)
                    
                    # Calculate CPU percentage
                    cpu_delta = stats['cpu_stats']['cpu_usage']['total_usage'] - \
                               stats['precpu_stats']['cpu_usage']['total_usage']
                    system_delta = stats['cpu_stats']['system_cpu_usage'] - \
                                  stats['precpu_stats']['system_cpu_usage']
                    
                    cpu_percent = 0
                    if system_delta > 0:
                        cpu_percent = (cpu_delta / system_delta) * 100
                    
                    # Calculate memory usage
                    memory_usage = stats['memory_stats'].get('usage', 0)
                    memory_limit = stats['memory_stats'].get('limit', 0)
                    memory_percent = 0
                    if memory_limit > 0:
                        memory_percent = (memory_usage / memory_limit) * 100
                    
                    # Network I/O
                    network_rx = 0
                    network_tx = 0
                    if 'networks' in stats:
                        for network in stats['networks'].values():
                            network_rx += network.get('rx_bytes', 0)
                            network_tx += network.get('tx_bytes', 0)
                    
                    container_metrics[container.name] = {
                        'status': container.status,
                        'cpu_percent': round(cpu_percent, 2),
                        'memory_usage_mb': round(memory_usage / 1024 / 1024, 2),
                        'memory_percent': round(memory_percent, 2),
                        'network_rx_mb': round(network_rx / 1024 / 1024, 2),
                        'network_tx_mb': round(network_tx / 1024 / 1024, 2),
                        'created': container.attrs['Created'],
                        'image': container.image.tags[0] if container.image.tags else 'unknown'
                    }
                    
                except Exception as e:
                    logger.error(f"Error getting stats for container {container.name}: {e}")
                    container_metrics[container.name] = {
                        'status': container.status,
                        'error': str(e)
                    }
            
        except Exception as e:
            logger.error(f"Error getting container metrics: {e}")
        
        return container_metrics
    
    def get_database_metrics(self) -> Optional[DatabaseMetrics]:
        """Get database metrics"""
        if not self.db_connection:
            return None
        
        try:
            with self.db_connection.cursor() as cursor:
                # Active connections
                cursor.execute("SELECT count(*) FROM pg_stat_activity WHERE state = 'active';")
                active_connections = cursor.fetchone()[0]
                
                # Max connections
                cursor.execute("SHOW max_connections;")
                max_connections = int(cursor.fetchone()[0])
                
                # Database size
                cursor.execute("""
                    SELECT pg_size_pretty(pg_database_size('neuroscan_db'));
                """)
                db_size_str = cursor.fetchone()[0]
                # Parse size (e.g., "12 MB" -> 12.0)
                db_size_mb = float(db_size_str.split()[0]) if 'MB' in db_size_str else 0
                
                # Cache hit ratio
                cursor.execute("""
                    SELECT 
                        sum(heap_blks_hit) / (sum(heap_blks_hit) + sum(heap_blks_read)) * 100 
                    FROM pg_statio_user_tables;
                """)
                cache_hit_result = cursor.fetchone()[0]
                cache_hit_ratio = float(cache_hit_result) if cache_hit_result else 0
                
                # Transactions per second (approximation)
                cursor.execute("""
                    SELECT xact_commit + xact_rollback 
                    FROM pg_stat_database 
                    WHERE datname = 'neuroscan_db';
                """)
                total_transactions = cursor.fetchone()[0]
                tps = total_transactions / 60  # Rough approximation
                
                # Slow queries (queries running > 1 second)
                cursor.execute("""
                    SELECT count(*) 
                    FROM pg_stat_activity 
                    WHERE state = 'active' AND now() - query_start > interval '1 second';
                """)
                slow_queries = cursor.fetchone()[0]
                
                # Lock count
                cursor.execute("SELECT count(*) FROM pg_locks;")
                locks_count = cursor.fetchone()[0]
                
                return DatabaseMetrics(
                    timestamp=datetime.now(),
                    active_connections=active_connections,
                    max_connections=max_connections,
                    database_size_mb=db_size_mb,
                    cache_hit_ratio=cache_hit_ratio,
                    transactions_per_second=tps,
                    slow_queries=slow_queries,
                    locks_count=locks_count
                )
                
        except Exception as e:
            logger.error(f"Error getting database metrics: {e}")
            return None
    
    def get_redis_metrics(self) -> Optional[Dict[str, Any]]:
        """Get Redis metrics"""
        if not self.redis_client:
            return None
        
        try:
            info = self.redis_client.info()
            
            return {
                'connected_clients': info.get('connected_clients', 0),
                'used_memory_mb': info.get('used_memory', 0) / 1024 / 1024,
                'used_memory_peak_mb': info.get('used_memory_peak', 0) / 1024 / 1024,
                'keyspace_hits': info.get('keyspace_hits', 0),
                'keyspace_misses': info.get('keyspace_misses', 0),
                'total_commands_processed': info.get('total_commands_processed', 0),
                'instantaneous_ops_per_sec': info.get('instantaneous_ops_per_sec', 0),
                'uptime_in_seconds': info.get('uptime_in_seconds', 0),
                'role': info.get('role', 'unknown')
            }
            
        except Exception as e:
            logger.error(f"Error getting Redis metrics: {e}")
            return None


class ServiceHealthChecker:
    """Check health of individual services"""
    
    def __init__(self):
        self.health_checks = {
            'api': self._check_api_health,
            'database': self._check_database_health,
            'redis': self._check_redis_health,
            'frontend': self._check_frontend_health
        }
    
    async def check_all_services(self) -> Dict[str, ServiceHealth]:
        """Check health of all services"""
        results = {}
        
        for service_name, check_func in self.health_checks.items():
            try:
                results[service_name] = await check_func()
            except Exception as e:
                logger.error(f"Error checking {service_name} health: {e}")
                results[service_name] = ServiceHealth(
                    service_name=service_name,
                    status='unknown',
                    response_time_ms=0,
                    error_rate=100,
                    last_check=datetime.now(),
                    details={'error': str(e)}
                )
        
        return results
    
    async def _check_api_health(self) -> ServiceHealth:
        """Check API health"""
        import aiohttp
        
        start_time = time.time()
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get('http://localhost:8000/health', timeout=10) as response:
                    response_time = (time.time() - start_time) * 1000
                    
                    if response.status == 200:
                        data = await response.json()
                        return ServiceHealth(
                            service_name='api',
                            status='healthy',
                            response_time_ms=response_time,
                            error_rate=0,
                            last_check=datetime.now(),
                            details=data
                        )
                    else:
                        return ServiceHealth(
                            service_name='api',
                            status='degraded',
                            response_time_ms=response_time,
                            error_rate=50,
                            last_check=datetime.now(),
                            details={'status_code': response.status}
                        )
                        
        except Exception as e:
            return ServiceHealth(
                service_name='api',
                status='unhealthy',
                response_time_ms=(time.time() - start_time) * 1000,
                error_rate=100,
                last_check=datetime.now(),
                details={'error': str(e)}
            )
    
    async def _check_database_health(self) -> ServiceHealth:
        """Check database health"""
        start_time = time.time()
        
        try:
            conn = psycopg2.connect(
                host="localhost",
                port=5432,
                database="neuroscan_db",
                user="neuroscan",
                password="password",
                connect_timeout=5
            )
            
            with conn.cursor() as cursor:
                cursor.execute("SELECT 1;")
                cursor.fetchone()
            
            conn.close()
            response_time = (time.time() - start_time) * 1000
            
            return ServiceHealth(
                service_name='database',
                status='healthy',
                response_time_ms=response_time,
                error_rate=0,
                last_check=datetime.now(),
                details={'connection': 'successful'}
            )
            
        except Exception as e:
            return ServiceHealth(
                service_name='database',
                status='unhealthy',
                response_time_ms=(time.time() - start_time) * 1000,
                error_rate=100,
                last_check=datetime.now(),
                details={'error': str(e)}
            )
    
    async def _check_redis_health(self) -> ServiceHealth:
        """Check Redis health"""
        start_time = time.time()
        
        try:
            client = redis.Redis(host='localhost', port=6379, decode_responses=True)
            client.ping()
            response_time = (time.time() - start_time) * 1000
            
            return ServiceHealth(
                service_name='redis',
                status='healthy',
                response_time_ms=response_time,
                error_rate=0,
                last_check=datetime.now(),
                details={'ping': 'successful'}
            )
            
        except Exception as e:
            return ServiceHealth(
                service_name='redis',
                status='unhealthy',
                response_time_ms=(time.time() - start_time) * 1000,
                error_rate=100,
                last_check=datetime.now(),
                details={'error': str(e)}
            )
    
    async def _check_frontend_health(self) -> ServiceHealth:
        """Check frontend health"""
        import aiohttp
        
        start_time = time.time()
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get('http://localhost:3000', timeout=10) as response:
                    response_time = (time.time() - start_time) * 1000
                    
                    if response.status == 200:
                        return ServiceHealth(
                            service_name='frontend',
                            status='healthy',
                            response_time_ms=response_time,
                            error_rate=0,
                            last_check=datetime.now(),
                            details={'status_code': response.status}
                        )
                    else:
                        return ServiceHealth(
                            service_name='frontend',
                            status='degraded',
                            response_time_ms=response_time,
                            error_rate=25,
                            last_check=datetime.now(),
                            details={'status_code': response.status}
                        )
                        
        except Exception as e:
            return ServiceHealth(
                service_name='frontend',
                status='unhealthy',
                response_time_ms=(time.time() - start_time) * 1000,
                error_rate=100,
                last_check=datetime.now(),
                details={'error': str(e)}
            )


class MonitoringDashboard:
    """Production monitoring dashboard"""
    
    def __init__(self):
        self.system_monitor = SystemMonitor()
        self.health_checker = ServiceHealthChecker()
        self.metrics_history = deque(maxlen=1440)  # 24 hours of minute-by-minute data
        self.health_history = deque(maxlen=1440)
        self.collection_interval = 60  # seconds
        self._running = False
    
    async def initialize(self):
        """Initialize the monitoring dashboard"""
        try:
            logger.info("Initializing Monitoring Dashboard...")
            
            # Test system monitoring connections
            system_metrics = self.system_monitor.get_system_metrics()
            logger.info(f"✅ System monitoring ready - CPU: {system_metrics.cpu_percent}%, Memory: {system_metrics.memory_percent}%")
            
            # Test service health checks
            health_status = await self.health_checker.check_all_services()
            healthy_services = sum(1 for h in health_status.values() if h.is_healthy)
            total_services = len(health_status)
            logger.info(f"✅ Health monitoring ready - {healthy_services}/{total_services} services healthy")
            
            logger.info("✅ Monitoring Dashboard initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Monitoring Dashboard: {e}")
            raise
    
    async def cleanup(self):
        """Cleanup monitoring dashboard resources"""
        try:
            logger.info("Cleaning up Monitoring Dashboard...")
            
            # Stop monitoring if running
            if self._running:
                self.stop()
            
            # Close system monitor connections
            if hasattr(self.system_monitor, 'db_connection') and self.system_monitor.db_connection:
                self.system_monitor.db_connection.close()
            
            # Clear history data
            self.metrics_history.clear()
            self.health_history.clear()
            
            logger.info("✅ Monitoring Dashboard cleanup completed")
        except Exception as e:
            logger.error(f"Error during Monitoring Dashboard cleanup: {e}")
    
    async def start(self):
        """Start monitoring collection"""
        self._running = True
        logger.info("Starting monitoring dashboard")
        
        while self._running:
            try:
                # Collect system metrics
                system_metrics = self.system_monitor.get_system_metrics()
                container_metrics = self.system_monitor.get_container_metrics()
                database_metrics = self.system_monitor.get_database_metrics()
                redis_metrics = self.system_monitor.get_redis_metrics()
                
                # Collect service health
                service_health = await self.health_checker.check_all_services()
                
                # Store metrics
                self.metrics_history.append({
                    'timestamp': datetime.now().isoformat(),
                    'system': system_metrics.__dict__,
                    'containers': container_metrics,
                    'database': database_metrics.__dict__ if database_metrics else None,
                    'redis': redis_metrics
                })
                
                self.health_history.append({
                    'timestamp': datetime.now().isoformat(),
                    'services': {name: health.__dict__ for name, health in service_health.items()}
                })
                
                # Wait for next collection
                await asyncio.sleep(self.collection_interval)
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(5)
    
    def stop(self):
        """Stop monitoring collection"""
        self._running = False
        logger.info("Stopping monitoring dashboard")
    
    def get_current_status(self) -> Dict[str, Any]:
        """Get current system status"""
        if not self.metrics_history or not self.health_history:
            return {'status': 'initializing'}
        
        latest_metrics = self.metrics_history[-1]
        latest_health = self.health_history[-1]
        
        # Calculate overall health
        services = latest_health['services']
        healthy_services = sum(1 for service in services.values() if service['status'] == 'healthy')
        total_services = len(services)
        overall_health = 'healthy' if healthy_services == total_services else 'degraded'
        
        if healthy_services < total_services * 0.5:
            overall_health = 'unhealthy'
        
        return {
            'overall_health': overall_health,
            'healthy_services': healthy_services,
            'total_services': total_services,
            'timestamp': latest_metrics['timestamp'],
            'system_metrics': latest_metrics['system'],
            'service_health': services,
            'container_metrics': latest_metrics['containers'],
            'database_metrics': latest_metrics['database'],
            'redis_metrics': latest_metrics['redis']
        }
    
    def get_metrics_history(self, hours: int = 1) -> List[Dict]:
        """Get metrics history for specified hours"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        return [
            metric for metric in self.metrics_history
            if datetime.fromisoformat(metric['timestamp']) > cutoff_time
        ]
    
    def get_health_trends(self, hours: int = 24) -> Dict[str, Any]:
        """Get health trends and statistics"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        relevant_health = [
            health for health in self.health_history
            if datetime.fromisoformat(health['timestamp']) > cutoff_time
        ]
        
        if not relevant_health:
            return {}
        
        # Calculate service availability
        service_stats = defaultdict(lambda: {'total_checks': 0, 'healthy_checks': 0, 'response_times': []})
        
        for health_point in relevant_health:
            for service_name, service_data in health_point['services'].items():
                stats = service_stats[service_name]
                stats['total_checks'] += 1
                
                if service_data['status'] == 'healthy':
                    stats['healthy_checks'] += 1
                
                stats['response_times'].append(service_data['response_time_ms'])
        
        # Calculate final statistics
        trends = {}
        for service_name, stats in service_stats.items():
            availability = (stats['healthy_checks'] / stats['total_checks']) * 100
            avg_response_time = statistics.mean(stats['response_times']) if stats['response_times'] else 0
            
            trends[service_name] = {
                'availability_percent': round(availability, 2),
                'average_response_time_ms': round(avg_response_time, 2),
                'total_checks': stats['total_checks'],
                'healthy_checks': stats['healthy_checks']
            }
        
        return trends
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary"""
        if len(self.metrics_history) < 2:
            return {}
        
        recent_metrics = list(self.metrics_history)[-60:]  # Last hour
        
        # Calculate averages
        cpu_values = [m['system']['cpu_percent'] for m in recent_metrics]
        memory_values = [m['system']['memory_percent'] for m in recent_metrics]
        disk_values = [m['system']['disk_percent'] for m in recent_metrics]
        
        return {
            'cpu': {
                'current': cpu_values[-1] if cpu_values else 0,
                'average': statistics.mean(cpu_values) if cpu_values else 0,
                'peak': max(cpu_values) if cpu_values else 0
            },
            'memory': {
                'current': memory_values[-1] if memory_values else 0,
                'average': statistics.mean(memory_values) if memory_values else 0,
                'peak': max(memory_values) if memory_values else 0
            },
            'disk': {
                'current': disk_values[-1] if disk_values else 0,
                'average': statistics.mean(disk_values) if disk_values else 0,
                'peak': max(disk_values) if disk_values else 0
            }
        }


# Global monitoring dashboard instance
monitoring_dashboard = MonitoringDashboard()


# Functions for external use
async def start_monitoring():
    """Start the monitoring dashboard"""
    await monitoring_dashboard.start()


def stop_monitoring():
    """Stop the monitoring dashboard"""
    monitoring_dashboard.stop()


def get_system_status() -> Dict[str, Any]:
    """Get current system status"""
    return monitoring_dashboard.get_current_status()


def get_health_trends(hours: int = 24) -> Dict[str, Any]:
    """Get service health trends"""
    return monitoring_dashboard.get_health_trends(hours)


def get_performance_summary() -> Dict[str, Any]:
    """Get performance summary"""
    return monitoring_dashboard.get_performance_summary()


def get_metrics_history(hours: int = 1) -> List[Dict]:
    """Get metrics history"""
    return monitoring_dashboard.get_metrics_history(hours)


# Alias for compatibility with main.py
observability_dashboard = monitoring_dashboard
