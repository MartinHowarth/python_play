import os
from click.parser import split_arg_string
from click._bashcomplete import get_choices


from naval.main import cli


script_core_template = """
_complete_{cli_name}()
{{
    local cur_word prev_word

    cur_word=${{COMP_WORDS[COMP_CWORD]}}
    comp_words_trunc=("${{COMP_WORDS[@]::${{#COMP_WORDS[@]}}-1}}")

    {defns}

    if [[ 0 == 1 ]] ;
    then
        COMPREPLY=()
    {cases}
    else
        COMPREPLY=()
    fi
    
}}

complete -o nosort -F _complete_{cli_name} {cli_name}
"""

arr_def_template = """
    {name}=( {words_array} )"""


case_template = """
    elif [[ ${{{arr_name}[@]}} == ${{comp_words_trunc[@]}} ]] ;
    then
        COMPREPLY=($(compgen -W "{choices_sentence}" -- ${{cur_word}}))"""


def choices_for_command(_cli, command):
    cwords = split_arg_string(command)
    prog_name = cwords[0]
    cword = len(command)
    args = cwords[1:cword]
    try:
        incomplete = cwords[cword]
    except IndexError:
        incomplete = ''

    return [choice[0] for choice in get_choices(_cli, prog_name, args, incomplete)]


def add_choice_recursive(_cli, command, structure):
    choices = choices_for_command(cli, command)
    structure[command] = choices
    for choice in choices:
        add_choice_recursive(_cli, command + ' ' + choice, structure)


def render_choice(index, command, choices):
    words_array = ' '.join(['"%s"' % word for word in command.split()])
    choices_sentence = ' '.join(choices)
    name = "_%s" % index
    case = case_template.format(
        arr_name=name,
        choices_sentence=choices_sentence,
    )
    defin = arr_def_template.format(
        name=name,
        words_array=words_array,
    )
    return defin, case


def create_complete_script(cli_name, structure):
    defns = ""
    cases = ""
    ii = 0
    for command, choices in structure.items():
        de, ca = render_choice(ii, command, choices)
        defns += de
        cases += ca
        ii += 1
    return script_core_template.format(
        cases=cases,
        cli_name=cli_name,
        defns=defns,
    )


choices_for_command(cli, "naval")
choices_for_command(cli, "naval ship")

whole_structure = {}
index = 1
start_command = "naval"
add_choice_recursive(cli, start_command, whole_structure)
from pprint import pprint
pprint(whole_structure)

print(create_complete_script("naval", whole_structure))
