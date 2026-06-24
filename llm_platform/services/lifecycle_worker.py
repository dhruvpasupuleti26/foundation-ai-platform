"""Background worker for model lifecycle management."""

import asyncio
from fastapi import FastAPI

from llm_platform.schemas.enums import LifecycleState, DeploymentStatus


async def run_lifecycle_loop(app: FastAPI):
    """Background task to enforce scale-to-zero lifecycle policies."""
    print("[Lifecycle Worker] Starting lifecycle management background worker.")
    
    # Wait a bit for the application to fully initialize
    await asyncio.sleep(5)
    
    try:
        platform = app.state.platform_application
    except AttributeError:
        print("[Lifecycle Worker] ERROR: Platform application not found on app state. Worker exiting.")
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
                
                # Scale-to-zero trigger
                if updated_record.state == LifecycleState.COLD:
                    print(f"[Lifecycle Worker] Deployment {deployment.deployment_id} transitioned to COLD. Unloading...")
                    await platform.chat_service.unload_deployment(deployment.deployment_id)
                    # Release GPU VRAM allocation
                    if hasattr(platform, 'gpu_tracker') and platform.gpu_tracker:
                        platform.gpu_tracker.release(deployment.deployment_id)
        except asyncio.CancelledError:
            print("[Lifecycle Worker] Lifecycle worker cancelled.")
            break
        except Exception as e:
            print(f"[Lifecycle Worker] Error in lifecycle loop: {e}")
            
        await asyncio.sleep(10)
