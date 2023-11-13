"""General utilities for interacting with the Slurm REST API"""

# The functions in this module are listed as examples only
# The actual implementation may very significantly


async def get_accounts(*args, **kwargs) -> list[str]:
    """Return a list of Slurm accounts"""


async def get_usage(*args, **kwargs) -> int:
    """Return the total SU usage for a given account"""


async def update_cluster_account_status(*args, **kwargs) -> None:
    """Lock/unlock user accounts based on the status of their SU allocation"""
