"""Plugin for providing command line functionality to a Slurm installation"""

import logging
import re
from shlex import split
from subprocess import PIPE, Popen
from typing import Collection, List

log = logging.getLogger(__name__)


def subprocess_call(args: List[str]) -> str:
    """Wrapper method for executing shell commands via ``Popen.communicate``

    Args:
        args: A sequence of program arguments

    Returns:
        The piped output to STDOUT and STDERR as strings
    """

    process = Popen(args, stdout=PIPE, stderr=PIPE)
    out, err = process.communicate()

    if process.returncode != 0:
        message = f"Error executing shell command: {' '.join(args)} \n {err.decode('utf-8').strip()}"
        log.error(message)
        raise RuntimeError(message)

    return out.decode("utf-8").strip()


def get_accounts_on_cluster(cluster_name: str) -> Collection[str]:
    """Gather a list of account names for a given cluster from sacctmgr

    Args:
        cluster_name: The name of the cluster to get usage on

    Returns:
        A list of Slurm account names
    """

    cmd = split(f"sacctmgr show -nP account withassoc where parents=root cluster={cluster_name} format=Account")

    out = subprocess_call(cmd)

    return out.split()


def set_cluster_limit(account_name: str, cluster_name: str, limit: int, in_minutes: bool = False) -> None:
    """Update the current TRES Billing hour usage limit to the provided limit on a given cluster for a given account
    with sacctmgr. The default time unit is Hours.

    Args:
        account_name: The name of the account to get usage for
        cluster_name: The name of the cluster to get usage on
        limit: Number of billing TRES hours to set the usage limit to
        in_minutes: Boolean value for whether (True) or not (False) the set limit is in minutes (Default: False)
    """

    if in_minutes:
        limit *= 60

    cmd = split(f"sacctmgr modify account where account={account_name} cluster={cluster_name} set GrpTresRunMins=billing={limit}")

    subprocess_call(cmd)


def get_cluster_limit(account_name: str, cluster_name: str, in_minutes: bool = False) -> int:
    """Get the current TRES Billing Hour usage limit on a given cluster for a given account with sacctmgr.
    The default time unit is Hours.

    Args:
        account_name: The name of the account to get usage for
        cluster_name: The name of the cluster to get usage on
        in_minutes: Boolean value for whether (True) or not (False) the returned limit is in minutes (Default: False)

    Returns:
        An integer representing the total (historical + current) billing TRES limit
    """

    cmd = split(f"sacctmgr show -nP association where account={account_name} cluster={cluster_name} "
                f"format=GrpTRESRunMin")

    limit = re.findall(r'billing=(.*)\n', subprocess_call(cmd))[0]

    if not limit.isnumeric():
        return 0

    limit = int(limit)
    if in_minutes:
        limit *= 60

    return limit


def get_cluster_usage(account_name: str, cluster_name: str, in_hours: bool = True) -> int:
    """Get the total billable usage in minutes on a given cluster for a given account

    Args:
        account_name: The name of the account to get usage for
        cluster_name: The name of the cluster to get usage on
        in_hours: Boolean value for whether (True) or not (False) the returned Usage is in hours (Default: True)

    Returns:
        An integer representing the total (historical + current) billing TRES hours usage from sshare
    """

    cmd = split(f"sshare -nP -A {account_name} -M {cluster_name} --format=GrpTRESRaw")

    usage = re.findall(r'billing=(.*),fs', subprocess_call(cmd))[0]

    if not usage.isnumeric():
        return 0

    usage = int(usage)
    if in_hours:
        usage //= 60

    return usage
