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

This mode uses a schedule to time control changes that have been configured beforehand. It is a record of every hour of the day. For each hour you can define which action should be taken. Below you will see how to define a action for a given hour. **All options can be stacked one after the other to be bale to define more than one at the time.**

#### charge option

* Charging is indicated by a `c` followed by the number of watt you want to charge. If it is negative it will discharge.
  * `c 5000`
* Discharge is indicated ba a `d` followed by the number of watt you want to discharge. If it is negative it will charge.
  * `d 5000`
* If nothing related to charging has been defined it will default to mode `None` and will free the inverter to do what it wants. This is also achievable by charging or discharging with 0 watt.

#### Minimum charge percentage

* This is a way to overwrite the minimum discharge percentage for a given hour. This action is indicated by `mcp` followed by the percentage that you would fill in in another field in the configuration of this addon. This value is bounded from 0 to 100. Going outside this range will automatically set it to the closest in bound value.
