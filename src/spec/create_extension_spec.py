# -*- coding: utf-8 -*-
import os.path

from pynwb.spec import (NWBNamespaceBuilder,
                        export_spec,
                        NWBGroupSpec,
                        NWBAttributeSpec,
                        NWBDatasetSpec)

def main():
    # these arguments were auto-generated from your cookiecutter inputs
    ns_builder = NWBNamespaceBuilder(
        doc="""Extension for defining neural probes in the probeinterface format""",
        name="""ndx-probeinterface""",
        version="""0.1.0""",
        author=["Alessio Buccino",
                "Kyu Hyun Lee"
                "Geeling Chau"],
        contact=["alessiop.buccino@gmail.com",
                 "kyuhyun9056@gmail.com",
                 "gchau@caltech.edu"]
    )

    # TODO: specify the neurodata_types that are used by the extension as well
    # as in which namespace they are found.
    # this is similar to specifying the Python modules that need to be imported
    # to use your new data types.
    # all types included or used by the types specified here will also be
    # included.
    ns_builder.include_type(
        data_type="Device",
        namespace="core"
    )
    ns_builder.include_namespace('hdmf-common')
    # TODO: define your new data types
    # see https://pynwb.readthedocs.io/en/latest/extensions.html#extending-nwb
    # for more information
    contact = NWBGroupSpec(
        doc="Neural probe contacts according to probeinterface specification",
        datasets=[
            NWBDatasetSpec(
                name="contact_id",
                doc="unique ID of the contact",
                dtype="text",
                neurodata_type_inc="VectorData"
            ),
            NWBDatasetSpec(
                name="contact_shape",
                doc="shape of the contact; e.g. 'circle'",
                dtype="text",
                neurodata_type_inc="VectorData"
            ),
            NWBDatasetSpec(
                name="contact_plane_axes",
                doc="dimension of the probe",
                dtype="float",
                dims=[['num_contacts', 'v1, v2', 'x,y'], ['num_contacts', 'v1,v2', 'x, y, z']],
                shape=[[None, 2, 2], [None, 2,3]],
                neurodata_type_inc="VectorData"
            ),
            NWBDatasetSpec(
                name="contact_position",
                doc="dimension of the probe",
                dtype="float",
                dims=[['num_contacts', 'x, y'], ['num_contacts','x, y, z']],
                shape=[[None, 2], [None, 3]],
                neurodata_type_inc="VectorData"
            ),
            NWBDatasetSpec(
                name="device_channel_index",
                doc="ID of the channel connected to the contact",
                dtype="int",
                neurodata_type_inc="VectorData"
            ),
            # NWBDatasetSpec(
            #     name="electrode",
            #     doc="electrode ID in ElectrodeTable; should link to ElectrodeTable",
            #     neurodata_type_inc="DynamicTableRegion"
            # ),
        ],
        neurodata_type_inc="DynamicTable",
        neurodata_type_def="ContactTable",
    )
    shank = NWBGroupSpec(
        doc="Neural probe shanks according to probeinterface specification",
        attributes=[
            NWBAttributeSpec(
                name="shank_id",
                doc="ID of the shank in the probe; must be a str",
                dtype="text",
                required=True,
            ),
        ],
        groups=[
            NWBGroupSpec(
                doc="Neural probe contacts according to probeinterface specification",
                neurodata_type_inc="ContactTable",
                quantity=1
            )
        ],
        neurodata_type_inc="NWBContainer",
        neurodata_type_def="Shank",
    )
    probe = NWBGroupSpec(
        doc="Neural probe object according to probeinterface specification",
        attributes=[
            NWBAttributeSpec(
                name="ndim",
                doc="dimension of the probe",
                dtype="int",
                required=True,
                default_value=2
            ),
            NWBAttributeSpec(
                name="model_name",
                doc="model of the probe; e.g. 'Neuropixels 1.0'",
                dtype="text",
                required=False,
            ),
            NWBAttributeSpec(
                name="serial_number",
                doc="serial number of the probe",
                dtype="text",
                required=False,
            ),
            NWBAttributeSpec(
                name="unit",
                doc="SI unit used to define the probe; e.g. 'meter'.",
                dtype="text",
                required=True,
                default_value='micrometer'
            ),
        ],
        neurodata_type_inc="Device",
        neurodata_type_def="Probe",
        groups=[
            NWBGroupSpec(
                doc="Neural probe shank object according to probeinterface specification",
                neurodata_type_inc="Shank",
                quantity="*"
            )
        ]
    )

    new_data_types = [probe, shank, contact]

    # export the spec to yaml files in the spec folder
    output_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'spec'))
    export_spec(ns_builder, new_data_types, output_dir)
    print('Spec files generated. Please make sure to rerun `pip install .` to load the changes.')


if __name__ == '__main__':
    # usage: python create_extension_spec.py
    main()
