// GalaxyRend Job Registry with OpenZeppelin Integration
use starknet::ContractAddress;

// Interface representing the Job Registry contract.
#[starknet::interface]
pub trait IJobRegistry<TContractState> {
    // Creates a new job and escrows the reward. Returns the new job ID.
    fn create_job(
        ref self: TContractState,
        asset_cid_part1: felt252,
        asset_cid_part2: felt252,
        reward_amount: u256,
        deadline_timestamp: u64,
    ) -> felt252;
    fn create_job_with_requirements(
        ref self: TContractState,
        asset_cid_part1: felt252,
        asset_cid_part2: felt252,
        reward_amount: u256,
        deadline_timestamp: u64,
        min_reputation: u16,
    ) -> felt252;
    // Allows a worker to submit a result.
    fn submit_result(
        ref self: TContractState,
        job_id: felt252,
        result_cid_part1: felt252,
        result_cid_part2: felt252,
    );
    // Finalizes a job and pays the reward to the worker.
    fn finalize_job(ref self: TContractState, job_id: felt252);
    // Emergency pause functionality
    fn pause(ref self: TContractState);
    fn unpause(ref self: TContractState);

    // New functions for better flow
    fn cancel_job(ref self: TContractState, job_id: felt252);
    fn approve_work(ref self: TContractState, job_id: felt252);


    // Worker Authorization and Reputation System
    fn register_worker(ref self: TContractState, worker_info_cid: felt252);
    fn verify_worker(ref self: TContractState, worker: ContractAddress, verification_status: bool);
    fn update_worker_reputation(
        ref self: TContractState, worker: ContractAddress, job_id: felt252, quality_score: u8,
    );
    fn slash_worker_reputation(
        ref self: TContractState, worker: ContractAddress, slash_amount: u16,
    );
    fn get_worker_status(
        self: @TContractState, worker: ContractAddress,
    ) -> (bool, u16, u32, u32); // (verified, reputation, jobs_completed, jobs_failed)
    fn get_minimum_reputation_for_job(self: @TContractState, job_id: felt252) -> u16;
    fn is_worker_eligible(self: @TContractState, worker: ContractAddress, job_id: felt252) -> bool;

    // Getter functions
    fn get_job_counter(self: @TContractState) -> felt252;
    fn get_job_creator(self: @TContractState, job_id: felt252) -> ContractAddress;
    fn get_job_worker(self: @TContractState, job_id: felt252) -> ContractAddress;
    fn get_job_reward(self: @TContractState, job_id: felt252) -> u256;
    fn get_job_asset_cid(self: @TContractState, job_id: felt252) -> (felt252, felt252);
    fn get_job_deadline(self: @TContractState, job_id: felt252) -> u64;
    fn is_job_completed(self: @TContractState, job_id: felt252) -> bool;
    fn get_job_submission_time(self: @TContractState, job_id: felt252) -> u64;
}

#[starknet::contract]
mod JobRegistry {
    use core::num::traits::Zero;
    use openzeppelin_access::ownable::OwnableComponent;
    use openzeppelin_security::pausable::PausableComponent;
    use openzeppelin_security::reentrancyguard::ReentrancyGuardComponent;
    use openzeppelin_token::erc20::interface::{IERC20Dispatcher, IERC20DispatcherTrait};
    use starknet::storage::{
        Map, StorageMapReadAccess, StorageMapWriteAccess, StoragePointerReadAccess,
        StoragePointerWriteAccess,
    };
    use starknet::{ContractAddress, get_block_timestamp, get_caller_address, get_contract_address};
    use super::IJobRegistry;

    // Components
    component!(path: OwnableComponent, storage: ownable, event: OwnableEvent);
    component!(
        path: ReentrancyGuardComponent, storage: reentrancy_guard, event: ReentrancyGuardEvent,
    );
    component!(path: PausableComponent, storage: pausable, event: PausableEvent);

    // Component implementations
    #[abi(embed_v0)]
    impl OwnableImpl = OwnableComponent::OwnableImpl<ContractState>;
    impl OwnableInternalImpl = OwnableComponent::InternalImpl<ContractState>;

