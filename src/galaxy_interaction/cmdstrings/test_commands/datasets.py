


from typing import Union

from galaxy_interaction.mock import MockApp
from galaxy.datatypes.sniff import guess_ext
from galaxy.model import (
    Dataset,
    HistoryDatasetAssociation,
    JobToInputDatasetAssociation,
    JobToOutputDatasetAssociation,
)


def generate_dataset(app: MockApp, varname: str, iotype: str) -> Union[JobToInputDatasetAssociation, JobToOutputDatasetAssociation]:
    """
    creates a dataset association. 
    this process creates a dataset and updates the sql database model.
    """
    # TODO HERE ALMOST THERE U CAN DO IT!
    i = app.dataset_counter
    varrep = 'gxvar_' + varname
    app.dataset_counter += 1

    if iotype == 'input':
        return JobToInputDatasetAssociation(name=varname, dataset=generate_hda(app, i, varname, varrep))
    elif iotype == 'output':
        return JobToOutputDatasetAssociation(name=varname, dataset=generate_hda(app, i, varname, varrep))
    raise RuntimeError('iotype must be "input" or "output" when generating a dataset')


def generate_hda(app: MockApp, id: int, name: str, path: str) -> HistoryDatasetAssociation:
    sniff_order = app.datatypes_registry.sniff_order
    ext = guess_ext()
    hda = HistoryDatasetAssociation(name=name, metadata=dict())
    hda.dataset = Dataset(id=id, external_filename=path)
    hda.dataset.metadata = dict()
    hda.children = []
    app.model.context.add(hda)
    app.model.context.flush()
    return hda












