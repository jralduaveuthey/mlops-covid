import asyncio
import sys
from prefect import get_client


async def remove_deployments(deployment2delete):
    client = get_client()
    deployments = await client.read_deployments()
    for deployment in deployments:
        if deployment.name == deployment2delete:
            print(f"Deleting deployment: {deployment.name}")
            await client.delete_deployment(deployment.id)
            print(f"Deployment with UUID {deployment.id} deleted")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        deployment2delete = sys.argv[1]
        asyncio.run(remove_deployments(deployment2delete))
    else:
        raise SystemExit("No deployment passed.")