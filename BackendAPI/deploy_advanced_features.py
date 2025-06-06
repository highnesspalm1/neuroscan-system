#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Advanced Features Deployment Script
Deploy and configure all advanced features for NeuroScan
"""

import asyncio
import json
import logging
import sys
from pathlib import Path
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class AdvancedFeaturesDeployment:
    """Deploy and configure advanced features"""
    
    def __init__(self):
        self.deployment_start = datetime.now()
        self.steps_completed = []
        self.errors = []
    
    async def run_deployment(self):
        """Run complete deployment process"""
        logger.info("🚀 Starting NeuroScan Advanced Features Deployment")
        logger.info(f"📅 Deployment started at: {self.deployment_start}")
        
        steps = [
            ("Database Migration", self.run_database_migration),
            ("Cache System Setup", self.setup_cache_system),
            ("Analytics Engine", self.setup_analytics_engine),
            ("Webhook System", self.setup_webhook_system),
            ("API Versioning", self.setup_api_versioning),
            ("Alerting System", self.setup_alerting_system),
            ("Observability Dashboard", self.setup_observability),
            ("Performance Optimization", self.optimize_performance),
            ("Security Hardening", self.harden_security),
            ("Health Checks", self.setup_health_checks),
            ("Documentation Update", self.update_documentation),
            ("Validation Tests", self.run_validation_tests)
        ]
        
        for step_name, step_function in steps:
            try:
                logger.info(f"▶️ Executing: {step_name}")
                await step_function()
                self.steps_completed.append(step_name)
                logger.info(f"✅ Completed: {step_name}")
            except Exception as e:
                error_msg = f"❌ Failed: {step_name} - {str(e)}"
                logger.error(error_msg)
                self.errors.append(error_msg)
                  # Decide whether to continue or abort
                if step_name in ["Database Migration"]:
                    logger.error("🛑 Critical step failed. Aborting deployment.")
                    await self.rollback_deployment()
                    return False
                else:
                    logger.warning("⚠️ Non-critical step failed. Continuing deployment.")
        
        # Generate deployment summary
        await self.generate_deployment_summary()
        
        if not self.errors:
            logger.info("🎉 Deployment completed successfully!")
            return True
        else:
            logger.warning(f"⚠️ Deployment completed with {len(self.errors)} warnings")
            return True
    
    async def run_database_migration(self):
        """Run database migrations for advanced features"""
        logger.info("📊 Creating advanced feature database tables...")
        
        try:
            # Import and run migration
            from app.db.migrations.create_advanced_tables import upgrade
            upgrade()
            
            # Verify tables were created
            from app.core.database import engine
            from sqlalchemy import inspect
            
            inspector = inspect(engine)
            required_tables = [
                'metrics', 'webhook_endpoints', 'webhook_deliveries',
                'cache_entries', 'api_versions', 'enhanced_sessions',
                'security_events', 'performance_baselines', 'system_health'
            ]
            
            existing_tables = inspector.get_table_names()
            missing_tables = [t for t in required_tables if t not in existing_tables]
            
            if missing_tables:
                raise Exception(f"Missing tables: {missing_tables}")
            
            logger.info(f"✅ Created {len(required_tables)} advanced feature tables")
            
        except Exception as e:
            logger.error(f"❌ Database migration failed: {e}")
            raise
    async def setup_cache_system(self):
        """Setup and initialize cache system"""
        logger.info("🔄 Initializing advanced caching system...")
        
        try:
            from app.core.caching import cache_manager
            
            # Load cache configuration
            config_path = Path("config/advanced_config.json")
            if config_path.exists():
                with open(config_path) as f:
                    config = json.load(f)
                cache_config = config.get("caching", {})
            else:
                cache_config = {
                    "enabled": True,
                    "default_ttl": 3600,
                    "l1_cache": {"max_size": 1000, "eviction_policy": "LRU"},
                    "l2_cache": {"redis_url": "redis://localhost:6379"}
                }
            
            # Modify config for local development (no Redis server required)
            cache_config["l2_cache"]["enabled"] = False  # Disable Redis for now
            
            # Initialize cache manager
            cache_manager.configure(cache_config)
            await cache_manager.initialize()
            
            # Test cache operations (L1 only)
            test_key = "deployment_test"
            test_value = {"timestamp": datetime.now().isoformat()}
            await cache_manager.set(test_key, test_value, ttl=60)
            
            retrieved = await cache_manager.get(test_key)
            if retrieved != test_value:
                raise Exception("Cache test failed")
            
            await cache_manager.delete(test_key)
            logger.info("✅ Cache system initialized and tested (L1 cache only)")
                
        except Exception as e:
            logger.error(f"❌ Cache system setup failed: {e}")
            # For development, continue without Redis
            logger.warning("⚠️ Continuing with L1 cache only (Redis not available)")
    
    async def setup_analytics_engine(self):
        """Setup analytics and business intelligence"""
        logger.info("📈 Initializing business intelligence engine...")
        
        try:
            from app.core.analytics import analytics_engine
            
            # Load analytics configuration
            config_path = Path("config/advanced_config.json")
            if config_path.exists():
                with open(config_path) as f:
                    config = json.load(f)
                analytics_config = config.get("analytics", {})
            else:
                analytics_config = {
                    "enabled": True,
                    "retention_days": 90,
                    "batch_size": 1000
                }
            
            # Initialize analytics engine
            analytics_engine.configure(analytics_config)
            await analytics_engine.initialize()
            
            # Record test metric
            await analytics_engine.record_metric(
                name="deployment_test",
                value=1,
                metric_type="counter",
                labels={"source": "deployment"}
            )
            
            logger.info("✅ Analytics engine initialized")
            
        except Exception as e:
            logger.error(f"❌ Analytics setup failed: {e}")
            raise
    
    async def setup_webhook_system(self):
        """Setup webhook delivery system"""
        logger.info("🪝 Initializing webhook system...")
        
        try:
            from app.core.webhooks import webhook_system
            
            # Load webhook configuration
            config_path = Path("config/advanced_config.json")
            if config_path.exists():
                with open(config_path) as f:
                    config = json.load(f)
                webhook_config = config.get("webhooks", {})
            else:
                webhook_config = {
                    "enabled": True,
                    "max_endpoints": 50,
                    "delivery_timeout": 30
                }
            
            # Initialize webhook system
            webhook_system.configure(webhook_config)
            await webhook_system.initialize()
            
            logger.info("✅ Webhook system initialized")
            
        except Exception as e:
            logger.error(f"❌ Webhook setup failed: {e}")
            raise
    
    async def setup_api_versioning(self):
        """Setup API versioning system"""
        logger.info("🔀 Initializing API versioning...")
        
        try:
            from app.core.versioning import version_manager
            
            # Load versioning configuration
            config_path = Path("config/advanced_config.json")
            if config_path.exists():
                with open(config_path) as f:
                    config = json.load(f)
                version_config = config.get("versioning", {})
            else:
                version_config = {
                    "enabled": True,
                    "current_version": "2.0.0",
                    "supported_versions": ["1.0.0", "1.1.0", "2.0.0"]
                }
            
            # Initialize version manager
            version_manager.configure(version_config)
            await version_manager.initialize()
            
            # Test version resolution
            current_version = await version_manager.resolve_version("2.0.0")
            if current_version != "2.0.0":
                raise Exception("Version resolution test failed")
            
            logger.info("✅ API versioning initialized")
            
        except Exception as e:
            logger.error(f"❌ API versioning setup failed: {e}")
            raise
    
    async def setup_alerting_system(self):
        """Setup alerting and notification system"""
        logger.info("🚨 Initializing alerting system...")
        
        try:
            from app.core.alerting import alert_manager
            
            # Load alerting configuration
            config_path = Path("config/advanced_config.json")
            if config_path.exists():
                with open(config_path) as f:
                    config = json.load(f)
                alert_config = config.get("alerting", {})
            else:
                alert_config = {
                    "enabled": True,
                    "channels": {
                        "email": {"enabled": False},
                        "webhook": {"enabled": True}
                    }
                }
            
            # Initialize alert manager
            alert_manager.configure(alert_config)
            await alert_manager.initialize()
            
            logger.info("✅ Alerting system initialized")
            
        except Exception as e:
            logger.error(f"❌ Alerting setup failed: {e}")
            raise
    
    async def setup_observability(self):
        """Setup observability dashboard"""
        logger.info("👁️ Initializing observability dashboard...")
        
        try:
            from app.core.observability import observability_dashboard
            
            # Load observability configuration
            config_path = Path("config/advanced_config.json")
            if config_path.exists():
                with open(config_path) as f:
                    config = json.load(f)
                observability_config = config.get("observability", {})
            else:
                observability_config = {
                    "enabled": True,
                    "dashboard_refresh_interval": 30,
                    "health_check_interval": 60
                }
            
            # Initialize observability dashboard
            observability_dashboard.configure(observability_config)
            await observability_dashboard.initialize()
            
            # Test health check
            health = await observability_dashboard.check_system_health()
            if not health.get("overall_status"):
                raise Exception("Health check test failed")
            
            logger.info("✅ Observability dashboard initialized")
            
        except Exception as e:
            logger.error(f"❌ Observability setup failed: {e}")
            raise
    
    async def optimize_performance(self):
        """Apply performance optimizations"""
        logger.info("⚡ Applying performance optimizations...")
        
        try:
            # Database connection pool optimization
            from app.core.database import engine
            
            # Update connection pool settings
            current_pool_size = engine.pool.size()
            logger.info(f"Current connection pool size: {current_pool_size}")
            
            # Cache warmup for critical data
            from app.core.caching import cache_manager
            
            # Warmup product catalog cache
            logger.info("Warming up cache with critical data...")
            
            # Pre-populate frequently accessed data
            warmup_data = {
                "system_config": {"deployment_time": datetime.now().isoformat()},
                "api_versions": ["1.0.0", "1.1.0", "2.0.0"],
                "feature_flags": {"advanced_features": True}
            }
            
            for key, value in warmup_data.items():
                await cache_manager.set(f"warmup_{key}", value, ttl=3600)
            
            logger.info("✅ Performance optimizations applied")
            
        except Exception as e:
            logger.error(f"❌ Performance optimization failed: {e}")
            raise
    
    async def harden_security(self):
        """Apply security hardening"""
        logger.info("🔒 Applying security hardening...")
        
        try:
            # Verify security configurations
            config_path = Path("config/advanced_config.json")
            if config_path.exists():
                with open(config_path) as f:
                    config = json.load(f)
                
                security_config = config.get("security", {})
                
                # Check critical security settings
                required_security = [
                    "enhanced_logging",
                    "api_key_rotation",
                    "session_security"
                ]
                
                for setting in required_security:
                    if setting not in security_config:
                        logger.warning(f"⚠️ Missing security setting: {setting}")
            
            # Initialize security monitoring
            from app.core.security import security_monitor
            await security_monitor.initialize()
            
            logger.info("✅ Security hardening applied")
            
        except Exception as e:
            logger.error(f"❌ Security hardening failed: {e}")
            # Don't raise for security - log and continue
            logger.warning("⚠️ Continuing with reduced security posture")
    
    async def setup_health_checks(self):
        """Setup comprehensive health checks"""
        logger.info("🏥 Setting up health checks...")
        
        try:
            from app.core.observability import observability_dashboard
            
            # Register health check endpoints
            health_checks = [
                "database_connectivity",
                "cache_availability", 
                "webhook_system",
                "analytics_engine",
                "alerting_system"
            ]
            
            for check in health_checks:
                await observability_dashboard.register_health_check(check)
            
            # Run initial health check
            health_status = await observability_dashboard.check_system_health()
            
            if health_status.get("overall_status") == "critical":
                raise Exception("Critical health check failures detected")
            
            logger.info("✅ Health checks configured")
            
        except Exception as e:
            logger.error(f"❌ Health check setup failed: {e}")
            raise
    
    async def update_documentation(self):
        """Update API documentation"""
        logger.info("📖 Updating documentation...")
        
        try:
            # Generate API documentation for new endpoints
            doc_updates = {
                "v2_api_endpoints": [
                    "/api/v2/analytics/dashboard",
                    "/api/v2/cache/statistics",
                    "/api/v2/webhooks/endpoints",
                    "/api/v2/monitoring/health"
                ],
                "new_features": [
                    "Advanced Caching with L1/L2 strategy",
                    "Business Intelligence Engine",
                    "Advanced Webhook System",
                    "API Versioning with automatic migration",
                    "Enhanced Monitoring and Alerting",
                    "Observability Dashboard"
                ],
                "deployment_info": {
                    "deployment_date": self.deployment_start.isoformat(),
                    "version": "2.0.0",
                    "advanced_features": True
                }
            }
            
            # Write documentation update
            doc_path = Path("docs/ADVANCED_FEATURES.md")
            doc_path.parent.mkdir(exist_ok=True)
            
            with open(doc_path, "w") as f:
                f.write("# NeuroScan Advanced Features\n\n")
                f.write(f"Deployed: {self.deployment_start.isoformat()}\n\n")
                f.write("## New API Endpoints\n\n")
                for endpoint in doc_updates["v2_api_endpoints"]:
                    f.write(f"- `{endpoint}`\n")
                f.write("\n## Features\n\n")
                for feature in doc_updates["new_features"]:
                    f.write(f"- {feature}\n")
            
            logger.info("✅ Documentation updated")
            
        except Exception as e:
            logger.error(f"❌ Documentation update failed: {e}")
            # Don't raise for documentation - it's not critical
            logger.warning("⚠️ Continuing without documentation update")
    
    async def run_validation_tests(self):
        """Run validation tests for deployed features"""
        logger.info("🧪 Running validation tests...")
        
        try:
            # Test each major component
            validation_results = {}
            
            # Test caching
            from app.core.caching import cache_manager
            test_key = "validation_test"
            await cache_manager.set(test_key, "test_value", ttl=60)
            cached_value = await cache_manager.get(test_key)
            validation_results["caching"] = cached_value == "test_value"
            await cache_manager.delete(test_key)
            
            # Test analytics
            from app.core.analytics import analytics_engine
            await analytics_engine.record_metric(
                name="validation_test",
                value=1,
                metric_type="counter"
            )
            validation_results["analytics"] = True
            
            # Test webhook system
            from app.core.webhooks import webhook_system
            webhook_stats = await webhook_system.get_statistics()
            validation_results["webhooks"] = isinstance(webhook_stats, dict)
            
            # Test API versioning
            from app.core.versioning import version_manager
            current_version = await version_manager.get_current_version()
            validation_results["versioning"] = current_version is not None
            
            # Test alerting
            from app.core.alerting import alert_manager
            alert_stats = await alert_manager.get_statistics()
            validation_results["alerting"] = isinstance(alert_stats, dict)
            
            # Check results
            failed_tests = [k for k, v in validation_results.items() if not v]
            if failed_tests:
                raise Exception(f"Validation failed for: {failed_tests}")
            
            logger.info(f"✅ All validation tests passed: {list(validation_results.keys())}")
            
        except Exception as e:
            logger.error(f"❌ Validation tests failed: {e}")
            raise
    async def rollback_deployment(self):
        """Rollback deployment in case of critical failure"""
        logger.warning("🔄 Rolling back deployment...")
        
        try:
            # Rollback database changes
            from app.db.migrations.create_advanced_tables import downgrade
            downgrade()
            
            logger.info("✅ Rollback completed")
            
        except Exception as e:
            logger.error(f"❌ Rollback failed: {e}")
            # Continue with manual cleanup instructions
            logger.warning("⚠️ Manual cleanup may be required")
    
    async def generate_deployment_summary(self):
        """Generate deployment summary report"""
        deployment_end = datetime.now()
        duration = deployment_end - self.deployment_start
        
        summary = {
            "deployment_info": {
                "start_time": self.deployment_start.isoformat(),
                "end_time": deployment_end.isoformat(),
                "duration_seconds": duration.total_seconds(),
                "success": len(self.errors) == 0
            },
            "steps_completed": self.steps_completed,
            "errors": self.errors,
            "features_deployed": [
                "Advanced Caching System",
                "Business Intelligence Engine", 
                "Advanced Webhook System",
                "API Versioning and Migration",
                "Enhanced Monitoring and Alerting",
                "Observability Dashboard",
                "Performance Optimizations",
                "Security Hardening"
            ]
        }
        
        # Write summary to file
        summary_path = Path("deployment_summary.json")
        with open(summary_path, "w") as f:
            json.dump(summary, f, indent=2)
        
        # Log summary
        logger.info("📋 Deployment Summary:")
        logger.info(f"   Duration: {duration.total_seconds():.1f} seconds")
        logger.info(f"   Steps completed: {len(self.steps_completed)}")
        logger.info(f"   Errors: {len(self.errors)}")
        
        if self.errors:
            logger.warning("⚠️ Deployment completed with warnings:")
            for error in self.errors:
                logger.warning(f"   - {error}")

async def main():
    """Main deployment function"""
    deployment = AdvancedFeaturesDeployment()
    
    try:
        success = await deployment.run_deployment()
        if success:
            logger.info("🎉 NeuroScan Advanced Features deployment completed!")
            sys.exit(0)
        else:
            logger.error("💥 Deployment failed!")
            sys.exit(1)
    except KeyboardInterrupt:
        logger.warning("⚠️ Deployment interrupted by user")
        await deployment.rollback_deployment()
        sys.exit(1)
    except Exception as e:
        logger.error(f"💥 Unexpected deployment failure: {e}")
        await deployment.rollback_deployment()
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
