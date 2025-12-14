use galaxyrend_job_registry::job_registry::{IJobRegistryDispatcher, IJobRegistryDispatcherTrait};
use openzeppelin_token::erc20::interface::{IERC20, IERC20Dispatcher, IERC20DispatcherTrait};
use snforge_std::{
    ContractClassTrait, DeclareResultTrait, declare, start_cheat_block_timestamp,
    start_cheat_caller_address, stop_cheat_block_timestamp, stop_cheat_caller_address,
};
use starknet::{ContractAddress, get_caller_address};

// Mock ERC20 contract for testing
#[starknet::contract]
mod MockERC20 {
    use core::num::traits::Zero;
    use openzeppelin_token::erc20::interface::IERC20;
    use starknet::storage::{
        Map, StorageMapReadAccess, StorageMapWriteAccess, StoragePointerReadAccess,
        StoragePointerWriteAccess,
    };
    use starknet::{ContractAddress, get_caller_address};


    #[storage]
    struct Storage {
        balances: Map<ContractAddress, u256>,
        allowances: Map<(ContractAddress, ContractAddress), u256>,
        total_supply: u256,
    }

    #[abi(embed_v0)]
    impl MockERC20Impl of IERC20<ContractState> {
        fn total_supply(self: @ContractState) -> u256 {
            self.total_supply.read()
        }

        fn balance_of(self: @ContractState, account: ContractAddress) -> u256 {
            self.balances.read(account)
        }

        fn allowance(
            self: @ContractState, owner: ContractAddress, spender: ContractAddress,
        ) -> u256 {
            self.allowances.read((owner, spender))
        }

        fn transfer(ref self: ContractState, recipient: ContractAddress, amount: u256) -> bool {
            let sender = get_caller_address();
            let sender_balance = self.balances.read(sender);
            if sender_balance < amount {
                return false;
            }
            self.balances.write(sender, sender_balance - amount);
            self.balances.write(recipient, self.balances.read(recipient) + amount);
            true
        }

        fn transfer_from(
            ref self: ContractState,
            sender: ContractAddress,
            recipient: ContractAddress,
            amount: u256,
        ) -> bool {
            let sender_balance = self.balances.read(sender);
            if sender_balance < amount {
                return false;
            }
            self.balances.write(sender, sender_balance - amount);
            self.balances.write(recipient, self.balances.read(recipient) + amount);
            true
        }

        fn approve(ref self: ContractState, spender: ContractAddress, amount: u256) -> bool {
            let owner = get_caller_address();
            self.allowances.write((owner, spender), amount);
            true
        }
    }

    #[abi(embed_v0)]
    impl MockERC20HelperImpl of super::IMockERC20Helper<ContractState> {
        fn mint(ref self: ContractState, to: ContractAddress, amount: u256) {
            let current_balance = self.balances.read(to);
            self.balances.write(to, current_balance + amount);
            self.total_supply.write(self.total_supply.read() + amount);
        }
    }
}

// Helper Interface for interacting with MockERC20 in tests (minting)
#[starknet::interface]
trait IMockERC20Helper<TContractState> {
    fn mint(ref self: TContractState, to: ContractAddress, amount: u256);
}

fn deploy_mock_erc20() -> ContractAddress {
    let contract = declare("MockERC20").unwrap().contract_class();
    let (contract_address, _) = contract.deploy(@ArrayTrait::new()).unwrap();
    contract_address
}

fn deploy_job_registry(owner: ContractAddress, token_address: ContractAddress) -> ContractAddress {
    let contract = declare("JobRegistry").unwrap().contract_class();
    let mut calldata = ArrayTrait::new();
    calldata.append(owner.into());
    calldata.append(token_address.into());
    let (contract_address, _) = contract.deploy(@calldata).unwrap();
    contract_address
}

#[cfg(test)]
mod tests {
    use galaxyrend_job_registry::job_registry::{
        IJobRegistryDispatcher, IJobRegistryDispatcherTrait,
    };
    use super::*;