    impl ReentrancyGuardInternalImpl = ReentrancyGuardComponent::InternalImpl<ContractState>;

    #[abi(embed_v0)]
    impl PausableImpl = PausableComponent::PausableImpl<ContractState>;
    impl PausableInternalImpl = PausableComponent::InternalImpl<ContractState>;

    #[storage]
    struct Storage {
        // OpenZeppelin components
        #[substorage(v0)]
        ownable: OwnableComponent::Storage,
        #[substorage(v0)]
        reentrancy_guard: ReentrancyGuardComponent::Storage,
        #[substorage(v0)]
        pausable: PausableComponent::Storage,
        // Job registry specific storage
        reward_token_address: ContractAddress,
        job_counter: felt252,
        job_asset_cid_part1: Map<felt252, felt252>,
        job_asset_cid_part2: Map<felt252, felt252>,
        job_reward: Map<felt252, u256>,
        job_creator: Map<felt252, ContractAddress>,
        job_deadline: Map<felt252, u64>,
        job_worker: Map<felt252, ContractAddress>,
        job_result_cid_part1: Map<felt252, felt252>,
        job_result_cid_part2: Map<felt252, felt252>,
        job_completed: Map<felt252, bool>,
        // Worker Authorization and Reputation System
        worker_verified: Map<ContractAddress, bool>, // Whether worker is verified
        worker_reputation: Map<ContractAddress, u16>, // Reputation score (0-1000)
        worker_jobs_completed: Map<ContractAddress, u32>, // Number of successfully completed jobs
        worker_jobs_failed: Map<ContractAddress, u32>, // Number of failed jobs
        worker_info_cid: Map<ContractAddress, felt252>, // IPFS CID for worker information
        worker_registration_time: Map<ContractAddress, u64>, // When worker registered
        job_minimum_reputation: Map<felt252, u16>, // Minimum reputation required for job
        job_quality_scores: Map<felt252, u8>, // Quality score for completed jobs (0-100)
        job_submission_time: Map<felt252, u64> // Time when result was submitted
    }

    #[event]
    #[derive(Drop, starknet::Event)]
    enum Event {
        #[flat]
        OwnableEvent: OwnableComponent::Event,
        #[flat]
        ReentrancyGuardEvent: ReentrancyGuardComponent::Event,
        #[flat]
        PausableEvent: PausableComponent::Event,
        JobCreated: JobCreated,
        ResultSubmitted: ResultSubmitted,
        JobFinalized: JobFinalized,
        JobCancelled: JobCancelled,
        WorkApproved: WorkApproved,
        // Worker Authorization Events
        WorkerRegistered: WorkerRegistered,
        WorkerVerified: WorkerVerified,
        ReputationUpdated: ReputationUpdated,
        ReputationSlashed: ReputationSlashed,
    }

    #[derive(Drop, starknet::Event)]
    struct JobCreated {
        #[key]
        job_id: felt252,
        #[key]
        creator: ContractAddress,
        reward_amount: u256,
        deadline: u64,
    }

    #[derive(Drop, starknet::Event)]
    struct ResultSubmitted {
        #[key]
        job_id: felt252,
        #[key]
        worker: ContractAddress,
    }

    #[derive(Drop, starknet::Event)]
    struct JobFinalized {
        #[key]
        job_id: felt252,
        #[key]
        worker: ContractAddress,
        reward_amount: u256,
    }

    #[derive(Drop, starknet::Event)]
    struct JobCancelled {
        #[key]
        job_id: felt252,
        creator: ContractAddress,
        refund_amount: u256,
    }

    #[derive(Drop, starknet::Event)]
    struct WorkApproved {
        #[key]
        job_id: felt252,
        worker: ContractAddress,
        approver: ContractAddress,
    }


    // Worker Authorization Events
    #[derive(Drop, starknet::Event)]
    struct WorkerRegistered {
        #[key]
        worker: ContractAddress,
        info_cid: felt252,
        registration_time: u64,
    }

