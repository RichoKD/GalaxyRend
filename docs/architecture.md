```
GalaxyRend/
│
├── contracts/                     # All Cairo smart contracts
│   ├── job_registry/               # Job registry contract (Cairo v2)
│   │   ├── src/
│   │   │   ├── job_registry.cairo
│   │   │   └── lib.cairo
│   │   ├── tests/                  # Protostar/Foundry tests
│   │   ├── Scarb.toml               # Cairo project config
│   │   └── README.md
│   ├── token/                      # ERC-20 or payment token
│   └── utils/                      # Shared Cairo libs (Uint256, etc.)
│
├── worker/                         # Off-chain worker node
│   ├── src/
│   │   ├── main.py                  # Worker entrypoint
│   │   ├── renderer.py              # Rendering logic (e.g., Blender)
│   │   ├── ipfs_client.py           # Upload/download from IPFS
│   │   ├── starknet_client.py       # Interact with contracts
│   │   └── verifier.py              # Optional verification logic
│   ├── Dockerfile
│   ├── requirements.txt
│   └── README.md
│
├── frontend/                       # Web UI for job submission/tracking
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── hooks/
│   │   └── utils/
│   ├── package.json
│   └── README.md
│
├── services/                       # Auxiliary services/microservices
│   ├── aggregator/                  # Verifies results, finalizes jobs
│   ├── scheduler/                    # Assigns jobs to workers
│   └── notifier/                     # Sends events/notifications
│
├── shared/                         # Shared code across packages
│   ├── proto/                        # Protobufs or API schemas
│   ├── types/                        # TypeScript/Python types
│   ├── utils/                        # Shared helper libs
│   └── config/                       # Centralized configs
│
├── infra/                          # Infrastructure configs
│   ├── docker-compose.yml            # Local dev network
│   ├── k8s/                          # Kubernetes manifests
│   ├── terraform/                    # Cloud infra
│   └── README.md
│
├── scripts/                        # Dev & deployment scripts
│   ├── deploy_contracts.sh
│   ├── start_worker.sh
│   └── seed_demo_data.py
│
├── docs/                           # Project documentation
│   ├── architecture.md
│   ├── contracts.md
│   ├── worker.md
│   └── roadmap.md
│
├── tests/                          # Cross-package integration tests
│   ├── test_end_to_end.py
│   └── test_worker_integration.py
│
├── .env.example
├── README.md
└── package.json / pyproject.toml    # Root-level dependencies for tooling
```