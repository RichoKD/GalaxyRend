# The Graph Integration Guide for GalaxyRend

This guide explains how to integrate The Graph Protocol into your GalaxyRend workflow for efficient blockchain data indexing and querying.

## Overview

GalaxyRend supports three approaches for blockchain data access:

1. **Direct Event Indexing** - FastAPI backend directly indexes contract events
2. **The Graph Only** - Use The Graph Protocol for all data queries
3. **Hybrid Approach** - Use The Graph with database fallback

## Setup Options

### Option 1: Pure Graph Integration

Replace the FastAPI event indexer entirely with The Graph:

```bash
# 1. Set up the subgraph
cd subgraph
./setup.sh
npm run codegen
npm run build

# 2. Deploy to local Graph node
npm run create-local
npm run deploy-local

# 3. Configure backend to use Graph
echo "USE_GRAPH=true" >> backend/.env
echo "GRAPH_ENDPOINT=http://localhost:8000/subgraphs/name/galaxyrend/galaxyrend-subgraph" >> backend/.env
echo "ENABLE_EVENT_INDEXING=false" >> backend/.env
```

### Option 2: Hybrid Approach (Recommended)

Use The Graph for complex queries with database fallback:

```bash
# 1. Deploy subgraph (same as above)
cd subgraph && ./setup.sh && npm run codegen && npm run build && npm run deploy-local

# 2. Configure hybrid mode
echo "USE_GRAPH=true" >> backend/.env
echo "ENABLE_EVENT_INDEXING=true" >> backend/.env  # Keep as fallback
```

## Deployment Workflows

### Local Development

```bash
# 1. Start Graph Node (Docker)
cd infra
docker-compose -f graph-node-compose.yml up -d

# 2. Deploy subgraph
cd ../subgraph
npm run deploy-local

# 3. Start backend
cd ../backend
source venv/bin/activate
uvicorn app.main:app --reload
```

### Production (Hosted Service)

```bash
# 1. Create subgraph on The Graph
graph auth --product hosted-service YOUR_ACCESS_TOKEN

# 2. Deploy to hosted service
cd subgraph
npm run deploy

# 3. Update backend config
echo "GRAPH_ENDPOINT=https://api.thegraph.com/subgraphs/name/YOUR_USERNAME/galaxyrend-subgraph" >> backend/.env
```

## API Usage Patterns

### Using Hybrid Endpoints

The hybrid API automatically chooses between Graph and database:

```python
# Workers API
GET /api/v1/hybrid/workers?verified_only=true&min_reputation=600

# Jobs API  
GET /api/v1/hybrid/jobs?status=open&creator_address=0x123...

# Available jobs for worker
GET /api/v1/hybrid/available-jobs?worker_address=0x456...

# Global statistics
GET /api/v1/hybrid/stats/global

# Daily trends
GET /api/v1/hybrid/stats/daily?days=30
```

### Direct Graph Queries

For custom queries, use the Graph client directly:

```python
from app.services.graph_client import get_graph_client

async def custom_query():
    client = await get_graph_client()
    
    # Custom GraphQL query
    result = await client.client.query("""
        query CustomWorkerStats {
            workers(where: {verified: true, reputation_gte: 800}) {
                id
                reputation
                jobsCompleted
                totalEarnings
            }
        }
    """)
    
    return result
```

## Benefits of Each Approach

### Direct Indexing
- ✅ Full control over data processing
- ✅ Real-time updates  
- ✅ Custom business logic
- ❌ Higher infrastructure costs
- ❌ More complex deployment

### The Graph Only
- ✅ Decentralized infrastructure
- ✅ Optimized for complex queries
- ✅ Built-in caching and CDN
- ✅ Lower operational overhead
- ❌ GraphQL learning curve
- ❌ Potential query limitations

### Hybrid Approach
- ✅ Best of both worlds
- ✅ Fallback reliability
- ✅ Gradual migration path
- ✅ Performance optimization
- ❌ Increased complexity
- ❌ Dual maintenance

## Configuration

### Environment Variables

```env
# The Graph settings
USE_GRAPH=true
GRAPH_ENDPOINT=http://localhost:8000/subgraphs/name/galaxyrend/galaxyrend-subgraph
ENABLE_EVENT_INDEXING=true  # Keep as fallback

# Contract settings (for both approaches)
STARKNET_RPC_URL=http://localhost:5050
CONTRACT_ADDRESS=0x...
START_BLOCK=12345
```

### Feature Flags

Control which data sources to use:

```python
# In your API routes
if settings.use_graph:
    # Use Graph for complex queries
    return await graph_client.get_worker_analytics()
else:
    # Use database for simple queries  
    return await db_query.get_workers()
```

## Data Consistency

### Ensuring Sync

The hybrid approach maintains consistency by:

1. **Primary Source**: The Graph for complex queries
2. **Fallback**: Database for reliability
3. **Validation**: Cross-check critical data
4. **Monitoring**: Alert on discrepancies

### Monitoring

```python
# Add to your health check
@app.get("/health/data-sync")
async def check_data_sync():
    try:
        # Check Graph availability
        graph_workers = await graph_client.get_workers(first=1)
        
        # Check database
        db_workers = await db.query("SELECT COUNT(*) FROM workers").scalar()
        
        return {
            "graph_status": "healthy" if graph_workers else "degraded",
            "database_status": "healthy",
            "sync_status": "synced" if abs(len(graph_workers) - db_workers) < 10 else "drift_detected"
        }
    except Exception as e:
        return {"status": "error", "details": str(e)}
```

## Migration Strategy

### Gradual Migration to The Graph

1. **Phase 1**: Deploy subgraph alongside existing indexer
2. **Phase 2**: Use hybrid endpoints for new features
3. **Phase 3**: Migrate read queries to Graph
4. **Phase 4**: Keep indexer for writes only
5. **Phase 5**: Full Graph migration

### Rollback Plan

If issues arise with The Graph:

```bash
# 1. Disable Graph usage
echo "USE_GRAPH=false" >> backend/.env

# 2. Restart backend
systemctl restart galaxyrend-backend

# 3. Database continues serving requests
# No data loss - seamless fallback
```

## Performance Considerations

### Query Optimization

The Graph excels at:
- Complex filtering and aggregations
- Historical data analysis  
- Multi-entity relationships
- Time-series queries

Database better for:
- Simple CRUD operations
- Real-time writes
- Custom business logic
- Transactional consistency

### Caching Strategy

```python
# Use Redis for frequently accessed Graph data
@cache(expire=300)  # 5 minute cache
async def get_trending_jobs():
    return await graph_client.get_jobs(
        orderBy="reward", 
        orderDirection="desc", 
        first=10
    )
```

## Next Steps

1. **Choose your approach** based on requirements
2. **Deploy the subgraph** using provided scripts
3. **Update your frontend** to use hybrid endpoints  
4. **Monitor performance** and adjust as needed
5. **Gradually migrate** more queries to The Graph

The Graph integration provides a powerful, scalable solution for blockchain data access while maintaining the flexibility and control of your existing FastAPI backend.
