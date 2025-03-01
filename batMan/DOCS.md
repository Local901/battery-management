# Home Assistant Add-on: Battery manager

## How to use

This add-on helps you to manager your SMA tripower transformer connected home battery charge and discharge.

### Mode: None

This mode releases control back to the transformer.

### Mode: Charge

This mode takes control away from the transformer and forces it to charge up to 5kW/h.

### Mode: Discharge

This mode takes control away from the transformer and forces it to discharge up to 5kW/h.

### Mode: Schedule (24h clock)

This mode uses a schedule to time control changes that have been configured beforehand. It starts at the current time with the action that was configured last if no action was configured it will start in mode `none`.

The schedule will trigger the next item on the schedule when the time has passed.

#### Syntax:

* None: `0` EG `d0h13: 0`
* Charge: `c <power>` EG `d0h13: c 1500`
* Discharge: `d <power>` EG `d0h13: d 1500`
* Anything that doesn't match previous actions will be ignored.
