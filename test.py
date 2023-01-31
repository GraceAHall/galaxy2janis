import importlib_metadata

additional_templates = {}
eps = importlib_metadata.entry_points()
for entrypoint in eps:
    additional_templates[entrypoint.name] = entrypoint.load()
    print()
print()