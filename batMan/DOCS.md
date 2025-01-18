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

This mode uses a schedule to time control changes that have been configured beforehand. __It always starts from the first item in the schedule.__ It starts with mode `none`.

The schedule will trigger the next item on the schedule when the time has passed.

#### Syntax:

* None: `<time: 00:00> 0` EG `13:15 0`
* Charge: `<time: 00:00> c <power>` EG `13:15 c 1500`
* Discharge: `<time: 00:00> d <power>` EG `13:15 d 1500`