    #[derive(Drop, starknet::Event)]
    struct WorkerVerified {
        #[key]
        worker: ContractAddress,
        verified: bool,
        verifier: ContractAddress,
    }

    #[derive(Drop, starknet::Event)]
    struct ReputationUpdated {
        #[key]
        worker: ContractAddress,
        job_id: felt252,
        old_reputation: u16,
        new_reputation: u16,
        quality_score: u8,
    }

    #[derive(Drop, starknet::Event)]
    struct ReputationSlashed {
        #[key]
        worker: ContractAddress,
        old_reputation: u16,
        new_reputation: u16,
        slash_amount: u16,
        reason: felt252,
    }

    #[constructor]
    fn constructor(
        ref self: ContractState, owner: ContractAddress, reward_token_address: ContractAddress,
    ) {
        // Initialize OpenZeppelin components
        self.ownable.initializer(owner);

        // Initialize contract-specific state
        self.reward_token_address.write(reward_token_address);
    }

    #[abi(embed_v0)]
    impl JobRegistryImpl of IJobRegistry<ContractState> {
        fn create_job(
            ref self: ContractState,
            asset_cid_part1: felt252,
            asset_cid_part2: felt252,
            reward_amount: u256,
            deadline_timestamp: u64,
        ) -> felt252 {
            // Default minimum reputation requirement
            self
                .create_job_with_requirements(
                    asset_cid_part1, asset_cid_part2, reward_amount, deadline_timestamp, 400_u16,
                )
        }

        fn create_job_with_requirements(
            ref self: ContractState,
            asset_cid_part1: felt252,
            asset_cid_part2: felt252,
            reward_amount: u256,
            deadline_timestamp: u64,
            min_reputation: u16,
        ) -> felt252 {
            // Security checks
            self.pausable.assert_not_paused();
            self.reentrancy_guard.start();

            let caller = get_caller_address();
            assert(!caller.is_zero(), 'Caller cannot be zero');
            assert(reward_amount > 0, 'Reward must be positive');
            assert(deadline_timestamp > get_block_timestamp(), 'Deadline must be in future');
            assert(min_reputation <= 1000, 'Max reputation is 1000');

            // Get the current job ID and increment it
            let job_id = self.job_counter.read() + 1;
            self.job_counter.write(job_id);

            // Transfer tokens from creator to this contract (escrow)
            let token = IERC20Dispatcher { contract_address: self.reward_token_address.read() };
            token.transfer_from(caller, get_contract_address(), reward_amount);

            // Store job details
            self.job_creator.write(job_id, caller);
            self.job_asset_cid_part1.write(job_id, asset_cid_part1);
            self.job_asset_cid_part2.write(job_id, asset_cid_part2);
            self.job_reward.write(job_id, reward_amount);
            self.job_deadline.write(job_id, deadline_timestamp);
            self.job_minimum_reputation.write(job_id, min_reputation);

            // Emit event
            self
                .emit(
                    JobCreated {
                        job_id, creator: caller, reward_amount, deadline: deadline_timestamp,
                    },
                );

            self.reentrancy_guard.end();
            job_id
        }

        fn submit_result(
            ref self: ContractState,
            job_id: felt252,
            result_cid_part1: felt252,
            result_cid_part2: felt252,
        ) {
            // Security checks
            self.pausable.assert_not_paused();

            let caller = get_caller_address();
            let creator = self.job_creator.read(job_id);

            assert(!creator.is_zero(), 'Job does not exist');
            assert(caller != creator, 'Creator cannot be worker');
            assert(self.job_worker.read(job_id).is_zero(), 'Job already has worker');
            assert(!self.job_completed.read(job_id), 'Job already completed');

            // Check worker authorization and eligibility
            assert(self.is_worker_eligible(caller, job_id), 'Worker not eligible for job');

            // Assign worker and store result
            self.job_worker.write(job_id, caller);
            self.job_result_cid_part1.write(job_id, result_cid_part1);
            self.job_result_cid_part2.write(job_id, result_cid_part2);
            self.job_submission_time.write(job_id, get_block_timestamp());

            // Emit event
            self.emit(ResultSubmitted { job_id, worker: caller });
        }

