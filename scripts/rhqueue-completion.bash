#/usr/bin/env bash
_complete_functions() {
    local cur=${COMP_WORDS[-1]};
    if [ ${#COMP_WORDS[@]} -eq 2 ]; then
        COMPREPLY=($(compgen -W "queue remove info" "${COMP_WORDS[1]}"))
    elif ((${#COMP_WORDS[@]} >= 3)); then
        if [ "${cur:0:2}" == "--" ]; then
            COMPREPLY=($(compgen -W "--args --conda-venv --venv --source-script --priority --email --output-file --begin-time --servers --script-name" "${cur}"))
        elif [ "${cur:0:1}" == "-" ]; then
            COMPREPLY=($(compgen -W "-a -c -v -p -e -o -b -s" "${cur}"))
        elif [ "${COMP_WORDS[-2]}" == "-v" ]; then
            echo "the default is: ${RHQ_VENV}"
            COMPREPLY=($(compgen -W "$(ls $RHQ_VENV_LOCATIONS/)" "${cur}"))
        elif [ "${COMP_WORDS[-2]}" == "-c" ]; then
            COMPREPLY=($(compgen -W "$(ls $RHQ_CONDALOC/envs/)" "${cur}"))
        else
            COMPREPLY=($(compgen -f -X '!*.py' -- "${cur}") $(compgen -d -S "/" "${cur}"))
        fi
    fi
    
}
complete -F _complete_functions rhqueue