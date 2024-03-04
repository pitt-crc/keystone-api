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


def set_cluster_limit(account_name: str, cluster_name: str, limit: int, in_hours: bool = True) -> None:
    """Update the current TRES Billing usage limit to the provided limit on a given cluster for a given account
    with sacctmgr. The default expected limit unit is Hours, and a conversion takes place as Slurm uses minutes.

    Args:
        account_name: The name of the account to get usage for
        cluster_name: The name of the cluster to get usage on
        limit: Number of billing TRES hours to set the usage limit to
        in_hours: Boolean value for whether (True) or not (False) the limit provided is in Hours (Default: True)
    """

    # Convert the input hours to minutes
    if in_hours:
        limit *= 60

    cmd = split(f"sacctmgr modify -i account where account={account_name} cluster={cluster_name} set GrpTresMins=billing={limit}")

    subprocess_call(cmd)


def get_cluster_limit(account_name: str, cluster_name: str, in_hours: bool = True) -> int:
    """Get the current TRES Billing usage limit on a given cluster for a given account with sacctmgr.
    The limit unit coming out of Slurm is minutes, and the default behavior is to convert this to hours.
    This can be skipped with in_hours = False.

    Args:
        account_name: The name of the account to get usage for
        cluster_name: The name of the cluster to get usage on
        in_hours: Boolean value for whether (True) or not (False) the returned limit is in Hours (Default: True)

    Returns:
        An integer representing the total (historical + current) billing TRES limit
    """

    cmd = split(f"sacctmgr show -nP association where account={account_name} cluster={cluster_name} format=GrpTRESMins")

    try:
        limit = re.findall(r'billing=(.*)', subprocess_call(cmd))[0]
    except IndexError:
        log.debug(f"'billing' limit not found in command output from {cmd}, assuming zero for current limit")
        return 0

    limit = int(limit) if limit.isnumeric() else 0

    return limit // 60 if in_hours else limit


def get_cluster_usage(account_name: str, cluster_name: str, in_hours: bool = True) -> int:
    """Get the total billable usage in Hours on a given cluster for a given account. Slurm provides a usage in minutes
    and that values is converted to Hours by default. This can be skipped with in_hours = False.

    Args:
        account_name: The name of the account to get usage for
        cluster_name: The name of the cluster to get usage on
        in_hours: Boolean value for whether (True) or not (False) the returned Usage is in hours (Default: True)

    Returns:
        An integer representing the total (historical + current) billing TRES hours usage from sshare
    """

    cmd = split(f"sshare -nP -A {account_name} -M {cluster_name} --format=GrpTRESRaw")

    try:
        usage = re.findall(r'billing=(.*),fs', subprocess_call(cmd))[0]
    except IndexError:
        log.debug(f"'billing' usage not found in command output from {cmd}, assuming zero for current usage")
        return 0

    usage = int(usage) if usage.isnumeric() else 0

    # Billing TRES comes out of Slurm in minutes, needs to be converted to hours
    return usage // 60 if in_hours else usage
