"""
Advanced API versioning and migration system
"""
import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable, Union
from dataclasses import dataclass, asdict
from enum import Enum
import logging
from fastapi import Request, Response, HTTPException
from fastapi.routing import APIRoute
import semver

logger = logging.getLogger(__name__)

class VersionStrategy(Enum):
    """API versioning strategies"""
    URL_PATH = "url_path"  # /v1/users
    QUERY_PARAMETER = "query_param"  # /users?version=1.0
    HEADER = "header"  # Accept: application/vnd.api+json;version=1.0
    ACCEPT_HEADER = "accept_header"  # Accept: application/vnd.neuroscan.v1+json
    CONTENT_TYPE = "content_type"  # Content-Type: application/vnd.neuroscan.v1+json

class DeprecationStatus(Enum):
    """API deprecation status"""
    CURRENT = "current"
    DEPRECATED = "deprecated"
    SUNSET = "sunset"  # Will be removed
    REMOVED = "removed"

@dataclass
class ApiVersion:
    """API version definition"""
    version: str  # Semantic version (e.g., "1.2.3")
    status: DeprecationStatus
    release_date: datetime
    deprecation_date: Optional[datetime] = None
    sunset_date: Optional[datetime] = None
    changelog: Optional[str] = None
    breaking_changes: Optional[List[str]] = None
    migration_guide_url: Optional[str] = None

@dataclass
class EndpointVersion:
    """Version-specific endpoint configuration"""
    version: str
    handler: Callable
    request_transformer: Optional[Callable] = None
    response_transformer: Optional[Callable] = None
    deprecated: bool = False
    sunset_date: Optional[datetime] = None

@dataclass
class MigrationRule:
    """Migration rule for transforming between API versions"""
    from_version: str
    to_version: str
    request_transform: Optional[Callable] = None
    response_transform: Optional[Callable] = None
    field_mappings: Optional[Dict[str, str]] = None
    removed_fields: Optional[List[str]] = None
    added_fields: Optional[Dict[str, Any]] = None

