


from containers.Container import Container
from gx.xmltool.requirements import Requirement


image_presets = {
    'python': [
        {
            'image_type': 'docker',
            'repo': 'python',
            'tag': '3.10',
            'url': 'quay.io/biocontainers/python:3.10',
            '_timestamp': 'Tue, 1 Mar 2022 18:45:00 -0000',
        }
    ]
}

def get_images_preset(requirement: Requirement) -> list[Container]:
    out: list[Container] = []
    if requirement.name in image_presets:
        for details in image_presets[requirement.name]:
            out.append(Container(details))
    return out