        fn finalize_job(ref self: ContractState, job_id: felt252) {
            // Security checks
            self.pausable.assert_not_paused();
            self.reentrancy_guard.start();

            let current_time = get_block_timestamp();
            let submission_time = self.job_submission_time.read(job_id);
            let worker = self.job_worker.read(job_id);

            assert(!worker.is_zero(), 'No worker assigned');
            assert(!self.job_completed.read(job_id), 'Job already completed');

            // Dispute period check (3 days = 259200 seconds)
            // If the creator hasn't approved or disputed, worker can claim after this period
            let dispute_period = 259200;
            assert(current_time >= submission_time + dispute_period, 'Dispute period active');

            let reward = self.job_reward.read(job_id);

            // Mark job as completed BEFORE transfer (CEI pattern)
            self.job_completed.write(job_id, true);

            // Transfer reward to worker
            let token = IERC20Dispatcher { contract_address: self.reward_token_address.read() };
            token.transfer(worker, reward);

            // Emit event
            self.emit(JobFinalized { job_id, worker, reward_amount: reward });

            self.reentrancy_guard.end();
        }

        fn cancel_job(ref self: ContractState, job_id: felt252) {
            self.pausable.assert_not_paused();
            self.reentrancy_guard.start();

            let caller = get_caller_address();
            let creator = self.job_creator.read(job_id);
            assert(caller == creator, 'Only creator can cancel');
            assert(!self.job_completed.read(job_id), 'Job already completed');

            // Can only cancel if no worker has submitted a result
            let worker = self.job_worker.read(job_id);
            assert(worker.is_zero(), 'Worker already assigned');

            let reward = self.job_reward.read(job_id);

            // Mark completed/cancelled BEFORE transfer
            self.job_completed.write(job_id, true);

            // Refund creator
            let token = IERC20Dispatcher { contract_address: self.reward_token_address.read() };
            token.transfer(creator, reward);

            self.emit(JobCancelled { job_id, creator, refund_amount: reward });

            self.reentrancy_guard.end();
        }

        fn approve_work(ref self: ContractState, job_id: felt252) {
            self.pausable.assert_not_paused();
            self.reentrancy_guard.start();

            let caller = get_caller_address();
            let creator = self.job_creator.read(job_id);
            assert(caller == creator, 'Only creator can approve');
            assert(!self.job_completed.read(job_id), 'Job already completed');

            let worker = self.job_worker.read(job_id);
            assert(!worker.is_zero(), 'No worker to approve');

            let reward = self.job_reward.read(job_id);

            // Mark completed BEFORE transfer
            self.job_completed.write(job_id, true);

            // Pay worker
            let token = IERC20Dispatcher { contract_address: self.reward_token_address.read() };
            token.transfer(worker, reward);

            self.emit(WorkApproved { job_id, worker, approver: caller });
            self.emit(JobFinalized { job_id, worker, reward_amount: reward });

            self.reentrancy_guard.end();
        }

        fn pause(ref self: ContractState) {
            self.ownable.assert_only_owner();
            self.pausable.pause();
        }

        fn unpause(ref self: ContractState) {
            self.ownable.assert_only_owner();
            self.pausable.unpause();
        }

        // Getter functions
        fn get_job_counter(self: @ContractState) -> felt252 {
            self.job_counter.read()
        }

        fn get_job_creator(self: @ContractState, job_id: felt252) -> ContractAddress {
            self.job_creator.read(job_id)
        }

        fn get_job_worker(self: @ContractState, job_id: felt252) -> ContractAddress {
            self.job_worker.read(job_id)
        }

        fn get_job_reward(self: @ContractState, job_id: felt252) -> u256 {
            self.job_reward.read(job_id)
        }

        fn get_job_asset_cid(self: @ContractState, job_id: felt252) -> (felt252, felt252) {
            (self.job_asset_cid_part1.read(job_id), self.job_asset_cid_part2.read(job_id))
        }

