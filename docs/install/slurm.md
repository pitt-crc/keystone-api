# Configuring Slurm

Keystone is agnostic to most Slurm settings, and requires minimal modification to a running Slurm cluster.
However, 

## Enable Resource Tracking

Slurm categorizes system usage in terms of trackable resources (TRES).
In order to impose a usage limit on a computational resource, that resource must be represented in Slurm as a TRES.
Resource tracking for common TRES' like CPU, memory, and energy usage is enabled by default.
However, administrators may wish to extend the default list to enable limits on additional resource types.

The `AccountingStorageTRES` setting is used to extend the default list of TRES values stored in the Slurm database.

!!! Example "Example: Tracking GPU usage"

    The following example enables tracking for GPU resources.

    ```
    AccountingStorageTRES=gres/gpu
    ```

## Disable Usage Decay

Most Slurm installations default to using the [multifactor priority plugin](https://slurm.schedmd.com/priority_multifactor.html) to schedule jobs.
This can be confirmed explicitly by checking the Slurm `PriorityType` setting. 

In order to ensure these values are recorded consistently, the `PriorityDecayHalfLife` and `PriorityUsageResetPeriod` settings need to be disabled:

```
PriorityDecayHalfLife=00:00:00
PriorityUsageResetPeriod=NONE
```

!!! Important

    Disabling the `PriorityDecayHalfLife` and `PriorityUsageResetPeriod` values may affect your Slurm fairshare policy.
    Administrators should adjust the rest of their fairshair policy settings as they see appropriate. 

## Configuring Charging Rates

Set `TRESBillingWeights` for each partition.

```
PartitionName=partition_name TRESBillingWeights="CPU=1.0,Mem=1.0G"
```

Billing weights are definable in variety of units. 
See the [Slurm documentation](https://slurm.schedmd.com/tres.html) for more details.

Set `PriorityFlags`.

```
PriorityFlags=MAX_TRES
```

If PriorityFlags=MAX_TRES is configured, the billable TRES is calculated as the MAX of individual TRESs on a node (e.g. cpus, mem, gres) plus the sum of all global TRESs (e.g. licenses).
Only TRES defined in `AccountingStorageTRES` are available for `TRESBillingWeights`.
