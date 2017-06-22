import docopt


_FORMAT_DICTIONARY = dict(
    # Documentation
    doc_usage=gpd.usage(),

    # Parameters
    param_database=gpn.database(),

    # Default values
    default_training_value=gdv.training_value(),

    # Miscellaneous
    global_name=ggv.name()
)


def parse_args_main_entry_point() -> None:
    global _FORMAT_DICTIONARY

    documentation = """{global_name}

Usage:
  {doc_usage}

Options:

""".format(**_FORMAT_DICTIONARY).format(**_FORMAT_DICTIONARY)

    arguments = docopt.docopt(documentation, version=ggv.version(), help=True)
    cleaned_arguments = clean_args(arguments)

    env.arguments = arguments
    env.cleaned_arguments = cleaned_arguments

    _init_statistics(cleaned_arguments)


def parse_args_forest_entry_point() -> dict:
    pass


def parse_args_forest_reduction_entry_point() -> dict:
    pass


if __name__ == "__main__":
    pass