    #[test]
    fn test_create_job_success() {
        let token_address = deploy_mock_erc20();
        let owner: ContractAddress = 0x111.try_into().unwrap();
        let job_registry_address = deploy_job_registry(owner, token_address);
        let job_registry = IJobRegistryDispatcher { contract_address: job_registry_address };

        let token = IERC20Dispatcher { contract_address: token_address };

        // Test Params
        let creator_address: ContractAddress = 0x123.try_into().unwrap();
        let asset_cid_part1: felt252 = 0x456;
        let asset_cid_part2: felt252 = 0x789;
        let reward_amount: u256 = u256 { low: 1000, high: 0 };
        let deadline_timestamp: u64 = 1000;

        // Mint tokens to creator
        let token_helper = IMockERC20HelperDispatcher { contract_address: token_address };
        token_helper.mint(creator_address, reward_amount);

        start_cheat_caller_address(job_registry_address, creator_address);

        let job_id = job_registry
            .create_job(asset_cid_part1, asset_cid_part2, reward_amount, deadline_timestamp);

        stop_cheat_caller_address(job_registry_address);

        assert(job_id == 1, 'First job should have ID 1');
        assert(job_registry.get_job_counter() == 1, 'Job counter should be 1');
        assert(job_registry.get_job_creator(job_id) == creator_address, 'Creator should match');
        assert(job_registry.get_job_reward(job_id) == reward_amount, 'Reward should match');

        // Check balance moved to registry
        let registry_balance = token.balance_of(job_registry_address);
        assert(registry_balance == reward_amount, 'Registry should hold funds');
    }

    #[test]
    fn test_cancel_job() {
        let token_address = deploy_mock_erc20();
        let owner: ContractAddress = 0x111.try_into().unwrap();
        let job_registry_address = deploy_job_registry(owner, token_address);
        let job_registry = IJobRegistryDispatcher { contract_address: job_registry_address };

        let token = IERC20Dispatcher { contract_address: token_address };

        let creator_address: ContractAddress = 0x123.try_into().unwrap();
        let reward_amount: u256 = 1000_u256;

        let token_helper = IMockERC20HelperDispatcher { contract_address: token_address };
        token_helper.mint(creator_address, reward_amount);

        start_cheat_caller_address(job_registry_address, creator_address);

        let job_id = job_registry.create_job(0x1, 0x2, reward_amount, 2000);

        // Assert registry has funds
        assert(
            token.balance_of(job_registry_address) == reward_amount, 'Registry should have funds',
        );
        assert(token.balance_of(creator_address) == 0, 'Creator sent funds');

        // Cancel Job
        job_registry.cancel_job(job_id);

        stop_cheat_caller_address(job_registry_address);

        // Verify Refund
        assert(token.balance_of(job_registry_address) == 0, 'Registry empty');
        assert(token.balance_of(creator_address) == reward_amount, 'Creator refunded');
        assert(job_registry.is_job_completed(job_id), 'Job marked completed');
    }

    #[test]
    fn test_approve_work() {
        let token_address = deploy_mock_erc20();
        let owner: ContractAddress = 0x111.try_into().unwrap();
        let job_registry_address = deploy_job_registry(owner, token_address);
        let job_registry = IJobRegistryDispatcher { contract_address: job_registry_address };

        let token = IERC20Dispatcher { contract_address: token_address };

        let creator: ContractAddress = 0x123.try_into().unwrap();
        let worker: ContractAddress = 0x456.try_into().unwrap();
        let reward_amount: u256 = 1000_u256;

        // Warp time forward to avoid 0 timestamp issues
        start_cheat_block_timestamp(job_registry_address, 1000);

        let token_helper = IMockERC20HelperDispatcher { contract_address: token_address };
        token_helper.mint(creator, reward_amount);

        // 1. Create Job
        start_cheat_caller_address(job_registry_address, creator);
        let job_id = job_registry.create_job(0x1, 0x2, reward_amount, 2000);
        stop_cheat_caller_address(job_registry_address);

        // 2. Register Worker
        start_cheat_caller_address(job_registry_address, worker);
        job_registry.register_worker(0x999);
        stop_cheat_caller_address(job_registry_address);

        // Owner verify worker
        start_cheat_caller_address(job_registry_address, owner);
        job_registry.verify_worker(worker, true);
        stop_cheat_caller_address(job_registry_address);

        // 3. Worker Submit
        start_cheat_caller_address(job_registry_address, worker);
        job_registry.submit_result(job_id, 0xA, 0xB);
        stop_cheat_caller_address(job_registry_address);

        // 4. Creator Approve
        start_cheat_caller_address(job_registry_address, creator);
        job_registry.approve_work(job_id);
        stop_cheat_caller_address(job_registry_address);

        // Verify payment
        assert(token.balance_of(worker) == reward_amount, 'Worker paid');
        assert(job_registry.is_job_completed(job_id), 'Job completed');

        stop_cheat_block_timestamp(job_registry_address);
    }
}
