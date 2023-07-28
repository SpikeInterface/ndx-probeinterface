from typing import Union, List, Optional
import numpy as np
from probeinterface import Probe, ProbeGroup

unit_map = {
    "um": "micrometer",
    "mm": "millimeter",
    "m": "meter",
}
inverted_unit_map = {v: k for k, v in unit_map.items()}

shape_words = ['radius', 'width', 'width/height']

def from_probe(probe: Probe):
    """
    Construct ndx-probeinterface Probe devices from a probeinterface.Probe

    Parameters
    ----------
    probe_or_probegroup: Probe or ProbeGroup
        Probe or ProbeGroup to convert to ndx-probeinterface Probe devices
    
    Returns
    -------
    devices: ndx_probeinterface.Probe 
        The ndx-probeinterface Probe device
    """
    assert isinstance(probe, Probe)
    return _single_probe_to_nwb_device(probe)


def from_probegroup(probegroup: ProbeGroup):
    """
    Construct ndx-probeinterface Probe devices from a probeinterface.ProbeGroup

    Parameters
    ----------
    probegroup: ProbeGroup
        ProbeGroup to convert to ndx-probeinterface Probe devices

    Returns
    -------
    list
        List of ndx-probeinterface Probe devices
    """
    assert isinstance(probegroup, ProbeGroup)
    devices = []
    for probe in probegroup.probes:
        devices.append(_single_probe_to_nwb_device(probe))
    return devices


def to_probeinterface(ndx_probeinterface_Probe)->Probe:
    """
    Construct a probeinterface.Probe from ndx-probeinterface Probe

    Parameters
    ----------
    ndx_probeinterface_Probe: ndx_probeinterface.Probe
        ndx_probeinterface.Probe to convert to probeinterface.Probe 
    
    Returns
    -------
    Probe: probeinterface.Probe 
    """
    ndim = ndx_probeinterface_Probe.ndim
    unit = inverted_unit_map[ndx_probeinterface_Probe.unit]
    polygon = ndx_probeinterface_Probe.planar_contour
    
    positions = []
    shapes = []
    shape_params = []
    shank_ids = []
    plane_axes = []
    for shank in ndx_probeinterface_Probe.shanks:
        positions.append(shank.contact_table['contact_position'][:])
        shapes.append(shank.contact_table['contact_shape'][:])
        shank_ids.append(shank.shank_id * len(shank.contact_table))
        plane_axes.append(shank.contact_table['contact_plane_axes'][:])
        # WARNING: currently assumes that all the contacts have the same shape
        shape_word = [shape for shape in shape_words if shape in shank.contact_table[:].columns][0]
        shape_params.append([{shape_word: val} for val in shank.contact_table[shape_word][:]])

    probeinterface_Probe = Probe(ndim=ndim, si_units=unit)
    probeinterface_Probe.set_contacts(positions=positions,
                                      shapes=shapes,
                                      shape_params=shape_params,
                                      plane_axes=plane_axes,
                                      shank_ids=shank_ids)
    probeinterface_Probe.set_planar_contour(polygon)

    return probeinterface_Probe


def _single_probe_to_nwb_device(probe: Probe):
    from pynwb import load_namespaces, get_class

    Probe = get_class('Probe', 'ndx-probeinterface')
    Shank = get_class('Shank', 'ndx-probeinterface')
    ContactTable = get_class('ContactTable', 'ndx-probeinterface')

    contact_positions = probe.contact_positions
    contact_plane_axes = probe.contact_plane_axes
    contact_ids = probe.contact_ids
    contacts_arr = probe.to_numpy()
    shank_ids = probe.shank_ids
    planar_contour = probe.probe_planar_contour

    if shank_ids is not None:
        unique_shanks = np.unique(shank_ids)
    else:
        unique_shanks = ["0"]

    shape_keys = []
    for shape_params in probe.contact_shape_params:
        keys = list(shape_params.keys())
        for k in keys:
            if k not in shape_keys:
                shape_keys.append(k)

    shanks = []
    contact_tables = []
    for i_s, unique_shank in enumerate(unique_shanks):
        if shank_ids is not None:
            shank_indices = np.nonzero(shank_ids == unique_shank)[0]
            pi_shank = probe.get_shanks()[i_s]
            shank_name = f"Shank {pi_shank.shank_id}"
            shank_id = str(pi_shank.shank_id)
        else:
            shank_indices = np.arange(probe.get_contact_count())
            shank_name = "Shank 0"
            shank_id = "0"

        contact_table = ContactTable(
            name="ContactTable",
            description="Contact Table for ProbeInterface",
        )
        
        if probe.device_channel_indices is not None:
            contact_table.add_column(name="device_channel_index", 
                                     description="Device channel index")
        for k in shape_keys:
            contact_table.add_column(name=k, 
                                     description="Shape parameter for electrode")

        for index in shank_indices:
            kwargs = dict(
                contact_position=contact_positions[index],
                contact_plane_axes=contact_plane_axes[index],
                contact_id=contact_ids[index],
                contact_shape=contacts_arr["contact_shapes"][index],
            )
            for k in shape_keys:
                kwargs[k] = contacts_arr[k][index]
            if probe.device_channel_indices is not None:
                kwargs["device_channel_index"] = probe.device_channel_indices[index]
            contact_table.add_row(kwargs)
        contact_tables.append(contact_table)
        shank = Shank(name=shank_name,
                      shank_id=shank_id,
                      contact_table=contact_table)
        shanks.append(shank)

    if "serial_number" in probe.annotations:
        serial_number = probe.annotations["serial_number"]
    else:
        serial_number = None
    if "model_name" in probe.annotations:
        model_name = probe.annotations["model_name"]
    else:
        model_name = None
    if "manufacturer" in probe.annotations:
        manufacturer = probe.annotations["manufacturer"]
    else:
        manufacturer = None

    probe_device = Probe(
        name=probe.annotations["name"],
        shanks=shanks,
        model_name=model_name,
        serial_number=serial_number,
        manufacturer=manufacturer,
        ndim=probe.ndim,
        unit=unit_map[probe.si_units],
        planar_contour=planar_contour
    )

    return probe_device