        fn get_job_deadline(self: @ContractState, job_id: felt252) -> u64 {
            self.job_deadline.read(job_id)
        }

        fn is_job_completed(self: @ContractState, job_id: felt252) -> bool {
            self.job_completed.read(job_id)
        }

        fn get_job_submission_time(self: @ContractState, job_id: felt252) -> u64 {
            self.job_submission_time.read(job_id)
        }


        // Worker Authorization and Reputation System Implementation
        fn register_worker(ref self: ContractState, worker_info_cid: felt252) {
            self.pausable.assert_not_paused();
            let caller = get_caller_address();

            assert(!caller.is_zero(), 'Caller cannot be zero');
            assert(worker_info_cid != 0, 'Worker info CID required');

            // Check if worker is already registered
            let current_time = self.worker_registration_time.read(caller);
            assert(current_time == 0, 'Worker already registered');

            // Register worker with initial reputation
            self.worker_verified.write(caller, false);
            self.worker_reputation.write(caller, 500); // Start with middle reputation (500/1000)
            self.worker_jobs_completed.write(caller, 0);
            self.worker_jobs_failed.write(caller, 0);
            self.worker_info_cid.write(caller, worker_info_cid);
            self.worker_registration_time.write(caller, get_block_timestamp());

            // Emit event
            self
                .emit(
                    WorkerRegistered {
                        worker: caller,
                        info_cid: worker_info_cid,
                        registration_time: get_block_timestamp(),
                    },
                );
        }

        fn verify_worker(
            ref self: ContractState, worker: ContractAddress, verification_status: bool,
        ) {
            // Only owner can verify workers
            self.ownable.assert_only_owner();
            self.pausable.assert_not_paused();

            assert(!worker.is_zero(), 'Worker cannot be zero');

            // Check if worker is registered
            let registration_time = self.worker_registration_time.read(worker);
            assert(registration_time != 0, 'Worker not registered');

            // Update verification status
            self.worker_verified.write(worker, verification_status);

            // If verified, boost reputation; if unverified, reduce it
            let current_reputation = self.worker_reputation.read(worker);
            let new_reputation = if verification_status {
                // Boost reputation for verification (min 600)
                if current_reputation < 600 {
                    600
                } else {
                    current_reputation
                }
            } else {
                // Reduce reputation for losing verification
                if current_reputation > 400 {
                    current_reputation - 200
                } else {
                    200
                }
            };
            self.worker_reputation.write(worker, new_reputation);

            // Emit event
            self
                .emit(
                    WorkerVerified {
                        worker, verified: verification_status, verifier: get_caller_address(),
                    },
                );
        }

        fn update_worker_reputation(
            ref self: ContractState, worker: ContractAddress, job_id: felt252, quality_score: u8,
        ) {
            // Only job creator can update reputation after job completion
            let caller = get_caller_address();
            let job_creator = self.job_creator.read(job_id);
            let job_worker = self.job_worker.read(job_id);

            assert(caller == job_creator, 'Only job creator can rate');
            assert(worker == job_worker, 'Worker must match job worker');
            assert(self.job_completed.read(job_id), 'Job not completed');
            assert(quality_score <= 100, 'Quality score max is 100');

            // Check if this job has already been rated
            assert(self.job_quality_scores.read(job_id) == 0, 'Job already rated');

            // Store quality score
            self.job_quality_scores.write(job_id, quality_score);

            // Calculate reputation change based on quality score
            let current_reputation = self.worker_reputation.read(worker);
            let reputation_change = if quality_score >= 90 {
                20_u16 // Excellent work
            } else if quality_score >= 75 {
                10_u16 // Good work
            } else if quality_score >= 60 {
                5_u16 // Acceptable work
            } else if quality_score >= 40 {
                0_u16 // No change for poor work
            } else {
                // Very poor work - decrease reputation
                let decrease = 15_u16;
                if current_reputation > decrease {
                    self.worker_reputation.write(worker, current_reputation - decrease);
                    self.worker_jobs_failed.write(worker, self.worker_jobs_failed.read(worker) + 1);
                } else {
                    self.worker_reputation.write(worker, 1); // Minimum reputation
                    self.worker_jobs_failed.write(worker, self.worker_jobs_failed.read(worker) + 1);
                }
                0_u16
            };

            // Apply positive reputation change
            if reputation_change > 0 {
                let new_reputation = if current_reputation + reputation_change > 1000 {
                    1000_u16 // Cap at maximum
                } else {
                    current_reputation + reputation_change
                };
                self.worker_reputation.write(worker, new_reputation);
                self
                    .worker_jobs_completed
                    .write(worker, self.worker_jobs_completed.read(worker) + 1);

                // Emit event
                self
                    .emit(
                        ReputationUpdated {
                            worker,
                            job_id,
                            old_reputation: current_reputation,
                            new_reputation,
                            quality_score,
                        },
                    );
            } else if quality_score < 40 {
                // Emit event for reputation decrease
                self
                    .emit(
                        ReputationUpdated {
                            worker,
                            job_id,
                            old_reputation: current_reputation,
                            new_reputation: self.worker_reputation.read(worker),
                            quality_score,
                        },
                    );
            }
        }

