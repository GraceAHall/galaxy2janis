


from typing import Union

from galaxy_interaction.mock import MockApp
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
    i = app.dataset_counter
    path = varname
    varrep = '__ʕ•́ᴥ•̀ʔっ♡_' + varname
    app.dataset_counter += 1

    if iotype == 'input':
        return JobToInputDatasetAssociation(name=varname, dataset=generate_hda(app, i, path, varrep))
    elif iotype == 'output':
        return JobToOutputDatasetAssociation(name=varname, dataset=generate_hda(app, i, path, varrep))
    raise RuntimeError('iotype must be "input" or "output" when generating a dataset')


def generate_hda(app: MockApp, id: int, name: str, path: str) -> HistoryDatasetAssociation:
    hda = HistoryDatasetAssociation(name=name, metadata=dict())
    hda.dataset = Dataset(id=id, external_filename=path)
    hda.dataset.metadata = dict()
    hda.children = []
    app.model.context.add(hda)
    app.model.context.flush()
    return hda












