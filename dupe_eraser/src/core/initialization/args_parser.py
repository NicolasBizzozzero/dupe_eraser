""" This module contains all functions related to parsing command-line arguments for all entry points of the package.
It uses the `docopt` package (listed as a dependencie) to easily combine the tedious task of writing documentation
and parsing arguments.
#TODO: We can gain time by not formatting the helping message twice, but by directly formatting the documentation from
#      the format dictionary
"""
import dupe_eraser.src.getters.get_default_value as gdv
import dupe_eraser.src.getters.get_global_variable as ggv
import dupe_eraser.src.getters.get_parameter_documentation as gpd
import dupe_eraser.src.getters.get_parameter_name as gpn
from dupe_eraser.src.core.initialization.args_cleaner import clean_arguments
import docopt


_FORMAT_DICTIONARY = dict(
    # Documentation
    doc_usage=gpd.usage(),
    doc_help_message=gpd.help_message(),
    doc_version=gpd.version(),
    doc_recursive=gpd.recursive(),
    doc_safe=gpd.safe(),
    doc_safe_directory=gpd.safe_directory(),
    doc_check=gpd.check(),
    doc_verbosity=gpd.verbosity(),
    doc_low_memory=gpd.low_memory(),
    doc_hashing_algorithm=gpd.hashing_algorithm(),

    # Parameters
    param_help_message=gpn.help_message(),
    param_version=gpn.version(),
    param_recursive=gpn.recursive(),
    param_safe=gpn.safe(),
    param_safe_directory=gpn.safe_directory(),
    param_check=gpn.check(),
    param_verbosity=gpn.verbosity(),
    param_low_memory=gpn.low_memory(),
    param_hashing_algorithm=gpn.hashing_algorithm(),

    # Default values
    default_safe_directory=gdv.safe_directory(),
    default_verbosity=gdv.verbosity(),
    default_hashing_algorithm=gdv.hashing_algorithm(),

    # Miscellaneous
    global_name=ggv.name()
)


def parse_args_main_entry_point() -> None:
    global _FORMAT_DICTIONARY

    documentation = """{global_name}

Usage:
  {doc_usage}

Options:
  {param_help_message}                 {doc_help_message}
  {param_version}                 {doc_version}
  {param_recursive}               {doc_recursive}
  {param_safe}                    {doc_safe}
  {param_safe_directory}=DIR      {doc_safe_directory}
  {param_check}                   {doc_safe}
  {param_verbosity}=LEVEL         {doc_verbosity}
  {param_low_memory}              {doc_low_memory}
  {param_hashing_algorithm}=ALGO  {doc_hashing_algorithm}

""".format(**_FORMAT_DICTIONARY).format(**_FORMAT_DICTIONARY)

    arguments = docopt.docopt(documentation, version=ggv.version(), help=True)
    clean_arguments(arguments)


if __name__ == "__main__":
    pass