        fn slash_worker_reputation(
            ref self: ContractState, worker: ContractAddress, slash_amount: u16,
        ) {
            // Only owner can slash reputation (for misconduct, etc.)
            self.ownable.assert_only_owner();
            self.pausable.assert_not_paused();

            assert(!worker.is_zero(), 'Worker cannot be zero');
            assert(slash_amount > 0, 'Slash amount must be positive');

            let current_reputation = self.worker_reputation.read(worker);
            let new_reputation = if current_reputation > slash_amount {
                current_reputation - slash_amount
            } else {
                1_u16 // Minimum reputation
            };

            self.worker_reputation.write(worker, new_reputation);
            self.worker_jobs_failed.write(worker, self.worker_jobs_failed.read(worker) + 1);

            // Emit event
            self
                .emit(
                    ReputationSlashed {
                        worker,
                        old_reputation: current_reputation,
                        new_reputation,
                        slash_amount,
                        reason: 'misconduct' // Could be made configurable
                    },
                );
        }

        fn get_worker_status(
            self: @ContractState, worker: ContractAddress,
        ) -> (bool, u16, u32, u32) {
            let verified = self.worker_verified.read(worker);
            let reputation = self.worker_reputation.read(worker);
            let jobs_completed = self.worker_jobs_completed.read(worker);
            let jobs_failed = self.worker_jobs_failed.read(worker);

            (verified, reputation, jobs_completed, jobs_failed)
        }

        fn get_minimum_reputation_for_job(self: @ContractState, job_id: felt252) -> u16 {
            let min_rep = self.job_minimum_reputation.read(job_id);
            if min_rep == 0 {
                400_u16
            } else {
                min_rep
            } // Default minimum reputation
        }

        fn is_worker_eligible(
            self: @ContractState, worker: ContractAddress, job_id: felt252,
        ) -> bool {
            // Check if worker exists and is registered
            let registration_time = self.worker_registration_time.read(worker);
            if registration_time == 0 {
                return false; // Not registered
            }

            // Check verification status
            let verified = self.worker_verified.read(worker);
            if !verified {
                return false; // Must be verified
            }

            // Check reputation requirement
            let worker_reputation = self.worker_reputation.read(worker);
            let min_reputation = self.get_minimum_reputation_for_job(job_id);
            if worker_reputation < min_reputation {
                return false; // Insufficient reputation
            }

            // Check if worker has too many recent failures
            let jobs_completed = self.worker_jobs_completed.read(worker);
            let jobs_failed = self.worker_jobs_failed.read(worker);
            let total_jobs = jobs_completed + jobs_failed;

            if total_jobs > 5 {
                let failure_rate = (jobs_failed * 100) / total_jobs;
                if failure_rate > 30 { // More than 30% failure rate
                    return false;
                }
            }

            true
        }
    }
}
