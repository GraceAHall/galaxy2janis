


from typing import Optional

from gx.interaction.mock import MockApp
from galaxy.datatypes.sniff import guess_ext
from galaxy.model import (
    Dataset,
    HistoryDatasetAssociation,
    JobToInputDatasetAssociation,
    JobToOutputDatasetAssociation,
)


def generate_input_dataset(app: MockApp, varname: str, filepath: str) -> JobToInputDatasetAssociation:
    """
    creates a dataset association. 
    this process creates a dataset and updates the sql database model.
    """
    #varrep = 'gxparam_' + varname
    app.dataset_counter += 1
    return JobToInputDatasetAssociation(
        name=varname, 
        dataset=generate_hda(app, app.dataset_counter, varname, filepath=filepath)
    )

def generate_output_dataset(app: MockApp, varname: str, ftype: str) -> JobToOutputDatasetAssociation:
    app.dataset_counter += 1
    return JobToOutputDatasetAssociation(
        name=varname, 
        dataset=generate_hda(app, app.dataset_counter, varname, ftype=ftype)
    )

def generate_hda(app: MockApp, id: int, name: str, ftype: Optional[str]=None, filepath: Optional[str]=None) -> HistoryDatasetAssociation:
    if filepath:
        sniff_order = app.datatypes_registry.sniff_order
        ext = guess_ext(fname=filepath, sniff_order=sniff_order)
        hda = HistoryDatasetAssociation(name=name, extension=ext, metadata=dict())
    elif ftype:
        ext = ftype
        hda = HistoryDatasetAssociation(name=name, extension=ext, metadata=dict())
    else:
        hda = HistoryDatasetAssociation(name=name, metadata=dict())
    hda.dataset = Dataset(id=id, external_filename=name)
    hda.dataset.metadata = dict()
    hda.children = []
    app.model.context.add(hda)
    app.model.context.flush()
    return hda












