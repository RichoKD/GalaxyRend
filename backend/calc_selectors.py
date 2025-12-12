from starknet_py.utils.data_serializer.events_serializer import EventsSerializer
from starknet_py.hash.selector import get_selector_from_name

events = [
    "JobCreated",
    "ResultSubmitted",
    "JobFinalized",
    "JobCancelled",
    "WorkApproved",
    "WorkerRegistered",
    "WorkerVerified",
    "WorkerReputationUpdated"
]

print("Event Selectors:")
for event in events:
    selector = get_selector_from_name(event)
    print(f"{event}: {hex(selector)}")
