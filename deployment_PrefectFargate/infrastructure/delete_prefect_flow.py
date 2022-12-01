import asyncio
import sys
from prefect.client import get_client

# Remove flows
async def remove_flows(flow2delete):
    orion_client = get_client()
    flows = await orion_client.read_flows()
    for flow in flows:
        flow_id = flow.id
        if flow.name == flow2delete:
            print(f"Deleting flow: {flow.name}, {flow_id}")
            await orion_client._client.delete(f"/flows/{flow_id}")
            print(f"Flow with UUID {flow_id} deleted")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        flow2delete = sys.argv[1]
        asyncio.run(remove_flows(flow2delete))
    else:
        raise SystemExit("No flow passed.")
    
