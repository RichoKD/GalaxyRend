import aiohttp
import logging
from typing import Dict, Any, List, Optional
from app.config import get_settings
import json

logger = logging.getLogger(__name__)

class GraphQLClient:
    def __init__(self):
        self.settings = get_settings()
        self.endpoint = self.settings.graph_endpoint
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def query(self, query: str, variables: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute a GraphQL query"""
        if not self.session:
            raise RuntimeError("GraphQLClient must be used as async context manager")
        
        payload = {
            "query": query,
            "variables": variables or {}
        }
        
        try:
            async with self.session.post(
                self.endpoint,
                json=payload,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    if "errors" in result:
                        logger.error(f"GraphQL errors: {result['errors']}")
                        raise Exception(f"GraphQL query failed: {result['errors']}")
                    return result["data"]
                else:
                    logger.error(f"GraphQL request failed with status {response.status}")
                    raise Exception(f"GraphQL request failed: {response.status}")
                    
        except Exception as e:
            logger.error(f"GraphQL query failed: {e}")
            raise

class GalaxyRendGraphClient:
    """High-level client for GalaxyRend subgraph queries"""
    
    def __init__(self):
        self.client = GraphQLClient()
    
    async def get_workers(
        self, 
        skip: int = 0, 
        first: int = 100,
        verified_only: bool = False,
        min_reputation: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Get workers from The Graph"""
        
        where_conditions = []
        if verified_only:
            where_conditions.append("verified: true")
        if min_reputation is not None:
            where_conditions.append(f"reputation_gte: {min_reputation}")
        
        where_clause = f"where: {{{', '.join(where_conditions)}}}" if where_conditions else ""
        
        query = f"""
        query GetWorkers($skip: Int!, $first: Int!) {{
            workers(
                skip: $skip,
                first: $first,
                orderBy: reputation,
                orderDirection: desc,
                {where_clause}
            ) {{
                id
                address
                registered
                registeredAt
                verified
                verifiedAt
                verifiedBy
                reputation
                jobsCompleted
                jobsAssigned
                totalEarnings
                fullInfoCid
                lastSeen
                createdAt
                updatedAt
            }}
        }}
        """
        
        async with self.client as client:
            result = await client.query(query, {"skip": skip, "first": first})
            return result.get("workers", [])
    
    async def get_worker_by_address(self, address: str) -> Optional[Dict[str, Any]]:
        """Get a specific worker by address"""
        query = """
        query GetWorker($address: ID!) {
            worker(id: $address) {
                id
                address
                registered
                registeredAt
                verified
                verifiedAt
                verifiedBy
                reputation
                jobsCompleted
                jobsAssigned
                totalEarnings
                fullInfoCid
                lastSeen
                createdAt
                updatedAt
                reputationHistory(orderBy: timestamp, orderDirection: desc) {
                    id
                    oldReputation
                    newReputation
                    changeAmount
                    reason
                    timestamp
                    transactionHash
                }
            }
        }
        """
        
        async with self.client as client:
            result = await client.query(query, {"address": address.lower()})
            return result.get("worker")
    
    async def get_jobs(
        self,
        skip: int = 0,
        first: int = 100,
        status: Optional[str] = None,
        creator: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get jobs from The Graph"""
        
        where_conditions = []
        if status:
            where_conditions.append(f'status: {status.upper()}')
        if creator:
            where_conditions.append(f'creator: "{creator.lower()}"')
        
        where_clause = f"where: {{{', '.join(where_conditions)}}}" if where_conditions else ""
        
        query = f"""
        query GetJobs($skip: Int!, $first: Int!) {{
            jobs(
                skip: $skip,
                first: $first,
                orderBy: createdAt,
                orderDirection: desc,
                {where_clause}
            ) {{
                id
                chainJobId
                creator
                fullAssetCid
                reward
                deadline
                minReputation
                assignedWorker {{
                    id
                    address
                }}
                assignedAt
                completed
                completedAt
                fullResultCid
                qualityScore
                status
                createdAt
                updatedAt
            }}
        }}
        """
        
        async with self.client as client:
            result = await client.query(query, {"skip": skip, "first": first})
            return result.get("jobs", [])
    
    async def get_job_by_id(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific job by ID"""
        query = """
        query GetJob($jobId: ID!) {
            job(id: $jobId) {
                id
                chainJobId
                creator
                fullAssetCid
                reward
                deadline
                minReputation
                assignedWorker {
                    id
                    address
                    reputation
                }
                assignedAt
                completed
                completedAt
                fullResultCid
                qualityScore
                status
                createdAt
                updatedAt
                events(orderBy: timestamp, orderDirection: desc) {
                    id
                    eventType
                    actor
                    timestamp
                    transactionHash
                    data
                }
            }
        }
        """
        
        async with self.client as client:
            result = await client.query(query, {"jobId": job_id})
            return result.get("job")
    
    async def get_available_jobs(
        self,
        worker_address: Optional[str] = None,
        skip: int = 0,
        first: int = 50
    ) -> List[Dict[str, Any]]:
        """Get available jobs for a worker"""
        
        # If worker address provided, we need to check their reputation first
        min_reputation_filter = ""
        if worker_address:
            worker = await self.get_worker_by_address(worker_address)
            if worker and worker.get("verified"):
                worker_reputation = worker.get("reputation", 0)
                min_reputation_filter = f"minReputation_lte: {worker_reputation},"
        
        query = f"""
        query GetAvailableJobs($skip: Int!, $first: Int!) {{
            jobs(
                skip: $skip,
                first: $first,
                where: {{
                    status: OPEN,
                    assignedWorker: null,
                    {min_reputation_filter}
                    deadline_gt: "{int(__import__('time').time())}"
                }},
                orderBy: reward,
                orderDirection: desc
            ) {{
                id
                chainJobId
                creator
                fullAssetCid
                reward
                deadline
                minReputation
                status
                createdAt
            }}
        }}
        """
        
        async with self.client as client:
            result = await client.query(query, {"skip": skip, "first": first})
            return result.get("jobs", [])
    
    async def get_global_stats(self) -> Dict[str, Any]:
        """Get global platform statistics"""
        query = """
        query GetGlobalStats {
            globalStats(id: "global") {
                totalWorkers
                totalVerifiedWorkers
                totalJobs
                totalCompletedJobs
                totalRewards
                averageReputation
                averageQualityScore
                averageJobReward
                openJobs
                assignedJobs
                activeWorkers
                lastUpdated
            }
        }
        """
        
        async with self.client as client:
            result = await client.query(query)
            return result.get("globalStats", {})
    
    async def get_daily_stats(self, days: int = 7) -> List[Dict[str, Any]]:
        """Get daily statistics for the last N days"""
        # Calculate timestamp for N days ago
        import time
        cutoff_timestamp = int(time.time()) - (days * 24 * 60 * 60)
        
        query = """
        query GetDailyStats($since: BigInt!) {
            dailyStats(
                where: { date_gte: $since },
                orderBy: date,
                orderDirection: desc
            ) {
                id
                date
                jobsCreated
                jobsCompleted
                totalReward
                averageQuality
                activeWorkers
                newWorkers
                workersVerified
                totalTransactions
                averageReputation
            }
        }
        """
        
        async with self.client as client:
            result = await client.query(query, {"since": str(cutoff_timestamp)})
            return result.get("dailyStats", [])

# Global client instance
_graph_client = None

async def get_graph_client() -> GalaxyRendGraphClient:
    """Get or create GalaxyRend Graph client instance"""
    global _graph_client
    if _graph_client is None:
        _graph_client = GalaxyRendGraphClient()
    return _graph_client
