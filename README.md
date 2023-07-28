# ndx-probeinterface Extension for NWB

Description of the extension

## Installation


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

---
This extension was created using [ndx-template](https://github.com/nwb-extensions/ndx-template).
