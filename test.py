
import json

print(json.dumps({
    'db': 'resfinder',
    'no_header': False,
    'min_dna_id': 80,
    'min_cov': None,
}))