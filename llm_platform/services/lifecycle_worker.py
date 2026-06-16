"""Background worker for model lifecycle management."""

import asyncio
import logging
from fastapi import FastAPI

from llm_platform.schemas.enums import LifecycleState, DeploymentStatus

logger = logging.getLogger(__name__)

async def run_lifecycle_loop(app: FastAPI):
    """Background task to enforce scale-to-zero lifecycle policies."""
    logger.info("Starting lifecycle management background worker.")
    
    # Wait a bit for the application to fully initialize
    await asyncio.sleep(5)
    
    try:
        platform = app.state.platform_application
    except AttributeError:
        logger.error("Platform application not found on app state. Worker exiting.")
        return

    while True:
        try:
            deployments = platform.registry.list_deployments()
            for deployment in deployments:
                if deployment.status != DeploymentStatus.READY:
                    continue
                    
                record = platform.registry.get_lifecycle(deployment.deployment_id)
                if not record:
                    continue
                    
                # Increment idle time by the sleep interval
                record.idle_duration_seconds += 10
                
                # Use manager.py to calculate if a state transition should occur
                updated_record = platform.lifecycle_manager.reconcile(record)
                platform.registry.upsert_lifecycle(updated_record)
                
                # Trigger scale-to-zero if model just went COLD
                if updated_record.state == LifecycleState.COLD:
                    logger.info(f"Deployment {deployment.deployment_id} transitioned to COLD. Unloading...")
                    await platform.chat_service.unload_deployment(deployment.deployment_id)
                    
        except asyncio.CancelledError:
            logger.info("Lifecycle worker cancelled.")
            break
        except Exception as e:
            logger.error(f"Error in lifecycle loop: {e}")
            
        await asyncio.sleep(10)
