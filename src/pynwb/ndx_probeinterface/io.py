from typing import Union, List, Optional
import numpy as np
from probeinterface import Probe, ProbeGroup
from pynwb.file import Device

unit_map = {
    "um": "micrometer",
    "mm": "millimeter",
    "m": "meter",
}
inverted_unit_map = {v: k for k, v in unit_map.items()}


def from_probeinterface(probe_or_probegroup: Union[Probe, ProbeGroup]) -> List[Device]:
    """
    Construct ndx-probeinterface Probe devices from a probeinterface.Probe

    Parameters
    ----------
    probe_or_probegroup: Probe or ProbeGroup
        Probe or ProbeGroup to convert to ndx-probeinterface Probe devices

    Returns
    -------
    devices: list
        The list of ndx-probeinterface Probe devices
    """
    assert isinstance(probe_or_probegroup, (Probe, ProbeGroup)), f"The input must be a Probe or ProbeGroup, not {type(probe_or_probegroup)}"
    if isinstance(probe_or_probegroup, Probe):
        probes = [probe_or_probegroup]
    else:
        probes = probe_or_probegroup.probes
    devices = []
    for probe in probes:
        devices.append(_single_probe_to_nwb_device(probe))
    return devices



def to_probeinterface(ndx_probe) -> Probe:
    """
    Construct a probeinterface.Probe from ndx_probeinterface.Probe

    Parameters
    ----------
    ndx_probe: ndx_probeinterface.Probe
        ndx_probeinterface.Probe to convert to probeinterface.Probe

    Returns
    -------
    Probe: probeinterface.Probe
    """
    ndim = ndx_probe.ndim
    unit = inverted_unit_map[ndx_probe.unit]
    polygon = ndx_probe.planar_contour

    positions = []
    shapes = []

    contact_ids = None
    shape_params = None
    shank_ids = None
    plane_axes = None
    device_channel_indices = None

    possible_shape_keys = ["radius", "width", "height"]
    contact_table = ndx_probe.contact_table

    positions.append(contact_table["contact_position"][:])
    shapes.append(contact_table["contact_shape"][:])
    if "contact_id" in contact_table.colnames:
        if contact_ids is None:
            contact_ids = []
        contact_ids.append(contact_table["contact_id"][:])
    if "device_channel_index_pi" in contact_table.colnames:
        if device_channel_indices is None:
            device_channel_indices = []
        device_channel_indices.append(contact_table["device_channel_index_pi"][:])
    if "contact_plane_axes" in contact_table.colnames:
        if plane_axes is None:
            plane_axes = []
        plane_axes.append(contact_table["contact_plane_axes"][:])
    if "shank_id" in contact_table.colnames:
        if shank_ids is None:
            shank_ids = []
        shank_ids.append(contact_table["shank_id"][:])
    for possible_shape_key in possible_shape_keys:
        if possible_shape_key in contact_table.colnames:
            if shape_params is None:
                shape_params = []
            shape_params.append([{possible_shape_key: val} for val in contact_table[possible_shape_key][:]])

    positions = [item for sublist in positions for item in sublist]
    shapes = [item for sublist in shapes for item in sublist]

    if contact_ids is not None:
        contact_ids = [item for sublist in contact_ids for item in sublist]
    if plane_axes is not None:
        plane_axes = [item for sublist in plane_axes for item in sublist]
    if shape_params is not None:
        shape_params = [item for sublist in shape_params for item in sublist]
    if shank_ids is not None:
        shank_ids = [item for sublist in shank_ids for item in sublist]
    if device_channel_indices is not None:
        device_channel_indices = [item for sublist in channel_indices for item in sublist]

    probeinterface_probe = Probe(ndim=ndim, si_units=unit)
    probeinterface_probe.set_contacts(
        positions=positions, shapes=shapes, shape_params=shape_params, plane_axes=plane_axes, shank_ids=shank_ids
    )
    probeinterface_probe.set_contact_ids(contact_ids=contact_ids)
    if device_channel_indices is not None:
        probeinterface_probe.set_device_channel_indices(channel_indices=device_channel_indices)
    probeinterface_probe.set_planar_contour(polygon)

    return probeinterface_probe


def _single_probe_to_nwb_device(probe: Probe):
    from pynwb import load_namespaces, get_class

    Probe = get_class("Probe", "ndx-probeinterface")
    ContactTable = get_class("ContactTable", "ndx-probeinterface")

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

    contact_table = ContactTable(
        name="ContactTable",
        description="Contact Table for ProbeInterface",
    )

    for index in np.arange(probe.get_contact_count()):
        kwargs = dict(
            contact_position=contact_positions[index],
            contact_plane_axes=contact_plane_axes[index],
            contact_id=contact_ids[index],
            contact_shape=contacts_arr["contact_shapes"][index],
        )
        for k in shape_keys:
            kwargs[k] = contacts_arr[k][index]
        if probe.device_channel_indices is not None:
            kwargs["device_channel_index_pi"] = probe.device_channel_indices[index]
        if probe.shank_ids is not None:
            kwargs["shank_id"] = probe.shank_ids[index]
        contact_table.add_row(kwargs)

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
        model_name=model_name,
        serial_number=serial_number,
        manufacturer=manufacturer,
        ndim=probe.ndim,
        unit=unit_map[probe.si_units],
        planar_contour=planar_contour,
        contact_table=contact_table
    )

    return probe_device
