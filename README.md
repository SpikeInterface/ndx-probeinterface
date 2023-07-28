# ndx-probeinterface Extension for NWB

`ndx-probeinterface` is an extension of the NWB format to formally define information about neural probes as data types in NWB files. It comes with helper functions to easily construct `ndx-probeinterface.Probe` from `probeinterface.Probe` and vice versa.

## Installation
```python
pip install ndx_probeinterface
```

## Usage

### Going from a `ndx_probeinterface.Probe` object to a `probeinterface.Probe` object 
```python
import ndx_probeinterface
pi_probe = ndx_probeinterface.to_probeinterface(ndx_probe)
```

### Going from a `probeinterface.Probe` object to a `ndx_probeinterface.Probe` object 
```python
import ndx_probeinterface
ndx_probe = ndx_probeinterface.from_probe(pi_probe)
```

## Future plans
- Add information about the headstage used for data acquisition
- Remove redundant information from `ElectrodeTable`
- Incorporate this NDX into the core NWB schema

---
This extension was created using [ndx-template](https://github.com/nwb-extensions/ndx-template).
