# ndx-probeinterface Extension for NWB

`ndx-probeinterface` is an extension of the NWB format to formally define information about neural probes as data types in NWB files. It comes with helper functions to easily construct `ndx-probeinterface.Probe` from `probeinterface.Probe` and vice versa.

## Installation
```python
pip install ndx_probeinterface
```

## Usage

### Going from a `probeinterface.Probe`/``ProbeGroup` object to a `ndx_probeinterface.Probe` object 
```python
import ndx_probeinterface

pi_probe = probeinterface.Probe(...)
pi_probegroup = probeinterface.ProbeGroup()

# from_probeinterface always returns a list of ndx_probeinterface.Probe devices
ndx_probes1 = ndx_probeinterface.from_probeinterface(pi_probe)
ndx_probes2 = ndx_probeinterface.from_probeinterface(pi_probegroup)

ndx_probes = ndx_probes1.extend(ndx_probes2)

nwbfile = pynwb.NWBFile(...)

# add Probe as NWB Devices
for ndx_probe in ndx_probes:
    nwbfile.add_device(ndx_probe)
```

### Going from a `ndx_probeinterface.Probe` object to a `probeinterface.Probe` object 
```python
import ndx_probeinterface

# load ndx_probeinterface.Probe objects from NWB file
io = pynwb.NWBH5IO(file_path, 'r', load_namespaces=True)
nwbfile = io.read()

ndx_probes = []
for device in nwbfile:
    if isinstance(device, ndx_probeinterface.Probe):
        ndx_probes.append(device)

# convert to probeinterface.Probe objects
pi_probes = []
for ndx_probe in ndx_probes:
    pi_probe = ndx_probeinterface.to_probeinterface(ndx_probe)
    pi_probes.append(pi_probe)
```

## Future plans
- Add information about the headstage used for data acquisition
- Remove redundant information from `ElectrodeTable`
- Incorporate this NDX into the core NWB schema

---
This extension was created using [ndx-template](https://github.com/nwb-extensions/ndx-template).