class ApiVersionManager:
    """Manages API versioning, deprecation, and migrations"""
    
    def __init__(self, default_version: str = "1.0.0", strategy: VersionStrategy = VersionStrategy.HEADER):
        self.default_version = default_version
        self.strategy = strategy
        self.versions: Dict[str, ApiVersion] = {}
        self.endpoint_versions: Dict[str, Dict[str, EndpointVersion]] = {}
        self.migration_rules: List[MigrationRule] = []
        self._setup_default_versions()
    
    async def initialize(self):
        """Initialize the version manager"""
        try:
            logger.info("Initializing API Version Manager...")
            
            # Validate version configurations
            current_versions = [v for v in self.versions.values() if v.status == DeprecationStatus.CURRENT]
            deprecated_versions = [v for v in self.versions.values() if v.status == DeprecationStatus.DEPRECATED]
            
            logger.info(f"✅ Version Manager initialized with {len(current_versions)} current and {len(deprecated_versions)} deprecated versions")
            
            # Log migration rules
            if self.migration_rules:
                logger.info(f"📝 Loaded {len(self.migration_rules)} migration rules")
                
        except Exception as e:
            logger.error(f"Failed to initialize Version Manager: {e}")
            raise
    
    async def cleanup(self):
        """Cleanup version manager resources"""
        try:
            logger.info("Cleaning up Version Manager...")
            
            # Clear data structures
            self.endpoint_versions.clear()
            self.migration_rules.clear()
            
            logger.info("✅ Version Manager cleanup completed")
        except Exception as e:
            logger.error(f"Error during Version Manager cleanup: {e}")
    
    def _setup_default_versions(self):
        """Setup default API versions"""
        # Version 1.0.0 - Initial release
        self.register_version(ApiVersion(
            version="1.0.0",
            status=DeprecationStatus.DEPRECATED,
            release_date=datetime(2024, 1, 1),
            deprecation_date=datetime(2024, 6, 1),
            sunset_date=datetime(2024, 12, 31),
            changelog="Initial API release",
            breaking_changes=[],
            migration_guide_url="/docs/migration/v1-to-v2"
        ))
        
        # Version 2.0.0 - Major update
        self.register_version(ApiVersion(
            version="2.0.0",
            status=DeprecationStatus.CURRENT,
            release_date=datetime(2024, 6, 1),
            changelog="Major API restructuring with improved security and performance",
            breaking_changes=[
                "Authentication now requires OAuth2",
                "Product scan response format changed",
                "User profile endpoints restructured"
            ],
            migration_guide_url="/docs/migration/v1-to-v2"
        ))
        
        # Version 2.1.0 - Minor update
        self.register_version(ApiVersion(
            version="2.1.0",
            status=DeprecationStatus.CURRENT,
            release_date=datetime(2024, 9, 1),
            changelog="Added webhook support and enhanced analytics",
            breaking_changes=[],
            migration_guide_url="/docs/migration/v2.0-to-v2.1"
        ))
    
    def register_version(self, version: ApiVersion):
        """Register a new API version"""
        self.versions[version.version] = version
        logger.info(f"Registered API version {version.version} with status {version.status.value}")
    
    def register_endpoint_version(self, endpoint_path: str, version: str, handler: Callable, **kwargs):
        """Register a version-specific endpoint handler"""
        if endpoint_path not in self.endpoint_versions:
            self.endpoint_versions[endpoint_path] = {}
        
        endpoint_version = EndpointVersion(
            version=version,
            handler=handler,
            **kwargs
        )
        
        self.endpoint_versions[endpoint_path][version] = endpoint_version
        logger.info(f"Registered endpoint {endpoint_path} for version {version}")
    
    def add_migration_rule(self, rule: MigrationRule):
        """Add a migration rule between versions"""
        self.migration_rules.append(rule)
        logger.info(f"Added migration rule from {rule.from_version} to {rule.to_version}")
    
    def extract_version_from_request(self, request: Request) -> str:
        """Extract API version from request based on strategy"""
        version = None
        
        if self.strategy == VersionStrategy.URL_PATH:
            # Extract from URL path: /v2/users -> "2.0.0"
            path_parts = request.url.path.strip('/').split('/')
            if path_parts[0].startswith('v'):
                version_num = path_parts[0][1:]
                version = f"{version_num}.0.0"
        
        elif self.strategy == VersionStrategy.QUERY_PARAMETER:
            # Extract from query parameter: ?version=2.0.0
            version = request.query_params.get('version')
        
        elif self.strategy == VersionStrategy.HEADER:
            # Extract from custom header: X-API-Version: 2.0.0
            version = request.headers.get('X-API-Version')
        
        elif self.strategy == VersionStrategy.ACCEPT_HEADER:
            # Extract from Accept header: Accept: application/vnd.neuroscan.v2+json
            accept_header = request.headers.get('Accept', '')
            if 'vnd.neuroscan.v' in accept_header:
                import re
                match = re.search(r'vnd\.neuroscan\.v(\d+)', accept_header)
                if match:
                    version_num = match.group(1)
                    version = f"{version_num}.0.0"
        
        elif self.strategy == VersionStrategy.CONTENT_TYPE:
            # Extract from Content-Type header: Content-Type: application/vnd.neuroscan.v2+json
            content_type = request.headers.get('Content-Type', '')
            if 'vnd.neuroscan.v' in content_type:
                import re
                match = re.search(r'vnd\.neuroscan\.v(\d+)', content_type)
                if match:
                    version_num = match.group(1)
                    version = f"{version_num}.0.0"
        
        # Return version or default
        return version or self.default_version
    
    def get_compatible_version(self, requested_version: str, endpoint_path: str) -> Optional[str]:
        """Find the best compatible version for an endpoint"""
        if endpoint_path not in self.endpoint_versions:
            return None
        
        available_versions = list(self.endpoint_versions[endpoint_path].keys())
        
        # Exact match
        if requested_version in available_versions:
            return requested_version
        
        # Find highest compatible version
        try:
            requested_sem_ver = semver.VersionInfo.parse(requested_version)
            compatible_versions = []
            
            for version in available_versions:
                try:
                    version_sem_ver = semver.VersionInfo.parse(version)
                    # Compatible if major version matches and minor/patch are >= requested
                    if (version_sem_ver.major == requested_sem_ver.major and 
                        version_sem_ver >= requested_sem_ver):
                        compatible_versions.append((version, version_sem_ver))
                except ValueError:
                    continue
            
            if compatible_versions:
                # Return the lowest compatible version
                compatible_versions.sort(key=lambda x: x[1])
                return compatible_versions[0][0]
        
        except ValueError:
            # Fallback to exact string matching
            pass
        
        return None
    
    async def apply_request_transformation(self, request_data: Any, from_version: str, to_version: str) -> Any:
        """Apply request transformation between versions"""
        # Find migration rule
        migration_rule = None
        for rule in self.migration_rules:
            if rule.from_version == from_version and rule.to_version == to_version:
                migration_rule = rule
                break
        
        if not migration_rule:
            return request_data
        
        transformed_data = request_data
        
        # Apply field mappings
        if migration_rule.field_mappings and isinstance(transformed_data, dict):
            for old_field, new_field in migration_rule.field_mappings.items():
                if old_field in transformed_data:
                    transformed_data[new_field] = transformed_data.pop(old_field)
        
        # Remove deprecated fields
        if migration_rule.removed_fields and isinstance(transformed_data, dict):
            for field in migration_rule.removed_fields:
                transformed_data.pop(field, None)
        
        # Add new fields with default values
        if migration_rule.added_fields and isinstance(transformed_data, dict):
            for field, default_value in migration_rule.added_fields.items():
                if field not in transformed_data:
                    transformed_data[field] = default_value
        
        # Apply custom transformation function
        if migration_rule.request_transform:
            if asyncio.iscoroutinefunction(migration_rule.request_transform):
                transformed_data = await migration_rule.request_transform(transformed_data)
            else:
                transformed_data = migration_rule.request_transform(transformed_data)
        
        return transformed_data
    
    async def apply_response_transformation(self, response_data: Any, from_version: str, to_version: str) -> Any:
        """Apply response transformation between versions"""
        # Find migration rule (reverse direction for response)
        migration_rule = None
        for rule in self.migration_rules:
            if rule.from_version == to_version and rule.to_version == from_version:
                migration_rule = rule
                break
        
        if not migration_rule:
            return response_data
        
        transformed_data = response_data
        
        # Apply custom transformation function
        if migration_rule.response_transform:
            if asyncio.iscoroutinefunction(migration_rule.response_transform):
                transformed_data = await migration_rule.response_transform(transformed_data)
            else:
                transformed_data = migration_rule.response_transform(transformed_data)
        
        return transformed_data
    
    def get_deprecation_headers(self, version: str) -> Dict[str, str]:
        """Get deprecation headers for a version"""
        headers = {}
        
        if version in self.versions:
            api_version = self.versions[version]
            
            if api_version.status == DeprecationStatus.DEPRECATED:
                headers['Deprecation'] = 'true'
                if api_version.sunset_date:
                    headers['Sunset'] = api_version.sunset_date.strftime('%a, %d %b %Y %H:%M:%S GMT')
                
                if api_version.migration_guide_url:
                    headers['Link'] = f'<{api_version.migration_guide_url}>; rel="successor-version"'
            
            elif api_version.status == DeprecationStatus.SUNSET:
                headers['Deprecation'] = 'true'
                headers['Warning'] = '299 - "API version will be removed soon"'
                if api_version.sunset_date:
                    headers['Sunset'] = api_version.sunset_date.strftime('%a, %d %b %Y %H:%M:%S GMT')
        
        return headers
    
    def validate_version_access(self, version: str) -> bool:
        """Validate if version is still accessible"""
        if version not in self.versions:
            return False
        
        api_version = self.versions[version]
        
        # Check if version is removed
        if api_version.status == DeprecationStatus.REMOVED:
            return False
        
        # Check if version has passed sunset date
        if (api_version.sunset_date and 
            datetime.utcnow() > api_version.sunset_date):
            return False
        
        return True
    
    def get_version_info(self, version: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a version"""
        if version not in self.versions:
            return None
        
        api_version = self.versions[version]
        return {
            'version': api_version.version,
            'status': api_version.status.value,
            'release_date': api_version.release_date.isoformat(),
            'deprecation_date': api_version.deprecation_date.isoformat() if api_version.deprecation_date else None,
            'sunset_date': api_version.sunset_date.isoformat() if api_version.sunset_date else None,
            'changelog': api_version.changelog,
            'breaking_changes': api_version.breaking_changes or [],
            'migration_guide_url': api_version.migration_guide_url
        }
    
    def list_all_versions(self) -> List[Dict[str, Any]]:
        """List all available API versions"""
        return [self.get_version_info(version) for version in sorted(self.versions.keys())]
    
    def get_current_versions(self) -> List[str]:
        """Get list of current (non-deprecated) versions"""
        return [
            version for version, api_version in self.versions.items()
            if api_version.status == DeprecationStatus.CURRENT
        ]

class VersionedRoute(APIRoute):
    """Custom route class that handles API versioning"""
    
    def __init__(self, path: str, endpoint: Callable, version_manager: ApiVersionManager, **kwargs):
        super().__init__(path, endpoint, **kwargs)
        self.version_manager = version_manager
    
    def get_route_handler(self) -> Callable:
        """Override route handler to add versioning logic"""
        original_route_handler = super().get_route_handler()
        
        async def versioned_route_handler(request: Request) -> Response:
            # Extract version from request
            requested_version = self.version_manager.extract_version_from_request(request)
            
            # Validate version access
            if not self.version_manager.validate_version_access(requested_version):
                raise HTTPException(
                    status_code=410,
                    detail=f"API version {requested_version} is no longer available"
                )
            
            # Find compatible version for this endpoint
            endpoint_path = request.url.path
            compatible_version = self.version_manager.get_compatible_version(requested_version, endpoint_path)
            
            if not compatible_version:
                # Use default handler
                response = await original_route_handler(request)
            else:
                # Use version-specific handler if available
                endpoint_version = self.version_manager.endpoint_versions[endpoint_path][compatible_version]
                
                # Apply request transformation if needed
                if endpoint_version.request_transformer:
                    # This would need to be integrated with request parsing
                    pass
                
                # Call version-specific handler
                response = await endpoint_version.handler(request)
                
                # Apply response transformation if needed
                if endpoint_version.response_transformer:
                    # This would need to be integrated with response formatting
                    pass
            
            # Add deprecation headers
            deprecation_headers = self.version_manager.get_deprecation_headers(requested_version)
            for header_name, header_value in deprecation_headers.items():
                response.headers[header_name] = header_value
            
            # Add version info header
            response.headers['X-API-Version'] = requested_version
            
            return response
        
        return versioned_route_handler

# Migration transformation functions
def transform_user_v1_to_v2(data: Dict[str, Any]) -> Dict[str, Any]:
    """Transform user data from v1 to v2 format"""
    transformed = data.copy()
    
    # Rename fields
    if 'name' in transformed:
        transformed['display_name'] = transformed.pop('name')
    
    # Add new required fields with defaults
    if 'profile' not in transformed:
        transformed['profile'] = {
            'avatar_url': None,
            'bio': None,
            'preferences': {}
        }
    
    # Transform nested structures
    if 'settings' in transformed:
        transformed['user_preferences'] = transformed.pop('settings')
    
    return transformed

def transform_product_scan_v1_to_v2(data: Dict[str, Any]) -> Dict[str, Any]:
    """Transform product scan data from v1 to v2 format"""
    transformed = data.copy()
    
    # Restructure scan result
    if 'scan_status' in transformed:
        transformed['result'] = {
            'status': transformed.pop('scan_status'),
            'confidence': transformed.pop('confidence', 1.0),
            'metadata': {}
        }
    
    # Add new security fields
    if 'security_info' not in transformed:
        transformed['security_info'] = {
            'threat_level': 'low',
            'verified': True,
            'scan_engine_version': '2.0.0'
        }
    
    return transformed

# Usage example for setting up versioning
def setup_api_versioning() -> ApiVersionManager:
    """Setup API versioning with migration rules"""
    version_manager = ApiVersionManager(
        default_version="2.1.0",
        strategy=VersionStrategy.HEADER
    )
    
    # Add migration rules
    version_manager.add_migration_rule(MigrationRule(
        from_version="1.0.0",
        to_version="2.0.0",
        request_transform=transform_user_v1_to_v2,
        field_mappings={
            'user_id': 'id',
            'created': 'created_at'
        },
        removed_fields=['legacy_field'],
        added_fields={
            'api_version': '2.0.0',
            'migrated': True
        }
    ))
    
    version_manager.add_migration_rule(MigrationRule(
        from_version="1.0.0",
        to_version="2.0.0",
        request_transform=transform_product_scan_v1_to_v2,
        field_mappings={
            'product_code': 'product_id',
            'scan_time': 'scanned_at'
        }
    ))
    
    return version_manager

# Decorator for version-specific endpoints
def version_endpoint(version: str, version_manager: ApiVersionManager):
    """Decorator to mark endpoint as version-specific"""
    def decorator(func: Callable):
        def wrapper(*args, **kwargs):
            # Register this endpoint version
            endpoint_path = func.__name__  # This would need to be the actual path
            version_manager.register_endpoint_version(endpoint_path, version, func)
            return func(*args, **kwargs)
        return wrapper
    return decorator


# Global version manager instance
version_manager = setup_api_versioning()
