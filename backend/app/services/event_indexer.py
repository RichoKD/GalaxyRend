import asyncio
import logging
from datetime import datetime
from typing import Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from app.database import get_db_session
from app.models import ContractEvent, Worker, Job, ReputationHistory
from app.services.starknet_client import get_starknet_client
from app.config import get_settings
import json

logger = logging.getLogger(__name__)

class EventIndexer:
    def __init__(self):
        self.settings = get_settings()
        self.running = False
        self.last_processed_block = 0
        self.starknet_client = None
        
    async def start(self):
        """Start the event indexer"""
        self.running = True
        self.starknet_client = await get_starknet_client()
        
        # Get last processed block from database
        await self._load_last_processed_block()
        
        logger.info(f"Event indexer started from block {self.last_processed_block}")
        
        # Start indexing loop
        asyncio.create_task(self._indexing_loop())
    
    async def stop(self):
        """Stop the event indexer"""
        self.running = False
        logger.info("Event indexer stopped")
    
    @property
    def is_running(self) -> bool:
        return self.running
    
    async def _load_last_processed_block(self):
        """Load the last processed block number from database"""
        try:
            async for db in get_db_session():
                query = select(ContractEvent.block_number).order_by(
                    ContractEvent.block_number.desc()
                ).limit(1)
                result = await db.execute(query)
                last_block = result.scalar_one_or_none()
                
                if last_block:
                    self.last_processed_block = last_block
                else:
                    # Start from a reasonable block number or 0
                    self.last_processed_block = self.settings.start_block
                break
                
        except Exception as e:
            logger.error(f"Failed to load last processed block: {e}")
            self.last_processed_block = self.settings.start_block
    
    async def _indexing_loop(self):
        """Main indexing loop"""
        while self.running:
            try:
                await self._process_new_events()
                # Wait before next iteration
                await asyncio.sleep(self.settings.indexer_poll_interval)
                
            except Exception as e:
                logger.error(f"Error in indexing loop: {e}")
                await asyncio.sleep(10)  # Wait longer on error
    
    async def _process_new_events(self):
        """Process new events from the blockchain"""
        try:
            # Get latest block
            latest_block = await self.starknet_client.get_latest_block_number()
            if not latest_block or latest_block <= self.last_processed_block:
                return
            
            # Process blocks in chunks
            chunk_size = 100  # Process 100 blocks at a time
            from_block = self.last_processed_block + 1
            
            while from_block <= latest_block:
                to_block = min(from_block + chunk_size - 1, latest_block)
                
                # Get events for this chunk
                events = await self.starknet_client.get_events(
                    from_block=from_block,
                    to_block=to_block
                )
                
                if events:
                    await self._store_and_process_events(events)
                
                from_block = to_block + 1
                self.last_processed_block = to_block
                
                logger.info(f"Processed blocks {from_block-chunk_size} to {to_block}")
                
        except Exception as e:
            logger.error(f"Failed to process new events: {e}")
    
    async def _store_and_process_events(self, events: list):
        """Store events in database and process them"""
        async for db in get_db_session():
            try:
                for event_data in events:
                    # Check if event already exists
                    existing_query = select(ContractEvent).where(
                        and_(
                            ContractEvent.transaction_hash == event_data["transaction_hash"],
                            ContractEvent.event_index == event_data["event_index"]
                        )
                    )
                    existing = await db.execute(existing_query)
                    if existing.scalar_one_or_none():
                        continue  # Skip if already processed
                    
                    # Decode event
                    decoded = await self.starknet_client.decode_event(event_data)
                    if not decoded:
                        continue
                    
                    # Store event
                    contract_event = ContractEvent(
                        transaction_hash=event_data["transaction_hash"],
                        block_number=event_data["block_number"],
                        event_index=event_data["event_index"],
                        contract_address=event_data["contract_address"],
                        event_name=decoded["event_name"],
                        event_data=json.dumps(decoded["decoded_data"])
                    )
                    
                    db.add(contract_event)
                    await db.flush()  # Get the ID
                    
                    # Process the event
                    await self._process_event(contract_event, decoded, db)
                
                await db.commit()
                
            except Exception as e:
                await db.rollback()
                logger.error(f"Failed to store and process events: {e}")
            break
    
    async def _process_event(self, contract_event: ContractEvent, decoded: Dict[str, Any], db: AsyncSession):
        """Process a specific event type"""
        try:
            event_name = decoded["event_name"]
            event_data = decoded["decoded_data"]
            
            if event_name == "WorkerRegistered":
                await self._process_worker_registered(event_data, db)
            elif event_name == "WorkerVerified":
                await self._process_worker_verified(event_data, db)
            elif event_name == "JobCreated":
                await self._process_job_created(event_data, contract_event, db)
            elif event_name == "JobAssigned":
                await self._process_job_assigned(event_data, db)
            elif event_name == "JobCompleted":
                await self._process_job_completed(event_data, db)
            elif event_name == "JobFinalized":
                await self._process_job_finalized(event_data, db)
            elif event_name == "JobCancelled":
                await self._process_job_cancelled(event_data, db)
            elif event_name == "WorkApproved":
                await self._process_work_approved(event_data, db)
            elif event_name == "ReputationUpdated":
                await self._process_reputation_updated(event_data, contract_event, db)
            
            # Mark event as processed
            contract_event.processed = True
            contract_event.processed_at = datetime.utcnow()
            
        except Exception as e:
            logger.error(f"Failed to process event {contract_event.event_name}: {e}")
    
    async def _process_worker_registered(self, event_data: list, db: AsyncSession):
        """Process WorkerRegistered event"""
        try:
            worker_address = event_data[0]  # Assuming first element is worker address
            info_cid_part1 = event_data[1] if len(event_data) > 1 else None
            info_cid_part2 = event_data[2] if len(event_data) > 2 else None
            
            # Check if worker already exists
            query = select(Worker).where(Worker.address == worker_address)
            result = await db.execute(query)
            existing_worker = result.scalar_one_or_none()
            
            if not existing_worker:
                # Create new worker
                full_info_cid = info_cid_part1
                if info_cid_part2:
                    full_info_cid += info_cid_part2
                
                worker = Worker(
                    address=worker_address,
                    info_cid=full_info_cid
                )
                db.add(worker)
                logger.info(f"Worker registered: {worker_address}")
            
        except Exception as e:
            logger.error(f"Failed to process worker registration: {e}")
    
    async def _process_worker_verified(self, event_data: list, db: AsyncSession):
        """Process WorkerVerified event"""
        try:
            worker_address = event_data[0]
            verifier_address = event_data[1] if len(event_data) > 1 else None
            
            # Update worker verification status
            query = select(Worker).where(Worker.address == worker_address)
            result = await db.execute(query)
            worker = result.scalar_one_or_none()
            
            if worker:
                worker.verified = True
                worker.verified_by = verifier_address
                worker.verified_at = datetime.utcnow()
                logger.info(f"Worker verified: {worker_address}")
            
        except Exception as e:
            logger.error(f"Failed to process worker verification: {e}")
    
    async def _process_job_created(self, event_data: list, contract_event: ContractEvent, db: AsyncSession):
        """Process JobCreated event"""
        try:
            job_id = int(event_data[0])
            # creator_address = event_data[1]
            reward = int(event_data[2])
            deadline = int(event_data[3])  # Timestamp
            
            # Check if job already exists
            query = select(Job).where(Job.chain_job_id == job_id)
            result = await db.execute(query)
            existing_job = result.scalar_one_or_none()
            
            if not existing_job:
                # Get full job details from contract
                job_info = await self.starknet_client.get_job_info(job_id)
                if job_info:
                    full_asset_cid = job_info["asset_cid_part1"]
                    if job_info["asset_cid_part2"]:
                        full_asset_cid += job_info["asset_cid_part2"]
                    
                    job = Job(
                        chain_job_id=job_id,
                        creator_address=creator_address,
                        asset_cid_part1=job_info["asset_cid_part1"],
                        asset_cid_part2=job_info["asset_cid_part2"],
                        full_asset_cid=full_asset_cid,
                        reward_amount=reward,
                        deadline=datetime.fromtimestamp(deadline),
                        min_reputation=job_info["min_reputation"]
                    )
                    db.add(job)
                    logger.info(f"Job created: {job_id}")
            
        except Exception as e:
            logger.error(f"Failed to process job creation: {e}")
    
    async def _process_job_assigned(self, event_data: list, db: AsyncSession):
        """Process JobAssigned event"""
        try:
            job_id = int(event_data[0])
            worker_address = event_data[1]
            
            # Get job and worker
            job_query = select(Job).where(Job.chain_job_id == job_id)
            job_result = await db.execute(job_query)
            job = job_result.scalar_one_or_none()
            
            worker_query = select(Worker).where(Worker.address == worker_address)
            worker_result = await db.execute(worker_query)
            worker = worker_result.scalar_one_or_none()
            
            if job and worker:
                job.worker_id = worker.id
                job.status = "assigned"
                job.assigned_at = datetime.utcnow()
                logger.info(f"Job {job_id} assigned to {worker_address}")
            
        except Exception as e:
            logger.error(f"Failed to process job assignment: {e}")
    
    async def _process_job_completed(self, event_data: list, db: AsyncSession):
        """Process JobCompleted event (Legacy/Optional)"""
        try:
            job_id = int(event_data[0])
            # ... kept for backward compatibility if needed
            logger.info(f"Processing JobCompleted for {job_id}")
        except Exception as e:
            logger.error(f"Failed to process job completion: {e}")

    async def _process_job_finalized(self, event_data: list, db: AsyncSession):
        """Process JobFinalized event"""
        try:
            job_id = int(event_data[0])
            worker_address = event_data[1]
            reward_amount = int(event_data[2])
            
            # Update job
            query = select(Job).where(Job.chain_job_id == job_id)
            result = await db.execute(query)
            job = result.scalar_one_or_none()
            
            if job:
                job.status = "completed"
                job.completed_at = datetime.utcnow()
                
                # Update worker stats
                query_worker = select(Worker).where(Worker.address == worker_address)
                result_worker = await db.execute(query_worker)
                worker = result_worker.scalar_one_or_none()
                
                if worker:
                    worker.jobs_completed += 1
                    worker.total_earnings += reward_amount
                
                logger.info(f"Job {job_id} finalized")
                
        except Exception as e:
            logger.error(f"Failed to process job finalization: {e}")

    async def _process_job_cancelled(self, event_data: list, db: AsyncSession):
        """Process JobCancelled event"""
        try:
            job_id = int(event_data[0])
            # refund_amount = int(event_data[2])
            
            query = select(Job).where(Job.chain_job_id == job_id)
            result = await db.execute(query)
            job = result.scalar_one_or_none()
            
            if job:
                job.status = "cancelled"
                job.completed_at = datetime.utcnow() # Using completed_at for cancellation time
                logger.info(f"Job {job_id} cancelled")
                
        except Exception as e:
            logger.error(f"Failed to process job cancellation: {e}")

    async def _process_work_approved(self, event_data: list, db: AsyncSession):
        """Process WorkApproved event"""
        try:
            job_id = int(event_data[0])
            worker_address = event_data[1]
            approver_address = event_data[2]
            
            query = select(Job).where(Job.chain_job_id == job_id)
            result = await db.execute(query)
            job = result.scalar_one_or_none()
            
            if job:
                job.status = "completed" # Approved work is completed
                job.quality_score = 100 # Default to max score since it was manually approved? Or leave None.
                logger.info(f"Job {job_id} work approved by {approver_address}")
                
        except Exception as e:
            logger.error(f"Failed to process work approval: {e}")
    
    async def _process_reputation_updated(self, event_data: list, contract_event: ContractEvent, db: AsyncSession):
        """Process ReputationUpdated event"""
        try:
            worker_address = event_data[0]
            old_reputation = int(event_data[1])
            new_reputation = int(event_data[2])
            reason = event_data[3] if len(event_data) > 3 else "unknown"
            
            # Update worker reputation
            query = select(Worker).where(Worker.address == worker_address)
            result = await db.execute(query)
            worker = result.scalar_one_or_none()
            
            if worker:
                worker.reputation = new_reputation
                
                # Create reputation history entry
                history = ReputationHistory(
                    worker_id=worker.id,
                    old_reputation=old_reputation,
                    new_reputation=new_reputation,
                    change_amount=new_reputation - old_reputation,
                    reason=reason,
                    transaction_hash=contract_event.transaction_hash
                )
                db.add(history)
                
                logger.info(f"Worker {worker_address} reputation updated: {old_reputation} -> {new_reputation}")
            
        except Exception as e:
            logger.error(f"Failed to process reputation update: {e}")
