




"""
get param dict
override param dict values with test values
jsonify & return
"""

"""
def to_job_dict(self, value_overrides: Optional[dict]=None) -> dict:
    # comment
    job_dict = self.get_job_dict()

    if value_overrides is not None:
        job_dict = self.override_job_dict_vals(job_dict, value_overrides)

        # incase anything went wrong matching test values to tool params
        if job_dict is None:
            return None

    # testing purposes
    job_dict = self.jsonify_job_dict(job_dict)
    return job_dict
"""
import json


class JobDict:
    pass


class JobDictifier:
    pass


def get_job_dict(inreg: InputRegister) -> dict:
    



    job_dict = {}

    for varname, param in self.params.items():
        varpath = varname.split('.')
        node = job_dict
        
        for i, text in enumerate(varpath):
            if text not in node:
                if i == len(varpath) - 1:
                    # terminal path, add param to node
                    node[text] = self.get_param_default_value(param)
                    break
                else:
                    # create new node for section
                    node[text] = {}

            node = node[text]    
    
    return job_dict


def override_job_dict_vals(self, job_dict: dict, value_overrides: dict) -> Optional[dict]:
    for varname, value in value_overrides.items():
        varpath = varname.split('.')
        node = job_dict

        for i, text in enumerate(varpath):
            # terminal path, add / overwrite value
            if i == len(varpath) - 1:
                node[text] = value
                break

            # not terminal path, but subdict doesn't 
            # exist for some reason (probably repeat param)
            elif text not in node:
                return None
                #node[text] = {}

            node = node[text]

    return job_dict


def jsonify_job_dict(self, job_dict: dict) -> dict:
    for key, val in job_dict.items():
        if isinstance(val, dict):
            job_dict[key] = json.dumps(val)  
    return job_dict
