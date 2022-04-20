


import os
import tarfile
import wget

from startup.ExeSettings import ToolExeSettings
import utils.etree as etree_utils 


def handle_downloads(intended_tool_id: str, esettings: ToolExeSettings) -> ToolExeSettings:
    esettings.xmldir = download_repo(esettings)
    esettings.xmlfile = select_xml_source(intended_tool_id, esettings)
    return esettings

def download_repo(esettings: ToolExeSettings) -> str: 
    uri = esettings.remote_url
    download_folder = esettings.get_download_dir()
    tarball_filename: str = wget.download(uri, out=download_folder)
    tar = tarfile.open(tarball_filename, "r:gz")
    tar.extractall(path=download_folder)
    tar.close()
    os.remove(tarball_filename)
    local_folder_name = tarball_filename.rsplit('.tar', 1)[0]
    return local_folder_name

def select_xml_source(intended_tool_id: str, esettings: ToolExeSettings) -> str:
    assert(esettings.xmldir)
    xmls = [x for x in os.listdir(esettings.xmldir) if x.endswith('.xml') and 'macros' not in x]
    if len(xmls) == 0:  # if no xmls, theres some error
        pass
    elif len(xmls) == 1:  # if only 1 valid xml, return
        return xmls[0]
    else: # else, open each and look at the tool_id and match to esettings
        for xml_file in xmls:
            full_path = os.path.join(esettings.xmldir, xml_file)
            xml_tool_id = etree_utils.get_xml_tool_id(full_path)
            if xml_tool_id == intended_tool_id:
                return xml_file
    raise RuntimeError('no valid tool xml in downloaded wraper folder')
            

