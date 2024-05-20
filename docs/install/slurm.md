# Configuring Slurm

## How it works

For each cluster you have defined in keystone, it is assumed that a corresponding cluster of the same name is defined 
in Slurm.

Keystone's usage limit updating functionality will communicate with your Slurm installation, updating the a Research
Group's limits by modifying the corresponding slurm account found on the cluster (except the root association).

It gets and sets the **current limit** with Slurm account/association level 
[`GrpTresMins=billing`](https://slurm.schedmd.com/resource_limits.html#assoc_grptresmins) value.

The **usage** on a given cluster is from sshare's [GrpTRESRaw](https://slurm.schedmd.com/sshare.html#OPT_GrpTRESRaw) 
value.

Unfortunately, Slurm's Fairshare component of its job priority calculation also utilizes this, so a few configuration
constraints are required. These are detailed in the section below.

## System Setup

Keystone makes the following assumptions about your Slurm configuration:

- One or more clusters that are also represented in your Keystone Cluster model
- Association structure with this format:
    Root association
        PI Assoc1
            User1
            User2
            User3
            ...
        PI Assoc2
            User5
            User6
            ...
        ...
- Username of the account owner / PI as the "Description field" for each Slurm Account/Association
- You are using Slurm's [MultiFactor Priority Plugin](https://slurm.schedmd.com/priority_multifactor.html)
- TRESBillingWeights are set on each partition, with PriorityFlags=MAX_TRES
- RawUsage has been reset prior to using limits functionality
- No decay of RawUsage over time
    PriorityDecayHalfLife=00:00:00
    PriorityUsageResetPeriod=NONE
